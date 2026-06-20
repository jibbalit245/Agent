# Replicate Models

> Source: https://replicate.com/docs/topics/models
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## What is a Model?

A model on Replicate is a machine learning algorithm packaged with its code, weights, and dependencies. Models have:
- An **owner** (user or organization)
- A **name** (unique per owner)
- One or more **versions** (immutable snapshots)

Model identifier format: `owner/name` or `owner/name:version_hash`

## Model Types

### Public Models
- Discoverable and runnable by anyone
- Hosted in Replicate's model registry
- 50,000+ available models

### Private Models
- Only visible to the owner
- Useful for proprietary models or during development

### Official Models
- Verified, maintained models from leading AI companies
- Simplified pricing (per output image, token, etc.)
- Examples: FLUX, Stable Diffusion, Llama, Whisper

## Browsing Models

- **Explore**: https://replicate.com/explore
- **Search by category**: text-to-image, language, audio, video
- **Collections**: curated lists of related models

## Getting Model Information

### Python

```python
import replicate

# Get a model
model = replicate.models.get("stability-ai/sdxl")
print(model.name)
print(model.description)
print(model.run_count)
print(model.url)

# Get latest version
version = model.latest_version
print(version.id)
print(version.created_at)

# Get all versions
versions = model.versions.list()
for v in versions:
    print(v.id, v.created_at)

# Get a specific version
specific_version = model.versions.get("39ed52f2...")
```

### HTTP API

```bash
# Get model
curl -s \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/stability-ai/sdxl

# List versions
curl -s \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/stability-ai/sdxl/versions

# Get specific version
curl -s \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/stability-ai/sdxl/versions/39ed52f2...
```

## Running Models

### Simple Run

```python
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "an astronaut on the moon"}
)
```

### With Specific Version

```python
output = replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={"prompt": "an astronaut on the moon"}
)
```

### Exploring Model Schema

```python
import replicate

model = replicate.models.get("stability-ai/sdxl")
version = model.latest_version

# OpenAPI schema defines all input/output parameters
schema = version.openapi_schema
inputs = schema["components"]["schemas"]["Input"]["properties"]

for name, props in inputs.items():
    print(f"{name}: {props.get('description', 'No description')}")
```

## Creating Models

### Via Python

```python
import replicate

model = replicate.models.create(
    owner="your-username",
    name="my-custom-model",
    description="My custom ML model",
    visibility="public",  # "public" or "private"
    hardware="gpu-a40-large",
    github_url="https://github.com/you/your-model",
    paper_url="https://arxiv.org/abs/...",
    license_url="https://opensource.org/licenses/MIT"
)

print(model.url)  # https://replicate.com/your-username/my-custom-model
```

### Available Hardware for Models

```python
hardware_list = replicate.hardware.list()
# Returns list of available hardware options:
# - cpu
# - gpu-t4-nano
# - gpu-l40s-medium
# - gpu-a100-large
# - gpu-h100-medium
```

## Model Versions

Each time you push a new version of your model via Cog, a new version is created with a unique SHA256 hash.

```python
# List all versions of a model
model = replicate.models.get("your-username/your-model")
versions = model.versions.list()

for version in versions:
    print(version.id)
    print(version.created_at)
    print(version.cog_version)
```

## Official Models

Official models are curated, maintained models with simplified pricing:

### Text-to-Image

| Model | Owner | Description |
|-------|-------|-------------|
| `black-forest-labs/flux-schnell` | Black Forest Labs | Fast FLUX image generation |
| `black-forest-labs/flux-dev` | Black Forest Labs | High-quality FLUX image generation |
| `black-forest-labs/flux-1.1-pro` | Black Forest Labs | Professional FLUX model |
| `stability-ai/stable-diffusion-3.5-large` | Stability AI | Latest Stable Diffusion |
| `stability-ai/sdxl` | Stability AI | Stable Diffusion XL |

### Language Models

| Model | Owner | Description |
|-------|-------|-------------|
| `meta/meta-llama-3-70b-instruct` | Meta | Llama 3 70B instruction-tuned |
| `meta/meta-llama-3-8b-instruct` | Meta | Llama 3 8B instruction-tuned |
| `mistralai/mistral-7b-instruct-v0.2` | Mistral AI | Mistral 7B instruction-tuned |

### Audio & Video

| Model | Owner | Description |
|-------|-------|-------------|
| `openai/whisper` | OpenAI | Speech-to-text transcription |
| `anotherjesse/zeroscope-v2-xl` | Community | Text-to-video generation |

## Fine-tuning (Training)

### Using a Model as Training Destination

```python
# First create a model to receive the fine-tuned weights
destination_model = replicate.models.create(
    owner="your-username",
    name="my-fine-tuned-flux",
    visibility="private",
    hardware="gpu-a100-large"
)

# Start training
training = replicate.trainings.create(
    model="black-forest-labs/flux-dev",
    version="latest-version-id",
    input={
        "input_images": "https://example.com/my-training-images.zip",
        "steps": 1000,
        "lora_rank": 16,
        "optimizer": "adamw8bit",
        "batch_size": 1,
        "resolution": "512,768,1024",
        "autocaption": True,
        "trigger_word": "TOK"
    },
    destination=f"your-username/my-fine-tuned-flux",
    webhook="https://example.com/training-complete"
)

print(training.id)
print(training.status)
training.wait()
print(training.output)  # Contains the trained model version
```

## Models as Secrets

Models can have attached secrets for private data or API keys used during inference:

```python
# Secrets are attached to model versions at push time via Cog
# Environment variable in cog.yaml:
# predict: predict.py:Predictor
# environment:
#   MY_SECRET: $MY_SECRET
```

## Pagination

```python
# Iterate through all public models
for page in replicate.paginate(replicate.models.list):
    for model in page.results:
        print(f"{model.owner}/{model.name}: {model.run_count} runs")
```

## Model Collections

```python
# List all collections
for page in replicate.paginate(replicate.collections.list):
    for collection in page:
        print(collection.slug, "-", collection.description)

# Get models in a specific collection
collection = replicate.collections.get("text-to-image")
for model in collection.models:
    print(f"{model.owner}/{model.name}")
```

Available collection slugs include:
- `text-to-image`
- `image-to-text`
- `language-models`
- `audio-generation`
- `video-generation`
- `image-upscaling`
- `image-restoration`
- `vision-models`
