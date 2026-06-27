#!/usr/bin/env python3
"""
Generate an OpenClaw setup code (and QR) for the "connect via code" flow.

The code is base64(JSON {url, bootstrapToken}) where bootstrapToken is a
short-lived credential signed with your OPENCLAW_GATEWAY_TOKEN. Your running
gateway validates it statelessly — no shared file needed.

Run this on the machine that runs the harness (it reads OPENCLAW_GATEWAY_TOKEN
from your .env).

Usage:
    # Tunnel (recommended): pass the public wss:// URL your phone will reach
    python scripts/openclaw_pair.py --url wss://ab12cd34.ngrok-free.app

    # LAN: pass your computer's LAN IP
    python scripts/openclaw_pair.py --url ws://192.168.1.50:18789

    # Custom lifetime (default 15 min)
    python scripts/openclaw_pair.py --url wss://... --ttl 1800

Then in the OpenClaw app choose "connect via code" and scan the QR or paste the
setup code. The code expires after --ttl seconds; just re-run for a fresh one.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from harness.gateways.openclaw import mint_bootstrap_token, make_setup_code


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an OpenClaw setup code")
    parser.add_argument(
        "--url",
        help="The gateway URL the PHONE will connect to (wss://<tunnel> or ws://<lan-ip>:18789). "
             "If omitted, falls back to ws://<host>:<port> from your config (loopback — usually NOT reachable by a phone).",
    )
    parser.add_argument("--ttl", type=int, default=900, help="Code lifetime in seconds (default 900 = 15 min)")
    args = parser.parse_args()

    secret = settings.OPENCLAW_GATEWAY_TOKEN
    if not secret:
        print("ERROR: OPENCLAW_GATEWAY_TOKEN is not set in your .env.")
        print("Set it (python -c \"import secrets; print(secrets.token_urlsafe(32))\"), then re-run.")
        sys.exit(1)

    url = args.url
    if not url:
        host = settings.OPENCLAW_GATEWAY_HOST
        if host == "0.0.0.0":
            host = "127.0.0.1"
        url = f"ws://{host}:{settings.OPENCLAW_GATEWAY_PORT}"
        print("WARNING: no --url given; using", url)
        print("         A phone almost certainly cannot reach that. Pass --url with your tunnel/LAN URL.\n")

    boot = mint_bootstrap_token(secret, ttl_seconds=args.ttl)
    code = make_setup_code(url, boot)

    print("=" * 60)
    print("OpenClaw setup code")
    print("=" * 60)
    print(f"URL embedded:  {url}")
    print(f"Expires in:    {args.ttl}s")
    print()
    print("Setup code (paste into the app's 'connect via code'):")
    print()
    print(code)
    print()

    # Optional QR rendering
    try:
        import qrcode  # type: ignore
        qr = qrcode.QRCode(border=1)
        qr.add_data(code)
        qr.make(fit=True)
        print("Or scan this QR:\n")
        qr.print_ascii(invert=True)
    except ImportError:
        print("(Install `qrcode` for a scannable QR:  pip install qrcode)")
    print()
    print("Code expires — re-run this script for a fresh one if it times out.")


if __name__ == "__main__":
    main()
