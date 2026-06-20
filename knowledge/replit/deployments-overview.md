# Replit Deployments Overview

> Source: https://docs.replit.com/deployments/about-deployments (403 Forbidden — content compiled from search results)
> Updated URL: https://docs.replit.com/cloud-services/deployments/
> Last updated: 2026-06

## What are Replit Deployments?

Replit Deployments allow you to publish your Replit App to the internet so it runs independently of your development workspace. Deployed apps run on Replit's cloud infrastructure and are publicly accessible via a `.replit.app` URL or a custom domain.

**Key distinction**: The development workspace (clicking Run) and the deployed app are separate environments. Each has its own secrets, environment variables, and runtime.

## Deployment Types

### 1. Autoscale Deployments
- Scales up with demand, scales to zero when idle
- Pay only for compute used (Compute Units)
- Best for: Web apps, APIs with variable traffic
- URL: `appname.replit.app`

### 2. Reserved VM Deployments
- Dedicated compute resources running 24/7
- Fixed monthly cost, predictable pricing
- Best for: Production apps with steady traffic, always-on services
- Starts at ~$20/month

### 3. Static Deployments
- Serve HTML, CSS, JavaScript files via CDN
- Automatic caching and TLS certificates
- Pay only for data transfer
- Best for: Websites, SPAs, documentation sites

### 4. Scheduled Deployments
- Run tasks on a schedule (cron jobs)
- Define schedule in natural language or cron expression
- Timeout: 11 hours maximum
- Minimum interval: 1 minute

### 5. Background Worker Deployments
- Long-running processes without HTTP endpoints
- Runs continuously
- Best for: Queue processors, data pipelines, bots

## How to Deploy

1. Open your Replit App
2. Click the **Deploy** button (or go to the Deployments tab)
3. Choose deployment type
4. Configure:
   - Build command (if applicable)
   - Run command
   - Environment variables / Secrets
   - Machine size
5. Click **Deploy**

Your app will be assigned a `.replit.app` URL automatically.

## Deployment vs. Workspace

| Feature | Workspace (Run) | Deployment |
|---------|----------------|------------|
| URL | Temporary `*.replit.dev` | Permanent `*.replit.app` |
| Secrets | Workspace secrets | Deployment secrets (separate) |
| Scaling | Single instance | Autoscales (Autoscale type) |
| Cost | Included in plan | Usage-based or fixed |
| Uptime | While workspace open | 24/7 (or on-demand) |

## Secrets in Deployments

Secrets must be added **separately** for deployments:
1. Open the Deployments tab
2. Find the Secrets section
3. Add each secret needed for production

You can use different values than in development (e.g., test API keys vs. production keys).

## Health Checks

For web deployments, your app's homepage must respond within **5 seconds** for health checks to pass.

Ensure your server:
- Binds to `0.0.0.0` (not `localhost`)
- Starts quickly
- Returns HTTP 200 on the root path

## Custom Domains

All deployment types support custom domains:
1. Go to Deployments → Settings → Link a domain
2. Enter your domain name
3. Copy the DNS records (A records and TXT records)
4. Add them at your domain registrar
5. Wait for propagation
6. Replit automatically provisions TLS/SSL certificates

## Deployment URLs

- Default: `your-app-name.replit.app`
- Custom: Your own domain with CNAME/A record pointing to Replit

## Monitoring

Replit provides deployment monitoring:
- Request logs
- Error logs
- Resource usage metrics
- Status indicators

## Pricing Summary

| Type | Billing Method | Starting Cost |
|------|---------------|---------------|
| Autoscale | Compute Units ($1/million) + $1/month base | ~$1/month + usage |
| Reserved VM | Fixed monthly | ~$20/month |
| Static | Data transfer | Very low |
| Scheduled | Compute Units per run | Pay per run |
| Background Worker | Compute Units | Usage-based |

Core plan includes $25/month in usage credits covering AI, compute, and deployments.
