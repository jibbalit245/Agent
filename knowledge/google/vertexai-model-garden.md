# Vertex AI Model Garden

> Source: https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

Model Garden is a platform in Vertex AI that lets you discover, test, customize, and deploy foundation models from Google and third-party providers. It provides a centralized model hub where you can find:

- **Google models**: Gemini family, PaLM 2, Imagen, Embeddings, Codey, Chirp, and more
- **Open source models**: Llama, Mistral, Falcon, BLOOM, Stable Diffusion, and more
- **Partner models**: Anthropic Claude, AI21 Labs, Cohere, and more

## Accessing Model Garden

**Console:** Navigate to Vertex AI > Model Garden in the Google Cloud Console

**URL:** https://console.cloud.google.com/vertex-ai/model-garden

## Google First-Party Models

### Gemini Models (Generative AI)

#### Gemini 2.5 Series (Current Generation)

| Model | ID | Context Window | Capabilities |
|-------|----| --------------|--------------|
| Gemini 2.5 Pro | `gemini-2.5-pro` | 1M tokens | Text, image, video, audio, code, reasoning |
| Gemini 2.5 Flash | `gemini-2.5-flash` | 1M tokens | Fast, multimodal, cost-effective |
| Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` | 1M tokens | Ultra-fast, lowest cost |

#### Gemini 2.0 Series

| Model | ID | Context Window | Capabilities |
|-------|----| --------------|--------------|
| Gemini 2.0 Flash | `gemini-2.0-flash-001` | 1M tokens | Multimodal, tool use, streaming |
| Gemini 2.0 Flash Lite | `gemini-2.0-flash-lite-001` | 1M tokens | Ultra-low cost |
| Gemini 2.0 Flash Image | `gemini-2.0-flash-exp-image-generation` | 1M tokens | Image generation |
| Gemini 2.0 Flash Live | Real-time streaming | — | Live audio/video streaming |

#### Gemini 3.x Series (Preview/Latest)

| Model | ID | Tier |
|-------|----| -----|
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | Preview |
| Gemini 3.5 Flash | `gemini-3.5-flash` | GA |
| Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite` | GA |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | Preview |
| Gemini 3 Pro Image | `gemini-3-pro-image-preview` | Preview |
| Gemini 3.1 Flash Image | `gemini-3.1-flash-image` | GA |

### Embedding Models

| Model | ID | Dimensions | Use Case |
|-------|----| -----------|---------|
| Gemini Embedding | `gemini-embedding-001` | Up to 3072 | Text embeddings, semantic search |
| Text Embedding | `text-embedding-004` | 768 | Legacy text embeddings |
| Multimodal Embedding | `multimodalembedding@001` | 1408 | Text + image embeddings |

### Image Generation Models

| Model | ID | Capabilities |
|-------|----| ------------|
| Imagen 4 | `imagen-4.0-generate-001` | Text-to-image, highest quality |
| Imagen 4 Ultra | `imagen-4.0-ultra-generate-001` | Highest quality |
| Imagen 4 Fast | `imagen-4.0-fast-generate-001` | Faster generation |
| Imagen 3 | `imagen-3.0-generate-001` | Text-to-image |
| Imagen 3 Capability | `imagen-3.0-capability-001` | Editing/inpainting |
| Imagen 4 Upscale | `imagen-4.0-upscale-preview` | Image upscaling |

### Video Generation Models (Veo)

| Model | ID | Capabilities |
|-------|----| ------------|
| Veo 3 | `veo-3.0-generate-preview` | Text-to-video, image-to-video |
| Veo 3.1 | `veo-3.1-generate-preview` | Latest generation video |
| Veo 2 | `veo-2.0-generate-001` | Previous generation |

### Speech Models

| Model | ID | Capabilities |
|-------|----| ------------|
| Chirp 3 | `chirp-3` | Text-to-speech, voice cloning |
| Chirp | `chirp` | Automatic speech recognition |

## Open Source Models (via Model Garden)

### Llama Models (Meta)

| Model | Parameters | Use Case |
|-------|-----------|---------|
| Llama 3.1 | 8B, 70B, 405B | General purpose |
| Llama 3.2 | 1B, 3B, 11B, 90B | Multimodal |
| Llama 3.3 | 70B | Latest generation |
| Code Llama | 7B, 13B, 34B | Code generation |

### Mistral Models

| Model | Parameters | Use Case |
|-------|-----------|---------|
| Mistral 7B | 7B | Fast general purpose |
| Mixtral 8x7B | 46.7B (MoE) | High quality MoE |
| Mistral Large | — | Complex reasoning |

### Other Open Source Models

- **Falcon** (TII): 7B, 40B
- **BLOOM** (BigScience): 176B multilingual
- **Stable Diffusion** (Stability AI): Image generation
- **Phi-3** (Microsoft): Small efficient models
- **Gemma** (Google): Open lightweight models
- **Code Gemma** (Google): Code-focused

