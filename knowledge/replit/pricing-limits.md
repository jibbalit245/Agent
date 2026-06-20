# Replit Pricing & Limits
> Source: https://docs.replit.com/getting-started/faq, https://replit.com/pricing
> Fetched: 2026-06-20

## Plan Overview (2026)

Replit restructured its plans in early 2026, reducing Core pricing and adding a Pro tier for advanced teams.

| Plan | Price | Target User |
|------|-------|-------------|
| **Starter** | Free | Learners, hobbyists, prototyping |
| **Core** | $20/month (annual) or $25/month | Individual developers building real projects |
| **Pro** | Higher (team-focused) | Advanced teams, collaboration |
| **Teams** | $40/seat/month | Teams with centralized admin |
| **Enterprise** | Custom | Large organizations |

## Free Tier (Starter) — Limits and Capabilities

### Compute Resources (Development)
- **RAM**: 512 MB (hard limit per Repl)
- **CPU**: 0.5 vCPU
- **Storage**: ~1–10 GB per Repl (practical limit for code + dependencies)
- **Inactivity sleep**: Repls pause after ~5 minutes of inactivity; 10–30 second cold start on resume

### AI Features
- **Daily AI credits**: Limited daily credits for Replit Agent and AI coding features
- **Agent checkpoints**: ~10/month (checkpoints are save points in Agent's workflow)
- **Publish one app**: Can deploy 1 public app

### Deployment Limits (Free)
- **Static deployments**: Free (serves HTML/CSS/JS)
- **Autoscale/Reserved VM/Scheduled**: Not available on free tier (requires Core or higher)
- **Custom domains**: Not available (free apps get `.replit.app` subdomain)
- **Private apps**: Not available (free tier is public only)

### Other Limits
- Public Repls only (no private Repls on free tier)
- Limited collaboration features
- No priority support

## Core Plan ($20/month annual, $25/month monthly)

### What Core Adds
- Unlimited public and private Repls
- **Up to 5 collaborators** without needing Teams subscription
- All deployment types (Autoscale, Reserved VM, Static, Scheduled)
- Custom domains for deployed apps
- Static deployments: free up to 100 GiB outbound data
- More AI credits and Agent checkpoints
- ZeroGPU access (if using Spaces-like features)

### Core Compute Resources
- Higher RAM options in development
- Access to larger machine types in deployment

## Compute Units (Autoscale & Scheduled Deployments)

Autoscale and Scheduled deployments bill by **Compute Units**:

### How Compute Units Work

```
Compute Units = (RAM usage × time) + (CPU usage × time)

1 RAM-second = 2 Compute Units
1 CPU-second = 18 Compute Units
```

**Example calculation**:
If your app uses 256 MB RAM and 0.1 vCPU for 10 seconds:
- RAM: 0.256 GB-seconds × 2 = 0.512 Compute Units/second × 10 = 5.12 CU
- CPU: 0.1 CPU-seconds × 18 = 1.8 CU
- Total: ~7 CU for that request

### Pricing
- **Overage**: $1 per 1 million Compute Units
- **Base fee**: $1/month for Autoscale and Scheduled deployments (added February 2025)

### Free Compute Units (Core Plan)
Core plan includes a monthly allotment of Compute Units before overages apply.

## Reserved VM Pricing

Reserved VMs charge a fixed monthly rate for always-on compute:

| VM Type | vCPU | RAM | Approximate Price |
|---------|------|-----|-------------------|
| Shared VM (small) | 0.5 | 512 MB | ~$7–10/month |
| Shared VM (medium) | 1 | 1 GB | ~$15–20/month |
| Reserved VM (dedicated, base) | 1 | 2 GB | ~$20/month |
| Reserved VM (dedicated, larger) | 2+ | 4+ GB | $40+/month |

Prices shifted in 2025 — Dedicated VMs became cheaper while Shared VMs had pricing adjustments.

## Static Deployment Limits

- **Free**: Unlimited static deployments on free tier (HTML/CSS/JS)
- **Data transfer**: Up to 100 GiB outbound included with Core; overages charged beyond that

## Deployment Pricing Calculator

Use the official tool: [https://deployment-pricing.replit.app](https://deployment-pricing.replit.app)

## RAM Limit Impacts

The 512 MB RAM limit on the free tier is significant for ML/AI:

| Task | Approximate RAM | Works on Free? |
|------|-----------------|----------------|
| Flask/FastAPI (serving) | ~50–100 MB | Yes |
| Calling external AI APIs | ~50 MB | Yes |
| NumPy/Pandas (small datasets) | ~100–300 MB | Yes |
| Small NLP models (DistilBERT) | ~300–500 MB | Marginal |
| Sentence transformers (MiniLM) | ~100–200 MB | Yes |
| PyTorch (import only) | ~300 MB | Marginal |
| LLaMA 7B (local) | ~14 GB | No |
| Stable Diffusion (local) | ~4–8 GB | No |

## Storage Limits

- **Free tier**: ~1–10 GB per Repl (enough for code, not large model weights)
- **Core**: Higher storage limits
- **Large files**: HuggingFace model weights (multi-GB) are not practical to store in a Repl

## Bandwidth and Networking

- Outbound requests (calling external APIs): Allowed, no strict per-request limits
- Inbound traffic: Rate limited on free tier; higher limits on paid plans
- External API calls are standard network requests — no special Replit restrictions

## 2025-2026 Pricing Changes Summary

1. **February 2025**: Added $1/month base fee for Autoscale and Scheduled deployments
2. **2025**: Dedicated Reserved VM pricing decreased (became cheaper)
3. **February 2026**: Core plan reduced from $25 to $20/month (annual); new Pro tier added; Core now supports up to 5 collaborators

## Comparing Replit to Alternatives

| Platform | Free GPU | Free CPU | Deployment | ML Focus |
|----------|----------|----------|------------|----------|
| Replit | No (beta) | 512 MB | Yes (paid) | No |
| Google Colab | Yes (T4) | Yes | No | Yes |
| HuggingFace Spaces | No (CPU) | Yes | Yes | Yes |
| Modal | No free GPU | Serverless | Yes | Yes |
| Railway | No | 512 MB | Yes | No |

## References

- [Replit Pricing Page](https://replit.com/pricing)
- [Replit Deployment Pricing](https://docs.replit.com/billing/deployment-pricing)
- [Replit Free Tier Limitations](https://p0stman.com/guides/replit-limitations)
- [Replit Pricing Breakdown (Superblocks)](https://www.superblocks.com/blog/replit-pricing)
- [Replit Pricing 2026 (lowcode.agency)](https://www.lowcode.agency/blog/replit-pricing-explained)
- [Replit Pricing Calculator](https://deployment-pricing.replit.app)
