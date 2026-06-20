# Vertex AI Model Garden  
> Source: https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models  
> Fetched: 2026-06-20

## Overview

Vertex AI Model Garden is a catalog of 200+ models available through Google Cloud's Vertex AI platform. It includes:
- Google's own Gemini models
- Open-source models (Llama, Mistral, Gemma, etc.)
- Partner/third-party models

Models can be accessed in two ways:
1. **Model-as-a-Service (MaaS)** — Serverless, pay-per-token, no infrastructure to manage
2. **Self-Deploy** — Deploy to a dedicated endpoint on your own compute (GPU instances)

## Available Model Families

### Google Models
- Gemini 2.5 Pro, Flash, Flash-Lite
- Gemma 3 (open weights, can be self-deployed)

### Meta Llama
- Llama 4 (Scout, Maverick) — generally available as MaaS on Vertex AI
- Llama 3.3 70B, Llama 3.1 405B
- Access: MaaS (pay-per-token) or self-deploy

### Mistral AI
- Mistral Large 24.11
- Codestral 25.01 (code-focused)
- Mistral NeMo, Mistral 7B
- Access: MaaS (pay-per-token) or self-deploy

### Other Notable Models
- Anthropic Claude (via Vertex AI partner program)
- AI21 Jamba
- Falcon
- Various Hugging Face models via custom deployment

## Model-as-a-Service (MaaS) Usage

MaaS models are serverless — you pay only for prediction requests with no infrastructure overhead.

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="your-project", location="us-central1")

# Using Llama 4 via MaaS
model = GenerativeModel("meta/llama-4-scout-17b-16e-instruct-maas")
response = model.generate_content("What is the meaning of life?")
print(response.text)
```

For Mistral via MaaS (uses OpenAI-compatible endpoint):
```python
import anthropic  # or use requests/httpx directly

# Mistral models expose an OpenAI-compatible endpoint
from openai import OpenAI

client = OpenAI(
    base_url=f"https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/endpoints/openapi/chat/completions",
    api_key="Bearer " + access_token  # from gcloud auth print-access-token
)
```

## Self-Deploy via Dedicated Endpoints

For self-deployment, you provision a Vertex AI endpoint with a specific GPU instance type.

### Instance Types for Model Deployment

| Instance | GPU | VRAM | Use Case |
|----------|-----|------|---------|
| `g2-standard-4` | 1x NVIDIA L4 | 24 GB | Small models (7B) |
| `g2-standard-12` | 1x NVIDIA L4 | 24 GB | Small models |
| `a2-highgpu-1g` | 1x NVIDIA A100 40GB | 40 GB | Medium models (13B-34B) |
| `a2-highgpu-2g` | 2x NVIDIA A100 40GB | 80 GB | Large models (70B) |
| `a2-highgpu-4g` | 4x NVIDIA A100 40GB | 160 GB | Very large models |
| `a2-ultragpu-1g` | 1x NVIDIA A100 80GB | 80 GB | Large models |
| `a3-highgpu-8g` | 8x NVIDIA H100 80GB | 640 GB | Largest models (405B) |

### Deploy a Model from Model Garden (Console)

1. Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. Search for the model (e.g., "Llama 3.3")
3. Click "Deploy" — choose instance type and region
4. Wait for endpoint to become active (5-15 minutes)
5. Get the endpoint ID and use it for predictions

### Deploy via Python SDK

```python
from google.cloud import aiplatform

aiplatform.init(project="your-project", location="us-central1")

# Deploy a model (example: Llama 3.3 70B)
model = aiplatform.Model(model_name="publishers/meta/models/llama-3-3-70b-instruct-maas")

endpoint = model.deploy(
    machine_type="a2-highgpu-2g",
    accelerator_type="NVIDIA_TESLA_A100",
    accelerator_count=2,
    min_replica_count=1,
    max_replica_count=1,
    traffic_percentage=100,
)

# Make predictions
response = endpoint.predict(instances=[{"prompt": "Hello, world!"}])
```

## Pricing

### MaaS Pricing
- Pay per token (input + output)
- Llama 4: priced per prediction request (infrastructure included)
- Mistral Large: pay-as-you-go
- Varies by model — check [Vertex AI pricing page](https://cloud.google.com/vertex-ai/pricing)

### Self-Deploy Pricing
- You pay for the compute instance while the endpoint is running
- Typical costs:
  - `g2-standard-4` (L4): ~$0.70/hour
  - `a2-highgpu-1g` (A100 40GB): ~$3.67/hour
  - `a2-highgpu-2g` (2x A100): ~$7.34/hour
  - `a3-highgpu-8g` (8x H100): ~$40+/hour
- Endpoints incur charges even when idle — delete when not in use

## Key Considerations

1. **Region availability**: Not all models are available in all regions. `us-central1` has the broadest model availability.
2. **MaaS quota**: New projects may need quota increases for MaaS models via Google Cloud support.
3. **Latency**: MaaS has cold-start latency; dedicated endpoints have consistent latency.
4. **Cost control**: Self-deploy endpoints run 24/7 until deleted — always monitor and delete unused endpoints.

## Useful Commands

```bash
# List available models
gcloud ai models list --region=us-central1

# List your deployed endpoints
gcloud ai endpoints list --region=us-central1

# Delete an endpoint (stops billing)
gcloud ai endpoints delete ENDPOINT_ID --region=us-central1
```

## References

- [Model Garden Console](https://console.cloud.google.com/vertex-ai/model-garden)
- [Llama 4 on Vertex AI Blog](https://developers.googleblog.com/llama-4-ga-maas-vertex-ai/)
- [Mistral AI Models on Vertex](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/partner-models/mistral)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
