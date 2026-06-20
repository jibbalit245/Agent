# Modal Pricing

> Source: https://modal.com/pricing
> Note: Page returned HTTP 403 during crawl; content compiled from search results and third-party pricing sources (2026).

## Overview

Modal uses a **pay-per-millisecond** billing model. You only pay for actual compute time — no charges when containers are idle. New accounts receive **$30/month in free compute credits**.

## Key Billing Principles

- **No idle charges** - Containers are billed only while actively running
- **Per-millisecond precision** - Granular billing, no rounding up to minutes/hours
- **No egress fees** - Data transfer out is free
- **No storage fees for basic use** - Volume storage may have separate pricing
- **No API call fees** - Only pay for compute

## GPU Pricing

| GPU | Price per Hour | Price per Second | VRAM |
|-----|---------------|-----------------|------|
| T4 | ~$0.59/hr | ~$0.000164/sec | 16 GB |
| L4 | ~$0.80/hr | ~$0.000222/sec | 24 GB |
| A10G | ~$1.10/hr | ~$0.000306/sec | 24 GB |
| A100 (40GB) | ~$2.40/hr | ~$0.000667/sec | 40 GB |
| A100 (80GB) | ~$2.70/hr | ~$0.000750/sec | 80 GB |
| H100 (SXM) | ~$4.29/hr | ~$0.001192/sec | 80 GB |
| H100 (PCIe) | ~$3.50/hr | ~$0.000972/sec | 80 GB |

> **Note:** Prices shown are base US region rates. Regional multipliers apply (see below).

## CPU Pricing

| Resource | Price |
|----------|-------|
| CPU (per core-hour) | ~$0.05/hr per core |
| Memory (per GB-hour) | ~$0.01/hr per GB |

Base CPU rate: ~$0.0000131 per CPU core-second

## Regional Pricing Multipliers

Modal supports multiple cloud regions. Prices vary by region:

| Region | Multiplier |
|--------|-----------|
| US (default) | 1.0x |
| EU | ~1.25-1.5x |
| Asia-Pacific | ~1.5-1.75x |

## Preemptibility

Modal offers preemptible and non-preemptible compute:

| Type | Pricing | Notes |
|------|---------|-------|
| Preemptible | Base price | May be interrupted, good for batch jobs |
| Non-preemptible | ~3x base price | Guaranteed compute, for critical workloads |

## Free Tier

| Feature | Free Tier |
|---------|-----------|
| Monthly credits | $30/month |
| Expiration | Credits refresh monthly |
| GPU access | Yes |
| Web endpoints | Yes |
| Secrets | Unlimited |
| Volumes | Yes |
| Deployments | Yes |

## Plan Tiers

| Feature | Free/Starter | Team | Enterprise |
|---------|-------------|------|-----------|
| Monthly free credits | $30 | $30 | Custom |
| Deployed endpoints | Limited | More | Unlimited |
| Custom domains | No | Yes | Yes |
| Priority support | No | Yes | Yes |
| SLA | No | No | Yes |
| Private networking | No | No | Yes |
| SSO | No | No | Yes |

## Cost Estimation Examples

### Image Generation (FLUX Schnell)

```
Workload: 100 image generations/day
GPU: A10G
Time per generation: ~3 seconds

Daily cost: 100 × 3s × $0.000306/s = $0.09/day
Monthly cost: ~$2.72/month
```

### LLM Inference (Llama 70B)

```
Workload: 1,000 requests/day
GPU: A100-80GB
Time per request: ~5 seconds

Daily cost: 1,000 × 5s × $0.000750/s = $3.75/day
Monthly cost: ~$112.50/month
```

### Training Run (One-time)

```
Training: Fine-tune SDXL for 2 hours
GPU: H100
Cost: 2 hours × $4.29/hr = $8.58
```

### Web Endpoint (API Service)

```
Traffic: 10,000 requests/day
GPU: A10G
Average request time: 1 second

Daily cost: 10,000 × 1s × $0.000306/s = $3.06/day
Monthly cost: ~$91.80/month
```

## Cost Optimization Strategies

### 1. Use Appropriate GPU

```python
# Don't use H100 for simple tasks
# T4 is 7x cheaper than H100

@app.function(gpu="T4")  # Good for small models
def small_model_inference():
    pass

@app.function(gpu="H100")  # For large models that need it
def large_model_inference():
    pass
```

### 2. Container Lifecycle Optimization

```python
# Load model once per container, not per request
@app.cls(gpu="A10G")
class ModelServer:
    @modal.enter()
    def load_model(self):
        # Loaded once when container starts
        self.model = load_expensive_model()
    
    @modal.method()
    def infer(self, prompt: str):
        # Fast - model already loaded
        return self.model(prompt)
```

### 3. GPU Fallbacks for Better Availability

```python
@app.function(gpu=["H100", "A100-80GB", "A10G"])
def flexible_inference():
    # Tries cheaper options if H100 unavailable
    pass
```

### 4. Batch Processing

```python
# Process multiple items in parallel instead of sequentially
results = list(my_function.map(items))  # Much cheaper than sequential
```

### 5. Right-size Memory

```python
# Only request what you need
@app.function(gpu="A10G", memory=8192)  # 8GB instead of default 32GB
def memory_efficient_function():
    pass
```

## Billing Dashboard

Monitor usage and costs at: https://modal.com/billing

- Real-time usage graphs
- Cost breakdown by function/app
- Historical usage data
- Invoice downloads

## Payment

- Credit card required
- Billed monthly for usage above free credits
- Enterprise: custom invoicing available
