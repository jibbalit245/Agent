# RunPod Pricing Guide
> Source: https://www.runpod.io/pricing, https://northflank.com/blog/runpod-gpu-pricing, computeprices.com, deploybase.ai, checkthat.ai
> Fetched: 2026-06-20

## Billing Fundamentals

- **Per-second billing** — billed from the moment a GPU starts to the moment it stops
- **No rounding up to the hour** — a 5-minute job costs 5 minutes
- **Two cloud tiers**: Secure Cloud (RunPod-owned DCs) and Community Cloud (distributed hosts)
- **No egress fees** — no charges for data transfer out

---

## GPU Pod Pricing

### Consumer GPUs (Community Cloud Only)

| GPU | VRAM | Community Spot | Community On-Demand |
|-----|------|---------------|---------------------|
| RTX 3090 | 24 GB | ~$0.10–0.15/hr | ~$0.19–0.34/hr |
| RTX 3090 Ti | 24 GB | ~$0.12–0.17/hr | ~$0.22–0.39/hr |
| RTX 4090 | 24 GB | ~$0.19–0.35/hr | ~$0.34–0.69/hr |

### Professional GPUs — Community Cloud

| GPU | VRAM | Community Spot | Community On-Demand |
|-----|------|---------------|---------------------|
| A40 | 48 GB | ~$0.25/hr | ~$0.44/hr |
| RTX A5000 | 24 GB | ~$0.14/hr | ~$0.27/hr |
| RTX A6000 | 48 GB | ~$0.39/hr | ~$0.79/hr |
| L4 | 24 GB | ~$0.28/hr | ~$0.44/hr |
| A100 PCIe 40GB | 40 GB | ~$0.45/hr | ~$0.89/hr |
| A100 SXM 80GB | 80 GB | ~$0.75/hr | ~$1.49/hr |
| H100 PCIe 80GB | 80 GB | ~$0.99/hr | ~$1.89/hr |
| H100 SXM 80GB | 80 GB | ~$1.49/hr | ~$2.69/hr |
| H200 SXM 141GB | 141 GB | ~$1.79/hr | ~$3.59/hr |
| B200 192GB | 192 GB | ~$2.99/hr | ~$5.98/hr |

### Secure Cloud Pricing (Higher, More Reliable)

| GPU | VRAM | Secure On-Demand |
|-----|------|-----------------|
| RTX 3090 | 24 GB | ~$0.44/hr |
| RTX 4090 | 24 GB | ~$0.69/hr |
| L40S | 48 GB | ~$0.99–1.49/hr |
| A100 PCIe 40GB | 40 GB | ~$1.39/hr |
| A100 SXM 80GB | 80 GB | ~$1.89/hr |
| H100 PCIe 80GB | 80 GB | ~$2.89/hr |
| H100 SXM 80GB | 80 GB | ~$3.49/hr |
| H200 SXM | 141 GB | ~$3.99/hr |

**Note**: Prices fluctuate with GPU availability. Community Cloud prices are lower but supply varies.

---

## Serverless Pricing

Serverless workers bill per second of GPU compute time.

### Approximate Compute Rates

| GPU | $/second | $/hour equiv |
|-----|----------|-------------|
| RTX 3090 | ~$0.000144/s | ~$0.52/hr |
| RTX 4090 | ~$0.000194/s | ~$0.70/hr |
| L40S | ~$0.000278/s | ~$1.00/hr |
| A100 PCIe | ~$0.000389/s | ~$1.40/hr |
| A100 80GB | ~$0.000556/s | ~$2.00/hr |
| H100 PCIe | ~$0.000833/s | ~$3.00/hr |
| H100 SXM | ~$0.001000/s | ~$3.60/hr |

### Serverless Cost Examples

**7B model inference (3 seconds per request, RTX 4090)**:
- Per request: 3s × $0.000194/s = **$0.000582**
- 1,000 requests/day = **$0.58/day** = **~$17.40/month**

**70B model inference (30 seconds per request, H100)**:
- Per request: 30s × $0.000833/s = **$0.025**
- 1,000 requests/day = **$25/day** = **~$750/month**

### Min Workers Cost

Active (minimum) workers are billed continuously:
- 1 always-on RTX 4090 worker = $0.70/hr × 24 × 30 = **$504/month**
- Active worker discount: up to 30% off → **~$353/month**

### Scale-to-Zero (Zero idle cost)

Set Min Workers = 0:
- No cost when no requests
- Cold start on first request after idle period
- Pay only for actual compute

---

## Network Volume / Storage Pricing

| Tier | Price | Notes |
|------|-------|-------|
| Standard NVMe | $0.07/GB/month | General purpose |
| High-Performance NVMe | $0.20/GB/month | 3x throughput, 4x IOPS |
| Unmounted volume | $0.10/GB/month | When no pod is attached |

### Storage Cost Examples

| Size | Standard/month | High-Perf/month |
|------|---------------|-----------------|
| 50 GB | $3.50 | $10.00 |
| 100 GB | $7.00 | $20.00 |
| 500 GB | $35.00 | $100.00 |
| 1 TB | $71.68 | $204.80 |
| > 1 TB | $0.05/GB additional | $0.05/GB additional |

**Important**: Network volumes accrue charges even when no pod is attached. Delete unused volumes.

---

## Pod Storage Pricing

Container disk is ephemeral (disappears on terminate) and included in the pod price.

For additional persistent storage tied to the pod lifetime:
- Volume disk (not network volume): charged at per-GB rates
- Disappeared when pod is terminated

---

## Data Transfer

- **Ingress (upload to RunPod)**: Free
- **Egress (download from RunPod)**: Free
- **No bandwidth charges** — RunPod does not charge for network traffic

This is a major advantage over AWS, GCP, Azure which charge significant egress fees.

---

## CPU Instances (No GPU)

For lightweight tasks (preprocessing, API backends):

| Type | vCPUs | RAM | Price |
|------|-------|-----|-------|
| cpu3c-2-4 | 2 vCPU | 4 GB | ~$0.02/hr |
| cpu3c-4-8 | 4 vCPU | 8 GB | ~$0.04/hr |
| cpu3c-8-16 | 8 vCPU | 16 GB | ~$0.08/hr |

---

## Community Cloud vs Secure Cloud

| Feature | Community Cloud | Secure Cloud |
|---------|----------------|-------------|
| Pricing | 40-60% cheaper | Higher, stable |
| Availability | Variable | More reliable |
| Interruption | Spot pods can be reclaimed | On-demand is guaranteed |
| Network Volumes | NOT available | Available |
| Compliance | Community-hosted hardware | RunPod-owned DCs |
| Best for | Dev, batch, experiments | Production, persistent state |

---

## How to Minimize Costs

1. **Use Community Cloud for dev** — 40-60% cheaper than Secure Cloud
2. **Use Spot pods for training** — Lower prices, implement checkpointing
3. **Set Min Workers = 0** for serverless unless latency SLA requires otherwise
4. **Delete network volumes** you no longer need
5. **Terminate (don't just stop) pods** when done — stopped pods still charge for storage
6. **Use smaller quantized models** — INT4 7B model needs ~4 GB VRAM vs ~14 GB for FP16
7. **Keep images small** — Smaller Docker images = faster cold starts = less billed startup time
8. **Use FlashBoot** — Pre-cached containers skip image pull time

---

## Billing and Payments

- **Prepaid credits** — Add credits via credit card (no subscription required)
- **Minimum deposit**: Typically $10
- **Auto-recharge**: Set up automatic credit recharge when balance drops
- **Usage visible** in real-time on the dashboard
- **Alerts**: Set spending alerts to avoid surprises
