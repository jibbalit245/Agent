# Vertex AI Gemini  
> Source: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal  
> Fetched: 2026-06-20

## Overview

Vertex AI is Google Cloud's enterprise ML platform. It provides access to Gemini models (and many open-source models via Model Garden) with enterprise-grade features: IAM access control, VPC networking, audit logging, regional data residency, and SLAs.

Unlike the Gemini API (AI Studio), Vertex AI requires a Google Cloud project, a billing account, and uses OAuth/service accounts rather than simple API keys.

## Key Differences from Google AI Studio

| Aspect | Gemini API (AI Studio) | Vertex AI |
|--------|----------------------|-----------|
| Auth | `GEMINI_API_KEY` | OAuth / ADC / Service Account |
| GCP project required | No | Yes |
| Free tier | Yes | No (pay-per-use) |
| Enterprise IAM | No | Yes |
| VPC / private networking | No | Yes |
| Audit logging | No | Yes |
| SLA | No | Yes |
| Model Garden | No | Yes (200+ models) |
| Fine-tuning | Limited | Full |

## Prerequisites

1. A Google Cloud project with billing enabled
2. Vertex AI API enabled: `gcloud services enable aiplatform.googleapis.com`
3. Authenticated credentials (see Authentication section)

## Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"   # or europe-west1, asia-northeast1, etc.
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"  # if using key file
```

## Installation

```bash
pip install google-cloud-aiplatform
# Or the newer unified SDK:
pip install google-genai
```

## Method 1: Using the `vertexai` SDK (classic)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize with project and location
vertexai.init(project="your-project-id", location="us-central1")

# Or use environment variables
# export GOOGLE_CLOUD_PROJECT=your-project-id
# export GOOGLE_CLOUD_LOCATION=us-central1
vertexai.init()  # reads from env vars

model = GenerativeModel("gemini-2.0-flash-001")
response = model.generate_content("Explain quantum computing")
print(response.text)
```

## Method 2: Using the unified `google-genai` SDK with Vertex AI backend

```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project="your-project-id",
    location="us-central1"
)

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Explain quantum computing"
)
print(response.text)
```

## Authentication Options

### Option 1: Application Default Credentials (ADC) — Recommended for local dev

```bash
gcloud auth application-default login
```

This creates a credentials file at `~/.config/gcloud/application_default_credentials.json`. Client libraries pick this up automatically.

### Option 2: Service Account JSON Key

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Option 3: Service Account in Code

```python
from google.oauth2 import service_account
import vertexai

credentials = service_account.Credentials.from_service_account_file(
    "/path/to/key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

vertexai.init(
    project="your-project-id",
    location="us-central1",
    credentials=credentials
)
```

## Supported Regions (Location Parameter)

Common choices:
- `us-central1` — Iowa (most models available here)
- `us-east4` — Northern Virginia
- `europe-west4` — Netherlands
- `asia-northeast1` — Tokyo

Not all models are available in all regions. Check availability in the [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations).

## Multimodal Example

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

vertexai.init(project="your-project", location="us-central1")
model = GenerativeModel("gemini-2.0-flash-001")

# Image + text
image_part = Part.from_uri(
    "gs://your-bucket/image.jpg",
    mime_type="image/jpeg"
)
response = model.generate_content(["Describe this image:", image_part])
print(response.text)
```

## Streaming

```python
for chunk in model.generate_content("Tell me a story", stream=True):
    print(chunk.text, end="", flush=True)
```

## Enabling Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com  # if using GCS for multimodal
```

## References

- [Vertex AI Generative AI Quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal)
- [Vertex AI Authentication](https://cloud.google.com/vertex-ai/docs/authentication)
- [python-aiplatform GitHub](https://github.com/googleapis/python-aiplatform)
- [Vertex AI Locations](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)
