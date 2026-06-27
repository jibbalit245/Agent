"""
OpenClaw-compatible gateway.

Implements the OpenClaw Gateway WebSocket protocol so the OpenClaw mobile app
(and CLI / web clients) can connect to this harness and chat with its agents —
the same swarm, council, knowledge-graph, and tool stack exposed everywhere else.

Protocol (text frames, JSON):
  1. Client opens WS. Gateway sends a pre-connect challenge:
       {"type":"event","event":"connect.challenge","payload":{"nonce","ts"}}
  2. Client's FIRST frame must be a connect request:
       {"type":"req","id","method":"connect","params":{minProtocol,maxProtocol,
        client,role,scopes,auth:{token|password},device,...}}
  3. Gateway validates auth and replies:
       {"type":"res","id","ok":true,"payload":{"type":"hello-ok","protocol":4,
        "server":{...},"features":{...},"auth":{role,scopes,deviceToken},"policy":{...}}}
  4. Operator chat:
       req  chat.send {sessionKey?, text, idempotencyKey?}
       res  {ok:true, payload:{status:"accepted", messageId}}        (immediate ack)
       event chat {sessionKey, messageId, role:"assistant", message, deltaText}  (reply)
       event agent {sessionKey, messageId, status:"ok"}              (run complete)

Auth: shared-token mode (auth.token == configured gateway token). If no token is
configured, loopback connections are allowed unauthenticated (dev only).

This implements the documented protocol; device pairing/signing is accepted but
not cryptographically enforced in shared-token mode. The chat path — connect and
talk to your agents from the app — is the focus.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PROTOCOL_MIN = 3
_PROTOCOL_MAX = 4

# Methods this gateway advertises in hello-ok.features.methods
_FEATURE_METHODS = ["connect", "chat.send", "ping", "sessions.list"]
_FEATURE_EVENTS = ["connect.challenge", "chat", "agent", "tick", "heartbeat"]


# ── Pairing / setup-code helpers ──────────────────────────────────────────────
# A setup code is base64(JSON {url, bootstrapToken}). The bootstrap token is a
# short-lived HMAC credential signed with the gateway secret, so the running
# gateway can validate codes it didn't store (stateless across processes).

def mint_bootstrap_token(secret: str, ttl_seconds: int = 900) -> str:
    """Create a short-lived single-device bootstrap token signed with the gateway secret."""
    exp = int(time.time()) + ttl_seconds
    nonce = secrets.token_hex(8)
    payload = f"{exp}.{nonce}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    raw = f"{payload}.{sig}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def verify_bootstrap_token(secret: str, token: str) -> bool:
    """Validate a bootstrap token's signature and expiry against the gateway secret."""
    if not secret or not token:
        return False
    try:
        pad = "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token + pad).decode()
        exp_s, nonce, sig = raw.split(".")
        payload = f"{exp_s}.{nonce}"
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(sig, expected):
            return False
        return int(exp_s) >= int(time.time())
    except Exception:
        return False


def make_setup_code(url: str, bootstrap_token: str) -> str:
    """Build the base64 setup code the OpenClaw app scans/pastes."""
    payload = {"url": url, "bootstrapToken": bootstrap_token}
    return base64.b64encode(json.dumps(payload).encode()).decode()


