# RunPod Environment Variables and Secrets
> Source: https://docs.runpod.io/pods/configuration/environment-variables, https://docs.runpod.io/pods/templates/secrets, https://www.runpod.io/articles/guides/security-feature-priority-ai-hosting
> Fetched: 2026-06-20

## Overview

RunPod provides two mechanisms for passing configuration to pods and serverless workers:

1. **Environment Variables**: Plain-text key-value pairs set at pod/endpoint creation
2. **Secrets**: Encrypted strings managed separately, injected at runtime

Never bake API keys or credentials directly into Docker images. Use secrets or environment variables injected at runtime.

## Environment Variables in Pods

### Setting via Web Console

When creating or editing a pod:
1. Scroll to **Environment Variables** section
2. Add key-value pairs (e.g., `MODEL_NAME=mistral-7b`, `HUGGING_FACE_HUB_TOKEN=hf_xxx`)
3. These appear as standard environment variables inside the container

### Setting via Python SDK

```python
import runpod

pod = runpod.create_pod(
    name="inference-pod",
    image_name="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
    gpu_type_id="NVIDIA GeForce RTX 4090",
    cloud_type="COMMUNITY",
    gpu_count=1,
    volume_in_gb=20,
    container_disk_in_gb=20,
    env={
        "MODEL_NAME": "mistralai/Mistral-7B-Instruct-v0.3",
        "HF_TOKEN": "hf_your_token_here",
        "CUDA_VISIBLE_DEVICES": "0",
        "TRANSFORMERS_CACHE": "/workspace/models"
    }
)
```

### Setting via Docker `-e` flag (for local testing)

```bash
docker run --gpus all \
  -e RUNPOD_API_KEY="your_api_key" \
  -e MODEL_NAME="mistral-7b" \
  -e HF_TOKEN="hf_xxx" \
  myimage:latest
```

### Accessing in Python

```python
import os

model_name = os.environ.get("MODEL_NAME", "default-model")
hf_token = os.environ.get("HF_TOKEN")
```

## RunPod Secrets Manager

Secrets are **encrypted strings** stored in your RunPod account and injected into pods/serverless at runtime as environment variables. They are not visible in the console UI after creation.

### Creating Secrets

1. Go to **Settings > Secrets** in the RunPod console
2. Click **Create Secret**
3. Enter:
   - **Name**: The environment variable name (e.g., `OPENAI_API_KEY`)
   - **Value**: The secret value (encrypted at rest)
4. Click **Create**

### Using Secrets in Pods

When creating a pod template or pod:
1. In the **Environment Variables** section, click the **key icon** (secret selector)
2. Choose a secret from your account
3. The secret is injected as an env var with its name at runtime

Via API, reference secrets by name in the `secrets` field (varies by API version — check current RunPod docs).

### Using Secrets in Serverless Endpoints

In the **Serverless Endpoint** settings:
1. Go to **Environment Variables**
2. Click the key icon to choose a stored secret
3. The secret name becomes the env var name inside the worker

## System-Provided Environment Variables

RunPod injects these automatically into every pod and serverless worker:

| Variable | Description |
|----------|-------------|
| `RUNPOD_POD_ID` | Unique ID of the current pod |
| `RUNPOD_GPU_COUNT` | Number of GPUs in the pod |
| `RUNPOD_PUBLIC_IP` | Public IP of the pod |
| `RUNPOD_TCP_PORT_22` | External SSH port (if TCP 22 is exposed) |
| `RUNPOD_POD_HOSTNAME` | Hostname for the pod |
| `RUNPOD_API_KEY` | Your RunPod API key (if set as a secret/env var) |

For serverless workers, additional variables:
| Variable | Description |
|----------|-------------|
| `RUNPOD_WEBHOOK_GET_JOB` | Internal job fetch URL |
| `RUNPOD_WEBHOOK_POST_OUTPUT` | Internal result post URL |
| `RUNPOD_TASK_ID` | Current job/task ID |

## RUNPOD_API_KEY

Your API key is used to authenticate against the RunPod API and SDK.

### Where to find it

**Settings > API Keys > Create API Key** in the RunPod console.

### How to use it

```python
import runpod
import os

# Method 1: Set directly
runpod.api_key = "rpa_your_key_here"

# Method 2: From environment variable (recommended)
runpod.api_key = os.environ.get("RUNPOD_API_KEY")
```

In REST API calls:
```bash
curl -H "Authorization: Bearer $RUNPOD_API_KEY" \
     https://api.runpod.io/v2/{endpoint_id}/run \
     -d '{"input": {"prompt": "Hello"}}'
```

### Best practices for API key management

1. **Never hardcode** API keys in source files — use env vars or secrets manager
2. **Create separate keys** for dev, staging, production
3. **Rotate keys** periodically; revoke old keys in the RunPod console
4. **Add to .gitignore** any files containing keys (`.env`, config files)

```bash
# .env file (do not commit)
RUNPOD_API_KEY=rpa_your_key_here
HF_TOKEN=hf_your_token_here
OPENAI_API_KEY=sk-your_key_here
```

```python
# load_env.py
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

runpod.api_key = os.environ["RUNPOD_API_KEY"]
```

## Environment Variables in Serverless Workers

Set environment variables for a serverless endpoint via the console under **Serverless > Your Endpoint > Edit**. They are available inside `handler.py` via `os.environ`.

### Example: HuggingFace token in worker

```python
# handler.py
import os
import runpod
from huggingface_hub import login

# Authenticate at startup using injected env var
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    login(token=hf_token)

def handler(job):
    # HF is now authenticated for downloading private models
    ...

runpod.serverless.start({"handler": handler})
```

## Security Notes

- Environment variables are visible to anyone with pod/endpoint access in your account
- Secrets provide an extra layer: values are encrypted and not displayed in UI after creation
- Secrets in team accounts can be scoped to specific members
- For highly sensitive values (payment keys, private model weights tokens), use secrets over plain env vars
- Container disk is ephemeral — environment variables are not persisted across pod restarts unless re-injected
