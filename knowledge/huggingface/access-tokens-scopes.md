# HuggingFace Access Tokens and Scopes
> Sources: https://huggingface.co/docs/hub/en/security-tokens, https://github.com/huggingface/hub-docs/blob/main/docs/hub/security-tokens.md, https://sfailabs.com/guides/how-to-get-huggingface-api-token, https://huggingface.co/docs/hub/programmatic-user-access-control, https://huggingface.co/docs/hub/enterprise-tokens-management, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

HuggingFace User Access Tokens authenticate all HuggingFace services:
- Hub API (download/upload models, datasets, Spaces)
- Inference API (serverless) and Inference Router
- `huggingface_hub` Python library
- HuggingFace CLI (`huggingface-cli` / `hf`)
- TGI and other self-hosted services

Managed at: **https://huggingface.co/settings/tokens**

---

## Token Types

### 1. Read Tokens
- Download public repositories
- Read private repositories you have access to
- Run inference on public models
- **Cannot:** write, create repos, upload files

### 2. Write Tokens
- Everything read tokens can, plus:
- Push files to your repositories
- Create new repositories
- Update model cards and metadata
- **Best for:** training pipelines that push checkpoints

### 3. Fine-Grained Tokens (Recommended for Production)
- Precisely scoped — define exactly what the token can access
- Limit to specific repositories, organizations, actions
- If leaked: blast radius is limited to scoped resources
- Auditable: activity logs per token
- May require administrator approval for org-scoped tokens
- **Best for:** production deployments, CI/CD pipelines

#### Fine-grained permission scopes:
| Scope | Description |
|-------|-------------|
| `repo.content.read` | Download files from repositories |
| `repo.content.write` | Upload/modify files in repositories |
| `inference.serverless.write` | Make calls to Inference Providers/Router |
| `org.read` | Read organization info |
| `org.write` | Manage organization members |
| `collections.read` | Read Hub collections |
| `collections.write` | Manage Hub collections |
| `webhook.read` | List webhooks |
| `webhook.write` | Create/delete webhooks |
| `user.read` | Read user profile info |
| `billing.read` | View billing info |

**Key scope for inference:** `inference.serverless.write` — required for using the Inference Router (`router.huggingface.co/v1`)

---

## How to Create a Token

### Via Web UI
1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Enter a descriptive name (e.g., "prod-inference-key", "dev-laptop")
4. Select type: **Read / Write / Fine-grained**
5. For fine-grained: configure repo access and permission scopes
6. Click **"Generate a token"**
7. **Copy immediately** — shown only once

### Via CLI
```bash
# Interactive login (prompts for token, saves locally)
huggingface-cli login

# Newer command
hf auth login

# Check who you're logged in as
huggingface-cli whoami
hf auth whoami
```

---

## Setting HF_TOKEN

The standard environment variable — automatically used by all HuggingFace libraries:

```bash
# Shell export
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# .env file
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Docker container
docker run -e HF_TOKEN=$HF_TOKEN my-image

# Python (set before importing HF libraries)
import os
os.environ["HF_TOKEN"] = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Libraries that automatically pick up `HF_TOKEN`:
- `huggingface_hub` — InferenceClient, HfApi, download functions
- `transformers` — `from_pretrained()` for gated models
- `diffusers` — `from_pretrained()` for FLUX and other gated models
- `datasets` — `load_dataset()` for gated datasets
- TGI Docker container (`-e HF_TOKEN=$HF_TOKEN`)

---

## Programmatic Login (huggingface_hub)

```python
from huggingface_hub import login, logout, whoami, notebook_login

# Interactive login (terminal prompt or notebook widget)
login()

# Non-interactive (for scripts/CI/CD)
login(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Non-interactive, no token storage (just for this Python session)
login(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", add_to_git_credential=False)

# Jupyter notebook (shows widget)
notebook_login()

# Check current auth
info = whoami()
print(info["name"])   # HF username
print(info["email"])  # registered email

# Log out (removes stored token from disk)
logout()
```

**Token storage location after login():**
```
~/.cache/huggingface/token
```

Custom location:
```bash
export HF_TOKEN_PATH=/custom/path/to/token
```

---

## Using Tokens Directly in Code (without login)

```python
from huggingface_hub import InferenceClient, HfApi, hf_hub_download, snapshot_download

# InferenceClient
client = InferenceClient(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
# also accepted as:
client = InferenceClient(api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# HfApi
api = HfApi(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Single file download
path = hf_hub_download(
    repo_id="meta-llama/Llama-3.1-8B",
    filename="config.json",
    token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)

# Full model download
local_dir = snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B",
    token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    local_dir="./models/llama",
)

# OpenAI client pointed at HF router
from openai import OpenAI
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
```

---

## Gated Model Access

Some models require accepting terms before your token works.

**Common gated models:**
- `meta-llama/Llama-3.1-8B-Instruct` and all Llama family
- `google/gemma-2b` and Gemma family
- `black-forest-labs/FLUX.1-dev`
- `mistralai/Mistral-7B-v0.1` (some variants)

**Process:**
1. Go to the model page: e.g., `https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct`
2. Click "Request access" or "Agree to license terms"
3. Fill out form (name, organization, intended use)
4. Most models: **automatic approval** (seconds to minutes)
5. Some research models: **manual review** (hours to days)
6. Once approved, your `HF_TOKEN` has access

**Without access — HTTP 403 error:**
```
"Access to model meta-llama/Llama-3.1-8B-Instruct is restricted.
You must have access to it and be authenticated to access it."
```

---

## Enterprise Token Management

For Team/Enterprise organizations:

```python
from huggingface_hub import HfApi

api = HfApi(token="hf_admin_token")

# List pending access requests for gated model
pending = api.list_pending_access_requests(repo_id="myorg/gated-model")

# Approve access
api.accept_access_request(repo_id="myorg/gated-model", username="user123")

# Reject access
api.reject_access_request(repo_id="myorg/gated-model", username="user123")

# Grant direct access (bypass application process)
api.grant_access(repo_id="myorg/gated-model", username="trusted-user")
```

---

## Security Best Practices

1. **Never commit tokens to git** — use env vars, `.env` files in `.gitignore`
2. **Use fine-grained tokens in production** — limit blast radius
3. **One token per system** — separate tokens for each deployment/machine
4. **Rotate regularly** — delete old tokens from settings
5. **Scope to minimum needed** — download-only? Use a read token
6. **Monitor activity** — check billing page for unexpected usage

---

## References

- [User Access Tokens Docs](https://huggingface.co/docs/hub/en/security-tokens)
- [Token Settings Page](https://huggingface.co/settings/tokens)
- [Programmatic User Access Control](https://huggingface.co/docs/hub/programmatic-user-access-control)
- [Enterprise Token Management](https://huggingface.co/docs/hub/enterprise-tokens-management)
- [huggingface_hub Login Reference](https://huggingface.co/docs/huggingface_hub/package_reference/login)
