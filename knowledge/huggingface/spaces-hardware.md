# HuggingFace Spaces Hardware Tiers
> Sources: https://huggingface.co/docs/hub/en/spaces-overview, https://huggingface.co/docs/hub/spaces-zerogpu, https://github.com/huggingface/hub-docs/blob/main/docs/hub/spaces-zerogpu.md, https://huggingface.co/docs/hub/spaces-storage, https://huggingface.co/docs/hub/spaces-gpus, https://huggingface.co/pricing, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

HuggingFace Spaces can run on a range of hardware tiers, from free CPU to high-end multi-GPU configurations. Hardware is selected per-Space and billed hourly (charged per minute of actual runtime).

Default free tier: **2 vCPU, 16 GB RAM, 50 GB ephemeral disk** — no cost.

---

## CPU Hardware Tiers

| Tier | vCPU | RAM | Disk | Price/hr | Notes |
|------|------|-----|------|----------|-------|
| CPU Basic (free) | 2 | 16 GB | 50 GB ephemeral | Free | Default; sleeps after ~48hr inactivity |
| CPU Upgrade | 8 | 32 GB | 50 GB ephemeral | ~$0.03/hr | Stays awake; more RAM for larger apps |

---

## GPU Hardware Tiers

| Tier | GPU | VRAM | vCPU | RAM | Price/hr |
|------|-----|------|------|-----|----------|
| T4-small | 1x NVIDIA T4 | 16 GB | 4 | 15 GB | ~$0.40/hr |
| T4-medium | 1x NVIDIA T4 | 16 GB | 8 | 30 GB | ~$0.60/hr |
| A10G-small | 1x NVIDIA A10G | 24 GB | 4 | 15 GB | ~$1.00/hr |
| A10G-large | 1x NVIDIA A10G | 24 GB | 12 | 46 GB | ~$1.50/hr |
| A10G-largex2 | 2x NVIDIA A10G | 48 GB | 24 | 92 GB | ~$3.00/hr |
| A10G-largex4 | 4x NVIDIA A10G | 96 GB | 48 | 184 GB | ~$6.00/hr |
| L4x1 | 1x NVIDIA L4 | 24 GB | varies | varies | varies |
| L4x4 | 4x NVIDIA L4 | 96 GB | varies | varies | varies |
| L40Sx1 | 1x NVIDIA L40S | 48 GB | varies | varies | varies |
| L40Sx4 | 4x NVIDIA L40S | 192 GB | varies | varies | varies |
| L40Sx8 | 8x NVIDIA L40S | 384 GB | varies | varies | varies |
| A100-large | 1x NVIDIA A100 | 80 GB | 12 | 142 GB | ~$2.50–4.00/hr |
| A100x4 | 4x NVIDIA A100 | 320 GB | varies | varies | ~$10/hr |
| A100x8 | 8x NVIDIA A100 | 640 GB | varies | varies | ~$20/hr |

**Notes:**
- T4, A10G, and L4 tiers are generally available to all users
- A100 requires requesting from HuggingFace (Enterprise/org plan typically needed)
- H100 available via request for high-compute workloads

---

## ZeroGPU — Free Shared GPU

ZeroGPU is HuggingFace's shared GPU infrastructure: GPUs are **dynamically allocated** to your Space only while a function is running, then released. This makes GPU access much more economical for demo-style use.

**Current hardware:** NVIDIA RTX Pro 6000 Blackwell (previously H200)

| Size | Hardware | VRAM | Quota Cost |
|------|----------|------|------------|
| `large` (default) | Half RTX Pro 6000 Blackwell | 48 GB | 1x |
| `xlarge` | Full RTX Pro 6000 Blackwell | 96 GB | 2x |

### Daily GPU Quotas per Account

| Account | Daily Quota | Priority |
|---------|-------------|----------|
| Free account | 5 min/day | Medium |
| PRO account ($9/mo) | 40 min/day | Highest |
| Team/Enterprise | 40–60 min/day | Highest |

PRO users can purchase additional quota at **$1 per 10 minutes**.

### Using ZeroGPU in Your Space

**Requirements:**
- SDK must be **Gradio** (version 4+)
- Install `spaces` package: `pip install spaces`
- Python version: 3.10.13 or 3.12.12

**Decorate GPU-intensive functions with `@spaces.GPU`:**

```python
import spaces
import gradio as gr
import torch

# Load model once at startup (CPU)
model = load_model()

@spaces.GPU
def generate(prompt: str) -> str:
    # This function gets GPU access when called
    # GPU is released when function returns
    outputs = model.generate(prompt)
    return outputs

# For long-running tasks (>60s default), set duration:
@spaces.GPU(duration=120)  # 120 seconds
def generate_video(prompt: str):
    return video_pipeline(prompt)

# Dynamic duration based on input
@spaces.GPU(duration=lambda inputs: len(inputs) * 2)
def process(inputs):
    return heavy_computation(inputs)

demo = gr.Interface(fn=generate, inputs="text", outputs="text")
demo.launch()
```

**Important notes:**
- Default max duration: **60 seconds**
- Shorter durations get higher queue priority for visitors
- `torch.compile` is **not supported** — use ahead-of-time compilation instead
- The `@spaces.GPU` decorator is a no-op in non-ZeroGPU environments (safe to keep)
- Maximum 10 Spaces (PRO) or 50 Spaces (Team/Enterprise) can use ZeroGPU

