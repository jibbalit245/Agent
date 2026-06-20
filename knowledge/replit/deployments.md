# Replit Deployments
> Source: https://docs.replit.com/cloud-services/deployments/about-deployments
> Fetched: 2026-06-20

## Overview

Replit offers one-click deployment with multiple deployment types, each suited for different use cases. Deployed apps get a persistent URL and stay running even when you're not actively working in the Repl.

All deployment types (except Static) support environment secrets. Deployed apps are separate from the development workspace.

## Deployment Types

### 1. Autoscale Deployments

**Best for**: Web apps and APIs with variable traffic

Autoscale deployments automatically scale up or down based on incoming request volume:
- **Scales to zero** when there's no traffic (cost-efficient)
- **Scales up** automatically when traffic increases
- Pay only for actual compute used

**Billing (Compute Units)**:
- 1 RAM second = 2 Compute Units
- 1 CPU second = 18 Compute Units
- Base fee: $1/month (as of February 2025)
- Overage: $1 per 1 million Compute Units

**Use cases**: APIs, web apps, Replit Agent-built apps, background services

**Cold start**: Apps that scale to zero will have a cold start delay when first request arrives

### 2. Reserved VM Deployments

**Best for**: Apps that need always-on availability, persistent state, or constant low-latency

Reserved VMs run 24/7 on dedicated compute:
- No cold starts
- Persistent memory and process state
- Predictable monthly cost

**Pricing (approximate, 2025)**:
- Starting at ~$20/month for the base Reserved VM tier
- Shared Reserved VM: lower cost, shared underlying hardware
- Dedicated Reserved VM: higher cost, dedicated hardware (pricing decreased in 2025 update)

**Use cases**: Websocket servers, Discord bots, cron-like long-running processes, databases, always-on APIs

### 3. Static Deployments

**Best for**: HTML, CSS, JavaScript sites with no server-side logic

- **Free** (up to 100 GiB of outbound data with Replit Core)
- Hosts pre-built static files
- Served via CDN
- **Does NOT support secrets/environment variables**
- No server-side code execution

**Use cases**: Landing pages, documentation sites, portfolios, pre-built React/Vue/Svelte apps

### 4. Scheduled Deployments

**Best for**: Periodic jobs, data pipelines, report generation

Runs on a user-defined schedule (cron-style):
- Define a schedule (e.g., every hour, daily at midnight)
- A VM spins up, runs the job, then shuts down
- Pay only for the time the job runs

**Pricing**:
- ~$0.000061/second of execution time
- Base fee: $1/month (as of February 2025)

**Use cases**: Data scraping, daily email reports, scheduled API calls, database maintenance

## How to Deploy

### From the Replit Workspace

1. Open your Repl
2. Click the **"Deploy"** button (rocket icon in sidebar)
3. Select deployment type (Autoscale, Reserved VM, Static, or Scheduled)
4. Configure settings:
   - **Name**: Deployment name / subdomain
   - **Machine type**: CPU/RAM configuration
   - **Build command**: e.g., `pip install -r requirements.txt`
   - **Run command**: e.g., `python main.py`
   - **Secrets**: Add environment variables (separate from workspace secrets!)
5. Click **"Deploy"**

### Via Replit CLI (optional)

```bash
# Install Replit CLI
npm install -g replit

# Deploy from command line
replit deploy
```

## Deployment URLs

- Default: `{deployment-name}.{username}.repl.co` or `{deployment-name}.replit.app`
- Custom domains: Available on Core and higher plans

## Deployment vs Development Workspace

**Critical distinction**: Your development Repl and your deployed app are **separate environments**:

| Aspect | Development Workspace | Deployed App |
|--------|----------------------|--------------|
| Secrets | Workspace Secrets tab | Must be added in Deploy → Settings |
| URL | Temporary (replit.dev) | Persistent (repl.co or custom) |
| State | Pauses when you close | Runs continuously |
| Code changes | Immediate | Requires re-deploy |

You must **explicitly add secrets** to the deployment configuration — workspace secrets do NOT automatically transfer to deployed apps (exception: 2025 update enabled automatic syncing of workspace secrets to deployment secrets for some plans).

## Machine Types for Autoscale/Reserved VM

| Type | vCPU | RAM | Notes |
|------|------|-----|-------|
| 0.5 vCPU / 0.5 GiB | 0.5 | 512 MB | Free tier default |
| 1 vCPU / 1 GiB | 1 | 1 GB | Small apps |
| 2 vCPU / 2 GiB | 2 | 2 GB | Medium apps |
| 4 vCPU / 4 GiB | 4 | 4 GB | Large apps |
| Custom | varies | varies | Higher tiers available |

No GPU options in standard deployment machine types.

## Deployment Pricing Calculator

Use the official calculator: [https://deployment-pricing.replit.app](https://deployment-pricing.replit.app)

Full pricing docs: [https://docs.replit.com/billing/deployment-pricing](https://docs.replit.com/billing/deployment-pricing)

## Build and Run Configuration

Each deployment has:

```toml
# .replit file (auto-generated or manually configured)
[deployment]
run = ["python", "main.py"]
build = ["pip", "install", "-r", "requirements.txt"]
deploymentTarget = "autoscale"  # or "gce" for Reserved VM

[[ports]]
localPort = 8080
externalPort = 80
```

## Health Checks

For Autoscale deployments, Replit pings your app's health endpoint:
- Default: HTTP GET to `/`
- Configurable: set a custom health check path
- App must respond with 2xx within the timeout period

## Rollbacks

You can roll back to a previous deployment version from the Deploy panel in the Replit workspace.

## References

- [Replit Deployments Docs](https://docs.replit.com/cloud-services/deployments/about-deployments)
- [Deployment Pricing](https://docs.replit.com/billing/deployment-pricing)
- [Autoscale Deployments Announcement](https://blog.replit.com/autoscale)
- [Deployment Pricing Calculator](https://deployment-pricing.replit.app)