class OpenClawGateway:
    """A WebSocket server speaking the OpenClaw gateway protocol, backed by AgentManager."""

    def __init__(
        self,
        agent_manager: Any,
        token: str = "",
        host: str = "0.0.0.0",
        port: int = 18789,
        memory_dir: Path = Path("./memory"),
        server_version: str = "agent-harness/1.0",
    ) -> None:
        self.manager = agent_manager
        self.token = token
        self.host = host
        self.port = port
        self.memory_dir = memory_dir
        self.server_version = server_version

    # ── auth ────────────────────────────────────────────────────────────────

    def _check_auth(self, params: dict, remote: str) -> tuple[bool, str]:
        """
        Validate the connect request's auth. Returns (ok, reason).

        Accepts three credential forms:
          - shared token: auth.token / auth.password == gateway token
          - setup-code pairing: auth.bootstrapToken (short-lived, HMAC-signed)
          - bootstrap token supplied in auth.token (some clients reuse that field)
        """
        auth = params.get("auth") or {}
        if not self.token:
            # No token configured: only allow loopback (dev convenience).
            if remote.startswith("127.") or remote == "::1" or remote.startswith("localhost"):
                return True, ""
            return False, "gateway token not configured; remote connections require a token"

        supplied = str(auth.get("token") or auth.get("password") or "")
        boot = str(auth.get("bootstrapToken") or "")

        if supplied and secrets.compare_digest(supplied, str(self.token)):
            return True, ""
        if boot and verify_bootstrap_token(self.token, boot):
            return True, ""
        # Some clients carry the pairing code's token in auth.token
        if supplied and verify_bootstrap_token(self.token, supplied):
            return True, ""
        return False, "invalid auth token or expired pairing code"

    # ── frame helpers ────────────────────────────────────────────────────────

    @staticmethod
    async def _send(ws, frame: dict) -> None:
        await ws.send(json.dumps(frame))

    async def _res_ok(self, ws, req_id: str, payload: dict) -> None:
        await self._send(ws, {"type": "res", "id": req_id, "ok": True, "payload": payload})

    async def _res_err(self, ws, req_id: str, code: str, message: str) -> None:
        await self._send(ws, {
            "type": "res", "id": req_id, "ok": False,
            "error": {"code": code, "message": message},
        })

    async def _event(self, ws, event: str, payload: dict) -> None:
        await self._send(ws, {"type": "event", "event": event, "payload": payload})

    # ── per-connection lifecycle ───────────────────────────────────────────────

    async def _handle(self, ws) -> None:
        remote = ""
        try:
            peer = getattr(ws, "remote_address", None)
            if peer:
                remote = str(peer[0])
        except Exception:
            pass

        conn_id = secrets.token_hex(8)
        logger.info("OpenClaw: connection %s from %s", conn_id, remote or "?")

        # 1. Pre-connect challenge
        nonce = secrets.token_hex(16)
        await self._event(ws, "connect.challenge", {"nonce": nonce, "ts": int(time.time() * 1000)})

        # 2. First frame must be a connect request
        try:
            first_raw = await asyncio.wait_for(ws.recv(), timeout=30)
        except asyncio.TimeoutError:
            logger.info("OpenClaw: %s handshake timeout", conn_id)
            return
        try:
            first = json.loads(first_raw)
        except (json.JSONDecodeError, TypeError):
            await self._send(ws, {"type": "res", "id": None, "ok": False,
                                  "error": {"code": "bad_frame", "message": "first frame must be JSON connect"}})
            return

        if first.get("type") != "req" or first.get("method") != "connect":
            await self._res_err(ws, first.get("id"), "expected_connect", "first frame must be a connect request")
            return

        params = first.get("params") or {}
        req_id = first.get("id")

        # protocol negotiation
        client_min = int(params.get("minProtocol", _PROTOCOL_MIN))
        client_max = int(params.get("maxProtocol", _PROTOCOL_MAX))
        negotiated = min(_PROTOCOL_MAX, client_max)
        if negotiated < max(_PROTOCOL_MIN, client_min):
            await self._res_err(ws, req_id, "protocol_mismatch",
                                f"server supports {_PROTOCOL_MIN}-{_PROTOCOL_MAX}, client {client_min}-{client_max}")
            return

        # auth
        ok, reason = self._check_auth(params, remote)
        if not ok:
            await self._res_err(ws, req_id, "unauthorized", reason)
            logger.info("OpenClaw: %s rejected (%s)", conn_id, reason)
            return

        role = params.get("role", "operator")
        client = params.get("client") or {}
        scopes = params.get("scopes") or (["operator.read", "operator.write"] if role == "operator" else [])
        device_token = secrets.token_urlsafe(24)

        # 3. hello-ok
        await self._res_ok(ws, req_id, {
            "type": "hello-ok",
            "protocol": negotiated,
            "server": {"version": self.server_version, "connId": conn_id},
            "features": {"methods": _FEATURE_METHODS, "events": _FEATURE_EVENTS},
            "snapshot": {"sessions": [], "presence": [], "stateVersion": 1, "uptimeMs": 0},
            "auth": {"role": role, "scopes": scopes, "deviceToken": device_token},
            "policy": {"maxPayload": 26214400, "maxBufferedBytes": 52428800, "tickIntervalMs": 15000},
        })
        logger.info("OpenClaw: %s connected (role=%s, client=%s, proto=%d)",
                    conn_id, role, client.get("id", "?"), negotiated)

        # session id for AgentManager — stable per connection/client
        base_uid = f"openclaw_{client.get('id') or conn_id}"
        try:
            from harness.tools.memory_tools import set_session_context
            set_session_context(base_uid, self.memory_dir)
        except Exception:
            pass

        # heartbeat task
        hb = asyncio.create_task(self._heartbeat(ws))
        try:
            async for raw in ws:
                try:
                    frame = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue
                await self._dispatch(ws, frame, base_uid)
        except Exception as exc:
            logger.info("OpenClaw: %s closed (%s)", conn_id, exc)
        finally:
            hb.cancel()

    async def _heartbeat(self, ws) -> None:
        try:
            while True:
                await asyncio.sleep(15)
                await self._event(ws, "tick", {"ts": int(time.time() * 1000)})
        except (asyncio.CancelledError, Exception):
            return

    # ── method dispatch ─────────────────────────────────────────────────────────

    async def _dispatch(self, ws, frame: dict, base_uid: str) -> None:
        if frame.get("type") != "req":
            return  # ignore res/event from client for now
        method = frame.get("method", "")
        req_id = frame.get("id")
        params = frame.get("params") or {}

        if method == "ping":
            await self._res_ok(ws, req_id, {"pong": True, "ts": int(time.time() * 1000)})
            return

        if method == "sessions.list":
            await self._res_ok(ws, req_id, {"sessions": []})
            return

        if method == "chat.send":
            await self._handle_chat(ws, req_id, params, base_uid)
            return

        if method == "node.invoke":
            # We are an operator-facing gateway; we don't host node capabilities.
            await self._res_err(ws, req_id, "unsupported", "this gateway does not host node capabilities")
            return

        # Unknown method — be permissive: ack so clients don't stall.
        await self._res_ok(ws, req_id, {"ignored": method})

    async def _handle_chat(self, ws, req_id: str, params: dict, base_uid: str) -> None:
        text = (params.get("text") or "").strip()
        session_key = params.get("sessionKey") or "default"
        message_id = secrets.token_hex(8)

        if not text:
            await self._res_err(ws, req_id, "empty", "no text in chat.send")
            return

        # Per-session uid so different app sessions keep separate histories
        uid = f"{base_uid}:{session_key}"

        # 1. Immediate accepted ack
        await self._res_ok(ws, req_id, {"status": "accepted", "messageId": message_id, "sessionKey": session_key})

        # 2. Run the agent
        try:
            result = await self.manager.chat(uid, text)
            reply = result.text or "(no response)"
            status = "ok"
        except Exception as exc:
            logger.error("OpenClaw chat failed for %s: %s", uid, exc, exc_info=True)
            reply = f"Error: {type(exc).__name__}: {exc}"
            status = "error"

        # 3. Emit the assistant message as a chat event
        await self._event(ws, "chat", {
            "sessionKey": session_key,
            "messageId": message_id,
            "role": "assistant",
            "deltaText": reply,
            "message": reply,
        })

        # 4. Final run-completion event
        await self._event(ws, "agent", {
            "sessionKey": session_key,
            "messageId": message_id,
            "status": status,
        })

    # ── server ──────────────────────────────────────────────────────────────────

    async def serve(self) -> None:
        """Run the WebSocket server forever."""
        import websockets
        logger.info("OpenClaw gateway listening on ws://%s:%d", self.host, self.port)
        if not self.token:
            logger.warning("OpenClaw gateway has NO token set — only loopback connections allowed. "
                           "Set OPENCLAW_GATEWAY_TOKEN for remote (phone) access.")
        async with websockets.serve(self._handle, self.host, self.port, max_size=26214400):
            await asyncio.Future()  # run forever

    def run_in_thread(self) -> None:
        """Start the gateway in a background daemon thread with its own event loop."""
        import threading

        def _run() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.serve())
            except Exception as exc:
                logger.error("OpenClaw gateway crashed: %s", exc, exc_info=True)

        t = threading.Thread(target=_run, daemon=True, name="openclaw-gateway")
        t.start()
        logger.info("OpenClaw gateway thread started")