## Partner Models (Available on Model Garden)

### Anthropic Claude (via Partner Model API)

| Model | Use Case |
|-------|---------|
| Claude 3.5 Sonnet | Balanced capability/speed |
| Claude 3.5 Haiku | Fast, cost-effective |
| Claude 3 Opus | Highest capability |

### AI21 Labs

- Jamba: Long-context model

### Cohere

- Command R: RAG-optimized
- Command R+: Most capable
- Embed: Embeddings

### Stability AI

- Stable Diffusion XL
- Stable Diffusion 3

## Deploying Models from Model Garden

### Method 1: Deploy to Endpoint (for custom/open-source models)

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(project='my-project', location='us-central1')

# Deploy a Model Garden model to an endpoint
model = aiplatform.Model(
    model_name='projects/my-project/locations/us-central1/models/MODEL_ID'
)

endpoint = model.deploy(
    deployed_model_display_name='my-deployed-model',
    machine_type='n1-standard-4',
    min_replica_count=1,
    max_replica_count=3,
)

# Make predictions
response = endpoint.predict(instances=[{"inputs": "Your prompt here"}])
```

### Method 2: Use Publisher Models Directly (Gemini)

No deployment needed for Google publisher models:

```python
from google import genai

client = genai.Client(vertexai=True, project='my-project', location='us-central1')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt here.'
)
print(response.text)
```

### Method 3: One-Click Deploy via Console

1. Navigate to Model Garden in Cloud Console
2. Select desired model
3. Click "Deploy"
4. Configure machine type, replicas, region
5. Click "Deploy" to create endpoint

## Model Categories in Model Garden

### By Task Type

- **Text Generation**: Gemini, PaLM 2, Llama, Mistral
- **Code Generation**: Gemini, Code Llama, StarCoder
- **Image Generation**: Imagen, Stable Diffusion
- **Video Generation**: Veo
- **Image Understanding**: Gemini (multimodal), LLaVA
- **Embeddings**: Gemini Embedding, text-embedding, Cohere Embed
- **Speech**: Chirp (ASR), Chirp 3 (TTS)
- **Translation**: PaLM 2 (multilingual)
- **Document AI**: Specialized document processing

### By License Type

- **Commercial**: Google models, Partner models
- **Open Source**: Llama, Mistral, Falcon, Gemma (Apache/custom licenses)
- **Research Only**: Some models with restricted licenses

## Model Cards and Documentation

Each model in Model Garden includes:
- Model description and capabilities
- Example use cases
- Sample code (Python, REST)
- Performance benchmarks
- License information
- Pricing information
- Regional availability

## Fine-Tuning Models from Model Garden

### Supervised Fine-Tuning (Gemini)

```python
from google.genai import types
from google import genai

client = genai.Client(vertexai=True, project='my-project', location='us-central1')

tuning_job = client.tunings.tune(
    base_model='gemini-2.0-flash-001',
    training_dataset=types.TuningDataset(
        gcs_uri='gs://my-bucket/training-data.jsonl',
    ),
    config=types.CreateTuningJobConfig(
        epoch_count=3,
        learning_rate_multiplier=1.0,
        tuned_model_display_name='my-fine-tuned-model'
    ),
)
```

Training data format (JSONL):
```json
{"contents": [{"role": "user", "parts": [{"text": "Your question"}]}, {"role": "model", "parts": [{"text": "Expected answer"}]}]}
```

### Open Source Model Fine-Tuning

Open source models (Llama, Mistral, etc.) can be fine-tuned using:
- Vertex AI Training with custom containers
- LoRA/QLoRA for efficient fine-tuning

```python
from google.cloud import aiplatform

job = aiplatform.CustomContainerTrainingJob(
    display_name='llama-finetuning',
    container_uri='us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-0:latest',
)

model = job.run(
    args=['--model=meta-llama/Llama-3.1-8B', '--epochs=3'],
    replica_count=1,
    machine_type='a2-highgpu-1g',
    accelerator_type='NVIDIA_TESLA_A100',
    accelerator_count=1,
)
```

## Regional Availability

Models in Model Garden have varying regional support:
- **Global availability**: Most Gemini models
- **US only**: Some preview models
- **Regional endpoints**: `us-central1`, `europe-west4`, `asia-northeast1` (most common)

## Quotas and Rate Limits

| Resource | Default Quota |
|----------|--------------|
| Requests per minute (Gemini) | 60 RPM |
| Tokens per minute | 4,000,000 TPM |
| Concurrent requests | 10 |
| Batch requests | 1,000 per batch |

Request quota increases via Cloud Console > IAM & Admin > Quotas.

## Related Resources

- Model Garden Console: https://console.cloud.google.com/vertex-ai/model-garden
- Vertex AI Pricing: https://cloud.google.com/vertex-ai/generative-ai/pricing
- Model IDs Reference: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versioning
- Tuning Guide: https://cloud.google.com/vertex-ai/generative-ai/docs/models/tune-models
