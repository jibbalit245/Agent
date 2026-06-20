# RunPod Overview and Quickstart
> Source: https://docs.runpod.io/pods/overview, https://www.runpod.io/product/serverless, https://www.lystr.tech/platform/runpod-gpu-cloud/, https://www.runpod.io/articles/guides/top-serverless-gpu-clouds
> Fetched: 2026-06-20

## What is RunPod?

RunPod is a GPU cloud platform that rents NVIDIA GPUs by the second for AI and ML workloads. It's designed to be cheaper and more flexible than major cloud providers (AWS, GCP, Azure) for GPU-intensive tasks like model training, fine-tuning, and inference.

Key differentiator: **per-second billing** — you pay from the moment a pod starts to the moment it stops, never rounded up to the hour. A 3-minute job costs 3 minutes.

## Service Types

### 1. GPU Pods (Dedicated Instances)

Full control over a containerized GPU VM. Think of it like renting an EC2 GPU instance, but per-second and with a Docker-centric workflow.

- **On-Demand Pods**: Reserved capacity; not interruptible. Higher price, guaranteed availability.
- **Spot Pods (Community Cloud)**: Available at 50–65% discount but can be interrupted (with ~5-second SIGTERM warning) when the host needs resources back. Good for fault-tolerant batch workloads.

Use pods for:
- Development and experimentation
- Long-running training jobs
- Workloads that need persistent state
- SSH access and interactive debugging

### 2. Serverless Endpoints

Auto-scaling inference infrastructure. You build a handler function, package it in Docker, and RunPod manages scaling from zero to N workers based on request queue depth.

- **Per-millisecond billing**: Workers are billed from start to full stop, rounded to nearest second.
- **Cold starts**: Sub-200ms cold starts via FlashBoot (pre-warmed worker cache). Larger images/models take longer.
- **Scale to zero**: Can drop to 0 workers when idle (no cost), or keep minimum workers active for low latency.

Use serverless for:
- Production inference APIs
- Variable traffic patterns
- Cost optimization at low traffic (scale to zero)

### 3. Clusters (Multi-node)

Multi-node GPU clusters for distributed training. Supports NVLink, InfiniBand, high-bandwidth inter-node networking. Available by reservation.

## How Billing Works

### Pods

- Billing starts the moment the pod reaches "Running" state.
- Billing stops the moment you terminate (not pause — termination is permanent; storage survives if using a Network Volume).
- Billed to the second, never to the hour.
- Storage is billed separately (per GB per month for Network Volumes).

### Serverless

- Workers are billed from when they start processing until fully stopped.
- Rounded up to the nearest second.
- You are NOT charged for idle time if Min Workers = 0.
- If Min Workers > 0, those workers accrue cost even without requests.

### Community Cloud vs Secure Cloud

| Feature | Community Cloud | Secure Cloud |
|---------|----------------|-------------|
| Pricing | Lower (community hosts) | Higher (RunPod-owned DCs) |
| Interruption | Spot pods can be interrupted | On-demand is guaranteed |
| Network Volumes | Not available | Available |
| Compliance | Community hosted | Datacenter-grade |
| Best for | Dev, batch, cost-sensitive | Production, persistent storage |

## Getting Started (Quickstart)

### 1. Create account and add funds

Sign up at runpod.io. Add credits via credit card. Minimum $10 deposit typically required.

### 2. Create your first pod

Navigate to **Pods > Deploy**:
1. Select a GPU type (RTX 4090 for dev, A100 for serious training)
2. Choose On-Demand or Spot
3. Select a template (PyTorch, TensorFlow, or custom Docker image)
4. Set container disk size and optionally attach a Network Volume
5. Click Deploy

### 3. Access your pod

- **SSH**: Use the SSH command provided in the pod details page.
- **HTTP**: Map a port (e.g., 8888 for Jupyter, 7860 for Gradio).
- **Web terminal**: Built into the RunPod console.

### 4. Terminate when done

Always terminate pods you're not using. Use the Stop or Terminate button in the console, or via the API.

## API Key

Manage all resources programmatically with your RunPod API key:
- Settings > API Keys > Create API Key
- Use as `RUNPOD_API_KEY` environment variable

## Available Regions

RunPod operates data centers across:
- United States (multiple)
- Europe (Poland, Netherlands, Sweden)
- Asia (limited)

Community Cloud spans additional host locations worldwide.

## Rough Cost Comparison vs AWS

| GPU | RunPod (Community) | RunPod (Secure) | AWS p3.2xlarge equiv |
|----|-------------------|----------------|----------------------|
| RTX 4090 | ~$0.39–0.69/hr | ~$0.89/hr | N/A (no 4090) |
| A100 80GB | ~$0.89–1.89/hr | ~$1.89/hr | ~$3.06/hr (p4d.xlarge) |
| H100 80GB | ~$1.89–2.99/hr | ~$2.89/hr | ~$6+ (p5.xlarge equiv) |

RunPod is typically 2–5x cheaper than AWS for GPU time. The tradeoff is less ecosystem integration (no native IAM, CloudWatch, VPC, etc.).
