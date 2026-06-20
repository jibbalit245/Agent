# Migrating from Google AI Studio to Vertex AI

> Source: https://cloud.google.com/vertex-ai/generative-ai/docs/migrate/migrate-google-ai
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base and PyPI google-genai documentation.
> Fetched: 2026-06-20

## Overview

Google offers two platforms for accessing Gemini models:

1. **Google AI / Gemini Developer API** (formerly Google AI Studio) - For prototyping and personal projects
2. **Vertex AI (Gemini Enterprise Agent Platform)** - For production applications on Google Cloud

The `google-genai` SDK (v1.0+) supports **both** platforms with the same API surface, making migration straightforward.

## Platform Comparison

| Feature | Gemini Developer API | Vertex AI |
|---------|---------------------|-----------|
| Authentication | API Key | Google Cloud IAM (OAuth 2.0) |
| Access | Direct API key | Google Cloud project required |
| Pricing | Pay-per-token (Gemini pricing) | Google Cloud pricing |
| Free tier | Yes (limited) | $300 free credit for new accounts |
| Data residency | Limited control | Full control (regional endpoints) |
| Enterprise SLA | No | Yes |
| VPC/Private connectivity | No | Yes |
| CMEK (Customer-managed keys) | No | Yes |
| Audit logging | Basic | Full Cloud Audit Logs |
| Model tuning | Limited | Full support |
| Model Garden | Limited | Full access |
| Batch predictions | Limited | Full support (BQ, GCS) |
| MLOps features | No | Full (pipelines, monitoring, etc.) |
| Support | Self-service | Enterprise support options |
| Compliance | Basic | HIPAA, SOC 2, ISO 27001, etc. |
| Organization/Billing | Not required | Google Cloud organization |

## When to Use Each Platform

### Use Gemini Developer API When:
- Building personal projects or prototypes
- Testing and experimentation
- You don't have a Google Cloud account
- You need the quickest setup (just an API key)
- Cost is a primary concern for low-volume use

### Use Vertex AI When:
- Building production applications
- You need enterprise SLAs and support
- You require data residency controls
- You need VPC/private connectivity
- You need full audit logging
- You're already on Google Cloud
- You need MLOps capabilities (pipelines, monitoring)
- You need compliance certifications (HIPAA, etc.)
- You need customer-managed encryption keys (CMEK)

## The google-genai SDK (Unified API)

The `google-genai` Python SDK provides the same interface for both platforms. Migration requires changing only the client initialization:

### Gemini Developer API Client

```python
from google import genai

# Using API key
client = genai.Client(api_key='GEMINI_API_KEY')

# Or via environment variable
# export GEMINI_API_KEY=your-key-here
# export GOOGLE_API_KEY=your-key-here
client = genai.Client()
```

### Vertex AI Client

```python
from google import genai

# Explicit initialization
client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1'
)

# Via environment variables
# export GOOGLE_GENAI_USE_VERTEXAI=true
# export GOOGLE_CLOUD_PROJECT=your-project-id
# export GOOGLE_CLOUD_LOCATION=us-central1
client = genai.Client()
```

## Migration Steps

### Step 1: Set Up Google Cloud Project

```bash
# Create project if needed
gcloud projects create my-project --name="My AI Project"

# Enable billing
gcloud billing projects link my-project --billing-account=BILLING_ACCOUNT_ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Set up authentication
gcloud auth application-default login
gcloud auth application-default set-quota-project my-project
```

### Step 2: Install/Update SDK

```bash
# Install the unified SDK
pip install google-genai

# Or update existing installation
pip install --upgrade google-genai
```

### Step 3: Update Client Initialization

**Before (Gemini Developer API):**
```python
from google import genai

client = genai.Client(api_key='YOUR_API_KEY')
```

**After (Vertex AI):**
```python
from google import genai

client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1'
)
```

### Step 4: Update Model Names (if needed)

Most model IDs are the same, but Vertex AI uses publisher-prefixed models in some cases. Check current model availability:

```python
# List available models on current platform
for model in client.models.list():
    print(model.name, model.display_name)
```

Common model IDs work on both platforms:
- `gemini-2.5-pro` 
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.0-flash`
- `gemini-2.0-flash-lite`

### Step 5: Update File Handling (if applicable)

The `client.files` API is only available on the Gemini Developer API. On Vertex AI, use GCS URIs:

**Gemini Developer API (files.upload):**
```python
# Upload and use file
file = client.files.upload(file='document.pdf')
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=['Summarize this.', file]
)
```

**Vertex AI (GCS URIs):**
```python
from google.genai import types

# Use GCS URI directly
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        'Summarize this.',
        types.Part.from_uri(
            file_uri='gs://my-bucket/document.pdf',
            mime_type='application/pdf'
        )
    ]
)
```

### Step 6: No Other Code Changes Needed

All other API calls (generate_content, streaming, function calling, etc.) remain identical:

```python
# Works on BOTH platforms without changes:
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)
print(response.text)

