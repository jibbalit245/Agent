# Replit Reserved VM Deployments

> Source: https://docs.replit.com/deployments/reserved-vm-deployments
> Updated URL: https://docs.replit.com/cloud-services/deployments/reserved-vm-deployments
> Last updated: 2026-06

## What are Reserved VM Deployments?

Reserved VM Deployments provide **dedicated compute resources** that run continuously (24/7). Unlike Autoscale deployments that scale to zero, a Reserved VM always has a running instance, ensuring no cold starts and consistent availability.

## Key Features

- **Always-on**: No cold starts; your app is always running
- **Dedicated resources**: CPU and memory reserved exclusively for your app
- **Predictable pricing**: Fixed monthly cost regardless of traffic
- **Best performance**: No resource sharing with other tenants
- **Full control**: Run any long-lived process, background jobs, etc.

## Use Cases

Best suited for:
- Production web applications with steady traffic
- Applications requiring constant uptime
- Services with WebSocket connections that must stay alive
- Heavy computation applications
- Applications that cannot tolerate cold start latency
- Database connections that need to stay warm

## How to Deploy

1. Open your Replit App
2. Click **Deploy**
3. Select **Reserved VM** deployment type
4. Configure:
   - Machine size (see table below)
   - Run command
   - Deployment secrets
5. Click **Deploy**

## Machine Sizes and Pricing

| Size | vCPUs | RAM | Price/month (approx.) |
|------|-------|-----|-----------------------|
| Shared CPU | 0.5 vCPU | 512 MB | ~$5-7/month |
| Standard | 1 vCPU | 1 GB | ~$10/month |
| Standard 2x | 2 vCPUs | 2 GB | ~$20/month |
| Performance | 4 vCPUs | 4 GB | ~$40/month |

*Pricing is approximate. Check the Replit dashboard for current exact pricing.*

Reserved VMs start at approximately **$20/month** for standard configurations.

## Pricing Details

- **Fixed monthly cost**: You pay the same regardless of traffic
- Billed from the moment you deploy
- Stop/delete deployment to stop billing
- Core plan includes **$25/month in credits** that can offset costs

## Comparison with Autoscale

| Feature | Reserved VM | Autoscale |
|---------|-------------|-----------|
| Availability | Always on | On-demand (scale to zero) |
| Cold starts | None | Possible when idle |
| Cost model | Fixed monthly | Pay-per-use |
| Predictability | High | Variable |
| Min monthly cost | ~$20 | ~$1 base + usage |
| Best for | Production, steady traffic | Variable traffic, cost optimization |

## Configuration

### Run Command
Set the command that keeps your app running:
```toml
# In .replit
[deployment]
run = ["python", "main.py"]
# or
run = ["node", "server.js"]
```

### Deployment Secrets
Add production secrets separately from workspace secrets:
1. Deployments tab → Secrets
2. Add each production key-value pair

### Health Checks
Your app must:
- Bind to `0.0.0.0` (not `127.0.0.1` or `localhost`)
- Listen on port 8080 (or configured port)
- Respond to HTTP GET on root path within 5 seconds

Example (Node.js):
```javascript
const express = require('express');
const app = express();
// Must use 0.0.0.0 for Replit deployments
app.listen(8080, '0.0.0.0', () => {
  console.log('Server running on port 8080');
});
```

Example (Python Flask):
```python
from flask import Flask
app = Flask(__name__)

if __name__ == '__main__':
    # Must bind to 0.0.0.0
    app.run(host='0.0.0.0', port=8080)
```

## Custom Domains

Same as other deployment types:
1. Deployments → Settings → Link a domain
2. Enter domain
3. Add DNS records at registrar
4. Automatic TLS provisioning

## Monitoring

- View real-time logs in the Deployments panel
- Monitor CPU and memory usage
- Set up alerts for downtime

## When NOT to Use Reserved VM

Consider Autoscale if:
- Traffic is highly variable or low
- You want to minimize costs
- Brief cold starts are acceptable

Consider Static if:
- Your app is pure HTML/CSS/JS
- No server-side processing needed

## SSH Access

Replit supports SSH access to your deployed environment for debugging and management.
