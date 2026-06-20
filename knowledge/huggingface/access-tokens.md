# HuggingFace Hub Access Tokens
> Source: https://huggingface.co/docs/hub/en/security-tokens
> Fetched: 2026-06-20

## Overview

HuggingFace User Access Tokens authenticate requests to the HuggingFace Hub API, the Inference API, and related services. Tokens are managed at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

## Token Types and Scopes

### Read Tokens
- Read-only access to all public repositories
- Read access to private repositories you have access to
- Cannot write or modify repositories
- Sufficient for most inference use cases with public models

### Write Tokens
- All read permissions, plus:
- Write access to repositories you have write permission on
- Can push models, datasets, update model cards
- Use when you need to programmatically upload or update content

### Fine-Grained Tokens (Recommended for Production)
Fine-grained tokens provide precise, least-privilege access. You can scope them to:
- **Specific repositories** (e.g., only one model)
- **Specific organizations**
- **Specific actions** (read, write, inference calls)

Key permission for inference:
- **"Make calls to Inference Providers"** — required for using the Inference Router (`router.huggingface.co/v1`)

Fine-grained tokens are strongly recommended in production because:
- If a token is leaked, exposure is limited to only the scoped resources
- Token activities are auditable
- Works well in CI/CD and deployment pipelines

> **Note**: If you create a fine-grained token scoped to an organization that requires administrator approval, the token enters a **Pending** state and cannot access that organization's resources until an administrator approves it.

## Creating a Token

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Choose token type:
   - "Read" — for downloading models and inference with public models
   - "Write" — for uploading/modifying content
   - "Fine-grained" — for production use with least-privilege scoping
4. For inference via the router: create a fine-grained token and enable **"Make calls to Inference Providers"**
5. Copy the token immediately — it is only shown once

## Setting HF_TOKEN

The standard environment variable for your HuggingFace token:

```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

This variable is automatically picked up by:
- `huggingface_hub` library
- HuggingFace CLI (`huggingface-cli`)
- Transformers library
- Diffusers library
- Many other HF ecosystem tools

## Using the huggingface_hub Library

### CLI Login

```bash
# Interactive login (prompts for token)
huggingface-cli login

# Or using the new hf auth command
hf auth login

# Check who is logged in
hf auth whoami
```

### Programmatic Login

```python
from huggingface_hub import login

# Interactive (prompts for token in terminal or shows widget in notebook)
login()

# Non-interactive (pass token directly)
login(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# In a Jupyter notebook (shows widget UI instead of terminal prompt)
from huggingface_hub import notebook_login
notebook_login()
```

### Token Storage and Cache

When you login via `login()` or CLI:
- Token is saved to `~/.cache/huggingface/token` (default)
- Location configurable via `HF_TOKEN_PATH` environment variable
- Token is also configured as a git credential for `git-lfs` operations
- Once stored, all `huggingface_hub` components use it automatically

### Checking Authentication

```python
from huggingface_hub import whoami

user_info = whoami()
print(user_info["name"])  # Your HF username
```

### Using Token Directly in Client

```python
from huggingface_hub import InferenceClient

client = InferenceClient(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
# or
client = InferenceClient(api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
```

## Token Scopes for Common Use Cases

| Use Case | Recommended Token Type | Key Permissions |
|----------|----------------------|-----------------|
| Run inference on public models | Read or Fine-grained | Make calls to Inference Providers |
| Download gated models | Fine-grained | Read + specific repo access |
| Upload model weights | Write or Fine-grained | Write access to your repos |
| CI/CD pipeline | Fine-grained | Only the needed resources |
| Local development | Read (easiest) | General read access |

## Gated Model Access

Some models (e.g., Llama, Gemma, FLUX.1-dev) are "gated" and require:
1. Visiting the model page on HuggingFace
2. Accepting the model's license/usage terms
3. Then your HF_TOKEN will have access to that model

Without accepting the terms, API calls to gated models return HTTP 403 even with a valid token.

## Enterprise Token Management

Enterprise Hub organizations can:
- Manage tokens centrally for all organization members
- Set organization-wide token policies
- Audit token usage across the organization

See: [https://huggingface.co/docs/hub/en/enterprise-hub-tokens-management](https://huggingface.co/docs/hub/en/enterprise-hub-tokens-management)

## References

- [User Access Tokens Docs](https://huggingface.co/docs/hub/en/security-tokens)
- [Token Settings](https://huggingface.co/settings/tokens)
- [huggingface_hub Authentication](https://huggingface.co/docs/huggingface_hub/en/package_reference/authentication)
- [Login and Logout Reference](https://huggingface.co/docs/huggingface_hub/package_reference/login)
- [Quickstart Guide](https://huggingface.co/docs/huggingface_hub/quick-start)