# Streaming - same on both
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story.'
):
    print(chunk.text, end='')

# Function calling - same on both
from google.genai import types

def get_weather(location: str) -> str:
    return "Sunny, 72°F"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather in Boston?',
    config=types.GenerateContentConfig(tools=[get_weather]),
)
```

## Platform-Specific Features

### Features Only on Vertex AI

```python
# 1. Compute tokens (returns token IDs)
response = client.models.compute_tokens(
    model='gemini-2.5-flash',
    contents='Hello world',
)

# 2. Batch predictions from BigQuery
job = client.batches.create(
    model='gemini-2.5-flash',
    src='bq://project.dataset.input-table',
    config=types.CreateBatchJobConfig(
        dest='bq://project.dataset.output-table',
    )
)

# 3. Model tuning
tuning_job = client.tunings.tune(
    base_model='gemini-2.0-flash',
    training_dataset=types.TuningDataset(
        gcs_uri='gs://bucket/training-data.jsonl',
    ),
    config=types.CreateTuningJobConfig(epoch_count=1),
)

# 4. Image upscaling (Imagen)
response = client.models.upscale_image(
    model='imagen-4.0-upscale-preview',
    image=original_image,
    upscale_factor='x2',
)

# 5. Image editing (Imagen)
response = client.models.edit_image(
    model='imagen-3.0-capability-001',
    prompt='Replace background with blue sky',
    reference_images=[raw_ref, mask_ref],
)
```

### Features Only on Gemini Developer API

```python
# File management
file = client.files.upload(file='document.pdf')
file_info = client.files.get(name=file.name)
client.files.delete(name=file.name)
```

## Checking Which Platform You're On

```python
from google import genai

client = genai.Client(vertexai=True, project='proj', location='us-central1')

# Check platform
print(client.vertexai)  # True for Vertex AI, False for Developer API

# Conditional code for platform differences
if client.vertexai:
    # Use GCS URIs
    content_part = types.Part.from_uri(
        file_uri='gs://bucket/file.pdf',
        mime_type='application/pdf'
    )
else:
    # Use files API
    file = client.files.upload(file='document.pdf')
    content_part = file
```

## Migrating from Old `vertexai` Library

If you were using the older `vertexai.generative_models` module (now deprecated), here's how to migrate:

### Old Code (Deprecated)

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

vertexai.init(project='my-project', location='us-central1')

model = GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Why is the sky blue?')
print(response.text)
```

### New Code (google-genai SDK)

```python
from google import genai

client = genai.Client(
    vertexai=True,
    project='my-project',
    location='us-central1'
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)
print(response.text)
```

## API Version and Endpoint Differences

The underlying REST endpoint differs:

**Gemini Developer API:**
```
https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

**Vertex AI:**
```
https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{model}:generateContent
```

The SDK handles these differences transparently.

## Environment Variable Migration

| Gemini Developer API | Vertex AI |
|---------------------|-----------|
| `GEMINI_API_KEY` | (not used) |
| `GOOGLE_API_KEY` | (not used) |
| `GOOGLE_GENAI_USE_VERTEXAI=false` | `GOOGLE_GENAI_USE_VERTEXAI=true` |
| (not needed) | `GOOGLE_CLOUD_PROJECT=project-id` |
| (not needed) | `GOOGLE_CLOUD_LOCATION=us-central1` |

## Cost Considerations

Both platforms use token-based pricing, but the rates differ slightly. Vertex AI adds Google Cloud overhead:

### Setup for Cost Monitoring on Vertex AI

```bash
# Set up budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Vertex AI Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

### Check Current Costs

```bash
# View billing export in BigQuery (if configured)
bq query --nouse_legacy_sql '
  SELECT service.description, SUM(cost) as total_cost
  FROM `project.billing_dataset.gcp_billing_export_v1_*`
  WHERE _PARTITIONTIME >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    AND service.description LIKE "%Vertex AI%"
  GROUP BY service.description
  ORDER BY total_cost DESC
'
```

## Migrating Quotas

The Gemini Developer API and Vertex AI have separate quota systems:

### Vertex AI Default Quotas

| Resource | Default |
|----------|---------|
| Requests per minute (gemini-2.5-flash) | 60 RPM |
| Tokens per minute | 4,000,000 TPM |
| Requests per day | Unlimited (quota may apply) |

### Request Quota Increase

1. Go to Cloud Console > IAM & Admin > Quotas
2. Filter by "Vertex AI"
3. Select the quota to increase
4. Click "Edit Quota" and submit request

## Useful Links for Migration

- google-genai SDK: https://pypi.org/project/google-genai/
- Vertex AI Pricing: https://cloud.google.com/vertex-ai/generative-ai/pricing
- Vertex AI Quotas: https://cloud.google.com/vertex-ai/docs/quotas
- Google Cloud Project Setup: https://cloud.google.com/resource-manager/docs/creating-managing-projects
- Authentication Guide: https://cloud.google.com/vertex-ai/docs/authentication
- Gemini Models on Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
