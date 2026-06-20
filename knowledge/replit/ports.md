# Replit Ports Configuration

> Source: https://docs.replit.com/replit-workspace/ports
> Blog: https://blog.replit.com/ports
> Last updated: 2026-06

## Overview

Replit uses a sophisticated port system to route traffic from the public internet to your app running inside a Repl. Understanding ports is essential for running web servers, APIs, and multi-service apps.

## How Port Routing Works

```
Internet Request
     ↓
Replit Proxy (HTTPS)
     ↓
VM Network Layer
     ↓
Port Authority (local proxy)
     ↓
Your App (listening on local port)
```

Replit's proxy intercepts incoming requests and routes them to the correct service inside your Repl, even if the service listens on localhost.

## Default Port Behavior

### Port 80 — Default HTTP

Port **80** is the "default port" for HTTP traffic:
- HTTP traffic sent to the root domain automatically routes to port 80
- This is the port shown in the Webview by default
- Configure your server to listen on port 8080 and map it to external port 80

### Standard Port Conventions

| App Type | Common Internal Port | External Port |
|----------|---------------------|---------------|
| HTTP servers | 8080 | 80 |
| Node.js | 3000 | 80 |
| Flask | 5000 | 80 |
| FastAPI | 8000 | 80 |
| React dev | 3000 | 80 |
| Vite | 5173 | 80 |

## Port Configuration in `.replit`

Port mappings are stored in the `.replit` file and persist across sessions:

```toml
[[ports]]
localPort = 8080
externalPort = 80
description = "Main web server"

[[ports]]
localPort = 3001
externalPort = 3001
description = "API server"

[[ports]]
localPort = 5432
externalPort = 5432
description = "PostgreSQL database"
```

### Fields

| Field | Description | Required |
|-------|-------------|----------|
| `localPort` | Port your app binds to internally | Yes |
| `externalPort` | Port exposed externally | Yes |
| `description` | Human-readable description | No |

## Binding to the Correct Interface

**Critical for Replit**: Your server must bind to `0.0.0.0`, not `127.0.0.1` or `localhost`:

### Python Flask

```python
from flask import Flask
app = Flask(__name__)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',   # Required for Replit
        port=8080,
        debug=True
    )
```

### Python FastAPI

```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
```

### Node.js Express

```javascript
const express = require('express');
const app = express();

app.listen(8080, '0.0.0.0', () => {
  console.log('Server running on port 8080');
});

// Or without specifying host (works in most cases):
app.listen(8080);
```

### Node.js with process.env.PORT

```javascript
const PORT = process.env.PORT || 8080;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

## Multiple Ports / Multiple Services

Run multiple services in the same Repl:

### Using process management

```python
# run.py - Start multiple services
import subprocess
import sys

services = [
    ['python', 'api.py'],       # Runs on 8080
    ['python', 'admin.py'],     # Runs on 3001
    ['redis-server', '--port', '6379'],  # Redis
]

processes = []
for service in services:
    p = subprocess.Popen(service)
    processes.append(p)

# Wait for all processes
for p in processes:
    p.wait()
```

### Switching Between Ports in Webview

When multiple ports are active:
1. Look at the Webview URL bar
2. Click the domain name
3. A dropdown appears showing available ports
4. Select which port to preview

Or use the **Networking tool** (gear icon in Webview) for detailed port management.

## Viewing Active Ports

The Networking panel (accessible via the gear icon in Webview or Tools menu) shows:
- All currently listening ports
- Port mapping (local → external)
- Port descriptions
- Quick links to open each port

## Port Availability

### Reserved/Special Ports

Some ports have special behavior:
- **Port 80**: Default HTTP, maps to root domain
- **Port 443**: HTTPS (handled by Replit proxy automatically)
- **Port 22**: SSH (if SSH access is enabled)

### Available Port Range

Typical application ports work fine:
- 1024-65535 for non-privileged ports
- Common: 3000, 3001, 5000, 8000, 8080, 8888

## External Port Access

Ports are accessible at:
- **Port 80**: `https://your-app.replit.app` (or dev URL)
- **Other ports**: `https://your-app.replit.app:PORT`

Example with port 3001:
```
https://myapp.username.repl.co:3001
```

## WebSocket Ports

WebSockets also work through Replit's port system:

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ 
  port: 8080,
  host: '0.0.0.0'
});
```

Client connects:
```javascript
const ws = new WebSocket('wss://your-app.replit.app');
// Note: wss:// (secure WebSocket) even on port 80
```

## Debugging Port Issues

### Port Not Accessible

1. Verify your server is binding to `0.0.0.0`, not `localhost`
2. Check the port is listed in `.replit` `[[ports]]` section
3. Ensure the server is actually running (check Console output)
4. Look at the Networking panel for active ports

### Wrong Port in Webview

1. Click the URL in Webview
2. Select the correct port from the dropdown
3. Or manually navigate to `your-dev-url:PORT`

### Port Already in Use

```bash
# Find what's using a port
lsof -i :8080

# Kill the process
kill -9 <PID>
```

## Deployment Ports

When deploying, Replit handles port routing automatically:
- Set your server to listen on the configured port (e.g., 8080)
- Map port 8080 → 80 in `.replit` deployment configuration
- Replit routes HTTPS traffic to your app

For health checks:
- Your app must respond on port 80 (or whatever maps to external 80)
- Response must come within 5 seconds
- HTTP 200 response expected on root path `/`
