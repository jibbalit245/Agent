# Replit Autoscale Deployments

> Source: https://docs.replit.com/deployments/autoscale-deployments
> Updated URL: https://docs.replit.com/cloud-services/deployments/autoscale-deployments
> Last updated: 2026-06

## What are Autoscale Deployments?

Autoscale Deployments run on cloud computing resources that **scale up and down** to efficiently handle the network traffic and workload of your Replit App. When your app is busy, autoscaling adds servers to manage the load. When your app is idle, it reduces the number of instances to as low as **zero** to save you money.

You're charged only when your app serves traffic.

## Key Features

- **Automatic scaling**: Adjusts resources based on traffic patterns
- **Scale to zero**: When idle, reduces instances to zero (no cost)
- **Custom domains**: Use `appname.replit.app` or your own domain
- **Configurable limits**: Set the maximum number of instances your app can scale to
- **Cold start optimization**: Replit has improved cold-start times for faster wake-ups

## Use Cases

Autoscale is best for:
- Web applications and APIs with variable traffic
- Development and staging environments
- Apps that can tolerate occasional cold starts
- Cost-optimized production workloads

## How to Set Up

1. Open your Replit App
2. Click **Publishing** (or the Deploy button)
3. Select **Autoscale** option
4. Click **Set up your published app**
5. Configure:
   - Machine size (vCPUs, RAM)
   - Maximum instances
   - Run command
   - Deployment secrets
6. Click **Deploy**

## Machine Sizes

Autoscale deployments support various machine configurations:

| Size | vCPUs | RAM |
|------|-------|-----|
| Nano | 0.25 vCPU | 256 MB |
| Micro | 0.5 vCPU | 512 MB |
| Small | 1 vCPU | 1 GB |
| Medium | 2 vCPUs | 2 GB |
| Large | 4 vCPUs | 4 GB |

*Exact sizes/names may vary — check current Replit dashboard for available options.*

## Pricing and Billing

### Compute Units

Autoscale deployments are billed via **Compute Units** (a measure of CPU and RAM usage):

| Resource | Rate |
|----------|------|
| 1 CPU second | 18 Compute Units |
| 1 GB-second RAM | 2 Compute Units |

**Cost per million Compute Units: $1**

### Base Fee
- **$1/month** base fee for each autoscale deployment (introduced February 2025)

### Example Cost Estimate

A small web app with light traffic:
- ~5-10 CPU-seconds per request, 512 MB RAM
- 10,000 requests/month ≈ $1-3/month in compute + $1 base fee

### Core Plan Credits

Replit Core includes **$25/month** in usage credits covering AI, compute, and deployments. Light-to-medium apps may fit entirely within credits.

## Scaling Configuration

You can configure:
- **Minimum instances**: Usually 0 (scale to zero) or 1 (always warm)
- **Maximum instances**: Cap on how many instances can run simultaneously

## Cold Starts

When scaled to zero, the first request after idle triggers a **cold start** — a brief delay while a new instance spins up. Replit has made behind-the-scenes improvements to cold-start times.

To minimize cold starts:
- Keep minimum instances at 1 (increases cost but eliminates cold starts)
- Optimize app startup time
- Use lightweight dependencies

## Health Checks

Your app must:
1. Bind to `0.0.0.0` (not `localhost`)
2. Listen on the correct port (typically 8080)
3. Respond to HTTP requests on the root path `/` within **5 seconds**

## Deployment Secrets

Add production secrets separately from workspace secrets:
1. Open Deployments tab
2. Go to Secrets section
3. Add key-value pairs for production environment

## Custom Domains

1. Go to Deployments → Settings → Link a domain
2. Add your domain
3. Set DNS records at registrar:
   - A record pointing to Replit's IP
   - TXT record for verification
4. TLS certificate auto-provisioned by Replit

## Monitoring

- View request logs in the Deployments tab
- Monitor resource usage
- Set up error alerting

## Comparison with Reserved VM

| Feature | Autoscale | Reserved VM |
|---------|-----------|-------------|
| Cost model | Usage-based | Fixed monthly |
| Scale to zero | Yes | No |
| Cold starts | Possible | No |
| Predictability | Variable cost | Fixed cost |
| Best for | Variable traffic | Steady/heavy traffic |
