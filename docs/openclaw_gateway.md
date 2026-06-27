# Connecting the OpenClaw phone app to this harness

The harness ships an OpenClaw-compatible gateway (`harness/gateways/openclaw.py`).
Turn it on, expose it with a tunnel, and point the OpenClaw app at it. You'll be
chatting with your agents — swarm, council, knowledge graph and all — from your phone.

## 1. Enable the gateway

In your `.env` (on the machine that runs the harness):

```
OPENCLAW_GATEWAY_ENABLED=true
OPENCLAW_GATEWAY_HOST=127.0.0.1        # 127.0.0.1 is fine when using a tunnel
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_GATEWAY_TOKEN=<a long random secret>
```

Generate a strong token:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

The token is the only thing protecting the gateway once it's on a public tunnel —
make it long and don't paste it anywhere public.

Then start the harness as usual:

```bash
python main.py
```

You'll see: `OpenClaw gateway listening on ws://127.0.0.1:18789`.
It runs alongside Telegram (Telegram foreground, gateway in a background thread).
If you don't set a Telegram token, the gateway becomes the primary interface.

## 2. Expose it with a tunnel

The gateway speaks plain `ws://` locally; the tunnel adds the `wss://` TLS the app needs.

### Option A — ngrok

```bash
ngrok http 18789
```

ngrok prints a forwarding URL like `https://ab12cd34.ngrok-free.app`.
Your gateway URL for the app is the same host with the `wss://` scheme:

```
wss://ab12cd34.ngrok-free.app
```

(No `:18789` — the tunnel maps 443 → your local 18789.)

> The free ngrok URL changes every restart. Reserve a static domain (ngrok dashboard)
> if you don't want to re-enter the URL each time.

### Option B — localtonet

localtonet publishes a one-stop OpenClaw self-host guide and gives you a stable
`wss://` endpoint. Create a TCP/HTTP tunnel to local port `18789`, then use the
`wss://<your-subdomain>` URL it gives you.

## 3. Connect from the app

In the OpenClaw app:

1. Add a gateway / server.
2. **URL:** the `wss://…` tunnel URL from step 2.
3. **Token:** your `OPENCLAW_GATEWAY_TOKEN`.
4. Connect — you should see **Connected**.

Send a message; it routes to the harness's active agent and the reply streams back.
Switch agents, run `/swarm`-style work, etc. — same agents as every other gateway.

## 4. Pick the agent the app talks to

Each app session maps to an AgentManager session keyed by the app's client +
`sessionKey`. The default agent is the harness default (researcher). To make the
phone default to, say, the swarm architect, set it as the default agent or switch
in-session the same way you would elsewhere.

## Troubleshooting

- **"token not configured; remote connections require a token"** — you enabled the
  gateway without `OPENCLAW_GATEWAY_TOKEN`. With no token, only loopback connects;
  a tunnel is remote, so set a token.
- **App can't connect** — confirm `python main.py` shows the listening line, the
  tunnel is up, and you used `wss://` (not `https://`/`ws://`) with no port suffix.
- **Connects then drops** — check the harness logs for the `OpenClaw:` lines; a
  handshake rejection logs the reason (bad token, protocol mismatch).
- **Protocol/pairing edge cases** — this gateway implements the documented shared-token
  chat protocol. If the app expects a handshake detail we don't emit yet, grab the
  app's error and the harness log and it can be tightened.

## Security notes

- A public tunnel exposes the gateway to the internet; the token is your only gate.
  Rotate it if it leaks.
- Prefer a tunnel provider that lets you restrict access, and stop the tunnel when
  you're not using it.
- `OPENCLAW_GATEWAY_HOST=127.0.0.1` keeps the raw port off your LAN — the tunnel is
  the only way in.
