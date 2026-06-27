#!/usr/bin/env bash
#
# One-shot OpenClaw setup. Run this ON THE MACHINE you want the gateway to live on
# (your computer or a VPS) — NOT in a cloud sandbox, and NOT on the phone.
#
# It will:
#   1. install Python deps
#   2. make/patch .env (you supply your MOONSHOT key; it generates the gateway token)
#   3. start the harness with the OpenClaw gateway on port 18789
#   4. open a public tunnel (cloudflared quick-tunnel, else ngrok) -> wss:// URL
#   5. print the setup code to paste/scan in the OpenClaw app
#
# Usage:
#   MOONSHOT_API_KEY=sk-... bash scripts/setup_openclaw.sh
#   # or set MOONSHOT_API_KEY in your shell / .env first, then: bash scripts/setup_openclaw.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
PY="${PYTHON:-python3}"

echo "==> OpenClaw setup starting in $(pwd)"

# ── 1. deps ──────────────────────────────────────────────────────────────────
echo "==> Installing Python dependencies"
$PY -m pip install -q -r requirements.txt

# ── 2. .env ──────────────────────────────────────────────────────────────────
touch .env
ensure_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" .env 2>/dev/null; then
    return  # leave existing value alone
  fi
  echo "${key}=${val}" >> .env
  echo "   set ${key}"
}

# MOONSHOT key: from env if provided, else must already be in .env
if [ -n "${MOONSHOT_API_KEY:-}" ]; then
  if ! grep -q "^MOONSHOT_API_KEY=" .env; then
    echo "MOONSHOT_API_KEY=${MOONSHOT_API_KEY}" >> .env
    echo "   set MOONSHOT_API_KEY"
  fi
fi
if ! grep -q "^MOONSHOT_API_KEY=." .env; then
  echo "!! MOONSHOT_API_KEY is not set. Re-run as:  MOONSHOT_API_KEY=sk-... bash scripts/setup_openclaw.sh"
  exit 1
fi

GW_TOKEN="$($PY -c 'import secrets;print(secrets.token_urlsafe(32))')"
ensure_env OPENCLAW_GATEWAY_ENABLED true
ensure_env OPENCLAW_GATEWAY_HOST 127.0.0.1
ensure_env OPENCLAW_GATEWAY_PORT "$PORT"
ensure_env OPENCLAW_GATEWAY_TOKEN "$GW_TOKEN"
ensure_env BRAIN_PROVIDER moonshot
ensure_env BRAIN_MODEL kimi-k2.6

# ── 3. start the harness ─────────────────────────────────────────────────────
echo "==> Starting harness (logs: openclaw_run.log)"
$PY main.py > openclaw_run.log 2>&1 &
HARNESS_PID=$!
echo "   harness PID $HARNESS_PID"

# wait for the gateway to be listening
for i in $(seq 1 30); do
  if grep -q "gateway listening on ws" openclaw_run.log 2>/dev/null; then break; fi
  sleep 1
done
if ! grep -q "gateway listening on ws" openclaw_run.log 2>/dev/null; then
  echo "!! Gateway did not come up. Last log lines:"; tail -20 openclaw_run.log; exit 1
fi
echo "   gateway listening on ws://127.0.0.1:${PORT}"

# ── 4. tunnel ────────────────────────────────────────────────────────────────
PUBLIC_URL=""
if command -v cloudflared >/dev/null 2>&1; then
  echo "==> Opening Cloudflare quick tunnel (no account needed)"
  cloudflared tunnel --url "http://localhost:${PORT}" > cloudflared.log 2>&1 &
  TUNNEL_PID=$!
  for i in $(seq 1 30); do
    URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' cloudflared.log 2>/dev/null | head -1 || true)
    if [ -n "$URL" ]; then PUBLIC_URL="${URL/https:/wss:}"; break; fi
    sleep 1
  done
elif command -v ngrok >/dev/null 2>&1; then
  echo "==> Opening ngrok tunnel"
  ngrok http "$PORT" --log=stdout > ngrok.log 2>&1 &
  TUNNEL_PID=$!
  for i in $(seq 1 30); do
    URL=$(grep -oE 'https://[a-z0-9-]+\.ngrok[-a-z.]*\.app' ngrok.log 2>/dev/null | head -1 || true)
    if [ -n "$URL" ]; then PUBLIC_URL="${URL/https:/wss:}"; break; fi
    sleep 1
  done
else
  echo "!! No tunnel tool found (cloudflared or ngrok)."
  echo "   Install one:  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  echo "   Then re-run, OR connect over LAN: set OPENCLAW_GATEWAY_HOST=0.0.0.0 and use ws://<this-machine-LAN-IP>:${PORT}"
fi

# ── 5. pairing code ──────────────────────────────────────────────────────────
echo
echo "================================================================"
if [ -n "$PUBLIC_URL" ]; then
  echo "Public gateway URL:  $PUBLIC_URL"
  echo
  $PY scripts/openclaw_pair.py --url "$PUBLIC_URL" --ttl 1800
else
  echo "No tunnel URL. For LAN use, set OPENCLAW_GATEWAY_HOST=0.0.0.0, restart, and run:"
  echo "  python scripts/openclaw_pair.py --url ws://<your-LAN-IP>:${PORT}"
fi
echo "================================================================"
echo
echo "In the OpenClaw app: choose 'connect via code', scan/paste the code above."
echo "DELETE the default 'Home Gateway -> 127.0.0.1' entry — that one can never work."
echo
echo "Harness PID: $HARNESS_PID   (stop with: kill $HARNESS_PID)"
[ -n "${TUNNEL_PID:-}" ] && echo "Tunnel PID:  $TUNNEL_PID   (stop with: kill $TUNNEL_PID)"
echo "Live logs:   tail -f openclaw_run.log"
