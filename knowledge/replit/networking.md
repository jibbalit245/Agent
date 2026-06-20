# Replit Networking

> Source: https://docs.replit.com/replit-workspace/networking-on-replit
> Last updated: 2026-06

## Overview

Replit runs your apps in cloud virtual machines with a sophisticated networking layer that handles:
- Routing public HTTP/HTTPS traffic to your running app
- Port management and mapping
- WebSocket connections
- Domain assignments and custom domains

## How Traffic Flows

```
Internet → Replit Proxy → Port Authority → Your App (local port)
```

1. HTTP/HTTPS request arrives at Replit's proxy
2. Proxy routes request to the specific VM running your Repl
3. A local proxy (Port Authority) looks up the destination Repl
4. Request is forwarded to the server running inside the Repl
5. Even if your server listens only on `localhost`, Replit routes to it

## URLs

### Development (Workspace)

When you click **Run**, your app gets a temporary URL:
```
https://<repl-slug>.<username>.repl.co
```

Or newer format:
```
https://<random-id>.replit.dev
```

This URL is only active while your workspace is open and the app is running.

### Deployed Apps

When you deploy, your app gets a permanent URL:
```
https://<app-name>.replit.app
```

This persists even when you close your workspace.

## Port Configuration

### Default Behavior

- Your app listens on a local port (e.g., 8080, 3000, 5000)
- Replit maps port **80** to your app's default URL
- Other ports get mapped to `yourdomain:PORT`

### Important: Binding to 0.0.0.0

For your app to be accessible in Replit (especially for deployment):

```python
# Python Flask
app.run(host='0.0.0.0', port=8080)  # Correct
app.run(host='localhost', port=8080)  # Won't work for external access
```

```javascript
// Node.js Express
app.listen(8080, '0.0.0.0')  // Correct
app.listen(8080)  // Works in dev, may not in deployment
```

### Port Mapping in `.replit`

```toml
# Map internal port to external port
[[ports]]
localPort = 8080
externalPort = 80       # Default HTTP (root URL)
description = "Web server"

[[ports]]
localPort = 3001
externalPort = 3001     # Accessible at yourdomain:3001
description = "API server"

[[ports]]
localPort = 5432
externalPort = 5432     # Database port
description = "PostgreSQL"
```

### External Port Numbers

- **Port 80**: Default HTTP — maps to the root domain URL
- **Other ports**: Accessible at `yourdomain.replit.app:PORT`

## Multiple Ports

Your Repl can run multiple services on different ports simultaneously:

```python
# In Python, run multiple services
import threading
from flask import Flask

api = Flask('api')
admin = Flask('admin')

@api.route('/')
def api_root():
    return {"service": "api"}

@admin.route('/')
def admin_root():
    return {"service": "admin"}

# Run on different ports
def run_api():
    api.run(host='0.0.0.0', port=8080)

def run_admin():
    admin.run(host='0.0.0.0', port=3001)

threading.Thread(target=run_api).start()
threading.Thread(target=run_admin).start()
```

**Switching ports in Webview:**
1. Click the URL/domain in the Webview pane
2. Select which port to preview
3. Or use the networking tool (gear icon) for full port management

## WebSockets

WebSockets work on Replit:

```javascript
// Node.js WebSocket server
const WebSocket = require('ws');

const wss = new WebSocket.Server({ 
  port: 8080, 
  host: '0.0.0.0'  // Important for Replit
});

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    console.log('Received:', message.toString());
    ws.send(`Echo: ${message}`);
  });
  ws.send('Connected!');
});
```

```javascript
// Client connection to deployed app
const ws = new WebSocket('wss://your-app.replit.app');
ws.onmessage = (event) => console.log(event.data);
```

## HTTPS/TLS

- Replit automatically handles **TLS/HTTPS** for all public URLs
- Your app doesn't need to manage SSL certificates
- All traffic is encrypted in transit
- Custom domains also get automatic TLS provisioning

## Inbound Networking

Your app can receive:
- HTTP/HTTPS requests (ports 80/443 → your app port)
- WebSocket connections (WSS)
- Custom port traffic (mapped ports)

## Outbound Networking

Your app can make outbound connections to:
- External APIs (HTTP/HTTPS)
- Databases (PostgreSQL, Redis, etc.)
- Other web services

### Outbound HTTP Example

```python
import requests

response = requests.get('https://api.github.com/repos/replit/upm')
print(response.json())
```

## Firewalled Replit

Some organizations use **Firewalled Replit** (for enterprise/education), which restricts:
- Outbound connections to whitelisted domains only
- Access to specific external services
- Traffic to/from the internet

In firewalled environments, contact your administrator for the allowed domains list.

## Environment Variables for Networking

Replit provides networking-related environment variables:

```python
import os

# Get the current Repl's URL
repl_id = os.environ.get('REPL_ID')
repl_slug = os.environ.get('REPL_SLUG')
repl_owner = os.environ.get('REPL_OWNER')

# Construct URL
dev_url = f"https://{repl_id}.id.repl.co"
```

## Proxy Headers

When requests come through Replit's proxy, they include headers:
- `X-Forwarded-For`: Client's real IP address
- `X-Forwarded-Proto`: Original protocol (http/https)
- `X-Replit-User-Id`: Authenticated user's ID (if using Replit Auth)
- `X-Replit-User-Name`: Authenticated user's name
- `X-Replit-User-Roles`: User's roles

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    real_ip = request.headers.get('X-Forwarded-For')
    user_id = request.headers.get('X-Replit-User-Id')
    return f"Your IP: {real_ip}, User: {user_id}"
```

## Rate Limits and Restrictions

- No specific published rate limits for outbound requests
- Standard fair-use policies apply
- For high-traffic production apps, consider the appropriate deployment tier

## SSH Access

Replit supports SSH access to Repls:
- Available on paid plans
- Useful for debugging and remote development
- Connect using standard SSH client