### Who Can Create ZeroGPU Spaces?
- **Using existing ZeroGPU Spaces:** Free for all users
- **Creating your own ZeroGPU Space:** Requires PRO subscription or Team/Enterprise org
- **Community GPU Grants:** Available for qualifying open-source/research projects (apply on HF)

---

## Persistent Storage

By default, Space disk is **ephemeral** — all data is lost on restart/redeploy.

### Persistent Storage Tiers

| Tier | Size | Price/month |
|------|------|-------------|
| Small | 20 GB | $5/month |
| Medium | 150 GB | $25/month |
| Large | 1 TB | $100/month |

Storage is mounted at `/data` inside the Space container.

### Setting Up Persistent Storage

**Via UI:** Space Settings → Persistent Storage

**Via Python API:**
```python
from huggingface_hub import HfApi

api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Add persistent storage
api.add_space_storage(
    repo_id="username/my-space",
    storage="small",  # "small" | "medium" | "large"
)

# Delete persistent storage (WARNING: deletes all data)
api.delete_space_storage(repo_id="username/my-space")
```

**In your Space code:**
```python
import os
from pathlib import Path

# Persistent path
DATA_DIR = Path("/data")
model_cache = DATA_DIR / "models"
model_cache.mkdir(parents=True, exist_ok=True)

# Save/load from persistent storage
model.save_pretrained(model_cache / "my-model")
```

---

## Secrets and Environment Variables

### Adding Secrets (sensitive values)
Secrets are encrypted at rest and never visible in git history.

**Via UI:** Space Settings → Variables and Secrets → Add Secret

**Via Python API:**
```python
from huggingface_hub import HfApi

api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Add a secret
api.add_space_secret(
    repo_id="username/my-space",
    key="HF_TOKEN",
    value="hf_xxxxxxxxxxxxxxxx",
)

# Add a non-secret variable (visible in UI)
api.add_space_variable(
    repo_id="username/my-space",
    key="MODEL_ID",
    value="meta-llama/Llama-3.1-8B-Instruct",
)

# Delete a secret
api.delete_space_secret(repo_id="username/my-space", key="HF_TOKEN")
```

**Accessing in Space code:**
```python
import os

api_key = os.environ.get("MY_API_KEY")
hf_token = os.environ.get("HF_TOKEN")
model_id = os.environ.get("MODEL_ID", "default-model")
```

**Secrets are NOT copied when a Space is duplicated/forked** — a security feature.

---

## Custom Domains

Available to PRO and Enterprise users:

1. Go to Space Settings → Custom Domains
2. Add your domain (e.g., `demo.mycompany.com`)
3. Configure DNS CNAME to point to `{username}-{space-name}.hf.space`

Without custom domain, Spaces are accessible at:
- `https://huggingface.co/spaces/{user}/{space}`
- `https://{user}-{space}.hf.space` (direct)

---

## Setting Hardware in README.md

```yaml
---
title: My Demo
sdk: gradio
sdk_version: "5.0.0"
app_file: app.py
hardware: a10g-small    # Set specific hardware tier
suggested_hardware: t4-small  # Suggest hardware for users who duplicate
pinned: false
---
```

### Hardware tier values for README:
- `cpu-basic` (free)
- `cpu-upgrade`
- `t4-small`, `t4-medium`
- `a10g-small`, `a10g-large`
- `a100-large`
- `zero-gpu` (ZeroGPU)

---

## Programmatic Hardware Management

```python
from huggingface_hub import HfApi, SpaceHardware

api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Change hardware
api.request_space_hardware(
    repo_id="username/my-space",
    hardware=SpaceHardware.A10G_SMALL,
)

# Pause a Space (stop billing)
api.pause_space(repo_id="username/my-space")

# Restart a Space
api.restart_space(repo_id="username/my-space")

# Get current runtime info
runtime = api.get_space_runtime(repo_id="username/my-space")
print(runtime.hardware)  # Current hardware
print(runtime.stage)     # "RUNNING", "PAUSED", "BUILDING", etc.
```

---

## Sleep and Always-On Behavior

| Hardware | Sleep behavior |
|----------|----------------|
| CPU Basic (free) | Sleeps after ~48hr of inactivity |
| CPU Upgrade (paid) | Always on while running |
| Any GPU tier (paid) | Always on while running |
| ZeroGPU | Active, but GPU only allocated during function execution |

To keep a free Space alive: use the Space's "Keep Space alive" option, or upgrade hardware.

---

## References

- [Spaces Overview](https://huggingface.co/docs/hub/en/spaces-overview)
- [ZeroGPU Docs](https://huggingface.co/docs/hub/spaces-zerogpu)
- [GPU Spaces Guide](https://huggingface.co/docs/hub/spaces-gpus)
- [Persistent Storage](https://huggingface.co/docs/hub/spaces-storage)
- [HuggingFace Pricing](https://huggingface.co/pricing)
- [Manage Spaces via huggingface_hub](https://huggingface.co/docs/huggingface_hub/en/guides/manage-spaces)
