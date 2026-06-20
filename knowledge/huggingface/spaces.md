# HuggingFace Spaces
> Source: https://huggingface.co/docs/hub/en/spaces-overview
> Fetched: 2026-06-20

## Overview

HuggingFace Spaces is a platform for hosting and sharing ML demo applications directly on the Hub. You can deploy Gradio, Streamlit, or Docker-based apps in minutes with a simple Git push, no server configuration required.

Spaces are hosted at: `https://huggingface.co/spaces/{username}/{space-name}`

## Supported SDKs / Deployment Types

- **Gradio** — most common; HF has deep integration with Gradio
- **Streamlit** — full Streamlit support with secrets management via Streamlit's native secrets system
- **Docker** — full custom Docker containers; maximum flexibility
- **Static HTML** — serve static HTML/CSS/JS sites

## Creating a Space

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose SDK (Gradio, Streamlit, Docker, Static)
4. Push code to the Space's git repository

The Space is configured via a `README.md` file with a YAML front matter block, or through the UI.

### Example README.md (Gradio)

```yaml
---
title: My Demo
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.0.0"
app_file: app.py
pinned: false
---
```

### Minimal Gradio App (app.py)

```python
import gradio as gr

def greet(name):
    return f"Hello, {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch()
```

## Environment Variables and Secrets

### Setting Secrets

Secrets are set via the Space's **Settings tab** in the UI (not committed to git). They are:
- Encrypted at rest
- Not visible in the code editor or git history
- Not transferred when someone forks your Space

### Accessing Secrets in Code

Secrets are injected as environment variables at runtime:

**Python (Gradio, Docker):**
```python
import os

api_key = os.environ.get("MY_API_KEY")
hf_token = os.environ.get("HF_TOKEN")
```

**Streamlit:**
Streamlit Spaces use Streamlit's native secrets management:
```python
import streamlit as st

api_key = st.secrets["MY_API_KEY"]
```

### Special Environment Variables in Spaces

Spaces automatically provide certain env vars:
- `SPACE_ID` — the Space's repo ID
- `SPACE_AUTHOR_NAME` — owner's username
- `SPACE_REPO_NAME` — Space name
- `SPACE_TITLE` — display title
- `HF_TOKEN` — if you add your token as a secret named `HF_TOKEN`

### Configuration Changes Trigger Restarts

Any change to Space configuration (adding/removing secrets, changing hardware) will trigger an automatic restart of the app.

## Hardware Tiers

### Free CPU Tier
- **CPU Basic**: 2 vCPU, 16 GB RAM — free, always on during activity
- Spaces sleep after ~48 hours of inactivity on the free CPU tier
- Ideal for lightweight demos (text-based, small models, UI demos)

### Paid Hardware (Upgraded CPU and GPU)

| Hardware | vCPU | RAM | GPU | Price/hr |
|----------|------|-----|-----|----------|
| CPU Upgrade | 8 | 32 GB | — | ~$0.03 |
| T4-small | 4 | 15 GB | 1x T4 (16 GB VRAM) | ~$0.40 |
| T4-medium | 8 | 30 GB | 1x T4 (16 GB VRAM) | ~$0.60 |
| A10G-small | 4 | 15 GB | 1x A10G (24 GB VRAM) | ~$1.00 |
| A10G-large | 12 | 46 GB | 1x A10G (24 GB VRAM) | ~$1.50 |
| A10G-largex2 | 24 | 92 GB | 2x A10G | ~$3.00 |
| A10G-largex4 | 48 | 184 GB | 4x A10G | ~$6.00 |
| L4x1 | — | — | 1x L4 | varies |
| L4x4 | — | — | 4x L4 | varies |
| L40Sx1–L40Sx8 | — | — | 1–8x L40S | varies |
| A100-large | 12 | 142 GB | 1x A100 (80 GB VRAM) | ~$2.50 |
| A100x4 | — | — | 4x A100 | ~$10.00 |
| A100x8 | — | — | 8x A100 | ~$20.00 |

> **Note**: A100 is not generally available — requires requesting from HuggingFace (available for organizations). A10G and L4 are available to everyone.

### ZeroGPU (Free GPU for PRO Users)
- PRO account holders ($9/month) can use ZeroGPU — access to H200 GPU
- Dynamic allocation (shared, not dedicated); time-limited per request
- Free for the PRO subscription; great for demos that need GPU occasionally
- Community GPU grants also available for qualifying open research projects

### Setting Hardware via README.md

```yaml
---
sdk: gradio
hardware: a10g-small
---
```

Or programmatically via the `huggingface_hub` Python library.

## Persistent Storage

By default, Spaces have ephemeral storage (data is lost on restart). For persistent data, you can attach a **Persistent Storage** volume:

### Storage Options
- **Small**: ~20 GB
- **Medium**: ~150 GB  
- **Large**: ~1 TB

Persistent storage is attached as a mounted volume (typically at `/data`), survives restarts and hardware upgrades.

### Setting Up Persistent Storage

Via the Space's Settings tab in the UI, or via configuration:

```python
from huggingface_hub import HfApi

api = HfApi()
api.add_space_storage(
    repo_id="username/my-space",
    storage="small",  # "small", "medium", or "large"
    token="hf_xxxxxxxx",
)
```

## Custom Domains

Paid plan users (PRO or Enterprise) can set custom domains for their Spaces:
1. Go to Space Settings → Custom Domains
2. Add your domain (e.g., `mydemo.example.com`)
3. Configure your DNS to point to HuggingFace

Without a custom domain, Spaces are served at `huggingface.co/spaces/{user}/{space}` or directly at `{user}-{space}.hf.space`.

## Space Visibility

- **Public**: visible to everyone, discoverable on HuggingFace
- **Private**: only visible to you and collaborators (requires PRO or paid org plan)

## Spaces Configuration Reference

Full configuration options in `README.md` front matter:

```yaml
---
title: Space Title
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio          # gradio | streamlit | docker | static
sdk_version: "4.0.0"
app_file: app.py
app_port: 7860       # for Docker
hardware: cpu-basic  # hardware tier
pinned: false
license: mit
tags:
  - nlp
  - demo
suggested_hardware: t4-small  # recommended hardware for users who duplicate
---
```

## Secrets in Forked Spaces

When someone forks (duplicates) your Space:
- Secrets are **NOT** copied to the fork
- The forker must add their own secrets
- This is a security feature preventing credential leakage

## Waking Up Sleeping Spaces

Free CPU Spaces sleep after 48 hours of inactivity. Options:
- Upgrade to paid hardware (never sleeps)
- Use the HF API to wake the Space programmatically
- PRO users can pin Spaces to prevent sleeping

## References

- [Spaces Overview](https://huggingface.co/docs/hub/en/spaces-overview)
- [Spaces Configuration Reference](https://huggingface.co/docs/hub/spaces-config-reference)
- [Gradio Spaces Guide](https://huggingface.co/docs/hub/en/spaces-sdks-gradio)
- [HuggingFace Pricing](https://huggingface.co/pricing)
- [Spaces Launch Page](https://huggingface.co/spaces/launch)
