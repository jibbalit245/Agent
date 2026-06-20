# Replicate HTTP API Reference

> Source: https://replicate.com/docs/reference/http
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official documentation.

## Base URL

```
https://api.replicate.com/v1/
```

## Authentication

All requests must include an Authorization header:

```
Authorization: Bearer r8_your_api_token_here
Content-Type: application/json
```

API tokens start with `r8_` and are 40 characters long.
Create/manage tokens at: https://replicate.com/account/api-tokens

## Rate Limits

| Endpoint | Rate Limit |
|----------|-----------|
| `POST /predictions` | 600 requests/minute |
| All other endpoints | 3000 requests/minute |

---

## Predictions

### Create a Prediction

**POST** `/v1/predictions`

Creates a new prediction.

#### Request Headers

```
Authorization: Bearer r8_...
Content-Type: application/json
Prefer: wait=30          # Optional: wait up to N seconds for result (sync mode)
```

#### Request Body

```json
{
  "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
  "input": {
    "prompt": "a photo of an astronaut riding a horse",
    "width": 768,
    "height": 768
  },
  "webhook": "https://example.com/webhook",
  "webhook_events_filter": ["completed"],
  "stream": false
}
```

#### Alternative Request Body (using model name)

```json
{
  "model": "black-forest-labs/flux-schnell",
  "input": {
    "prompt": "a photo of an astronaut"
  }
}
```

#### Model Identifier Formats

| Format | Example |
|--------|---------|
| `owner/name` | `"black-forest-labs/flux-schnell"` |
| `owner/name:version` | `"stability-ai/sdxl:39ed52f2..."` |
| Version hash only | `"39ed52f2a78e934b..."` |

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes (if no `model`) | Version ID hash |
| `model` | string | Yes (if no `version`) | Model in `owner/name` format |
| `input` | object | Yes | Model-specific input parameters |
| `webhook` | string | No | URL to receive webhook callbacks |
| `webhook_events_filter` | array | No | Events to filter: `start`, `output`, `logs`, `completed` |
| `stream` | boolean | No | Enable streaming output |

#### Response (202 Accepted)

```json
{
  "id": "gm3qorzdhgbfurvjtvhg6dckhu",
  "model": "black-forest-labs/flux-schnell",
  "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
  "urls": {
    "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
    "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel"
  },
  "created_at": "2024-01-15T10:30:00.000Z",
  "started_at": null,
  "completed_at": null,
  "source": "api",
  "status": "starting",
  "input": {
    "prompt": "a photo of an astronaut riding a horse"
  },
  "output": null,
  "error": null,
  "logs": null,
  "metrics": {}
}
```

#### Synchronous Mode with Prefer Header

```
Prefer: wait=30
```

With this header, the request waits up to 30 seconds for the prediction to complete before returning. If it completes in time, the response includes the output. If not, returns the prediction in progress.

---

### Get a Prediction

**GET** `/v1/predictions/{prediction_id}`

Retrieve the current state of a prediction.

#### Response (200 OK)

```json
{
  "id": "gm3qorzdhgbfurvjtvhg6dckhu",
  "model": "black-forest-labs/flux-schnell",
  "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
  "urls": {
    "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
    "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel"
  },
  "created_at": "2024-01-15T10:30:00.000Z",
  "started_at": "2024-01-15T10:30:01.500Z",
  "completed_at": "2024-01-15T10:30:08.000Z",
  "source": "api",
  "status": "succeeded",
  "input": {
    "prompt": "a photo of an astronaut riding a horse"
  },
  "output": [
    "https://replicate.delivery/pbxt/example-output.webp"
  ],
  "error": null,
  "logs": "Using seed: 12345\nGenerating image...\n",
  "metrics": {
    "predict_time": 6.5,
    "total_time": 7.0
  }
}
```

#### Prediction Status Values

| Status | Description |
|--------|-------------|
| `starting` | Queued, waiting to start |
| `processing` | Model is running |
| `succeeded` | Completed successfully |
| `failed` | Encountered an error |
| `canceled` | Canceled by user |

---

### List Predictions

**GET** `/v1/predictions`

Returns a paginated list of predictions for the authenticated user/org. Sorted newest first, 100 records per page.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cursor` | string | Pagination cursor for next/prev page |

#### Response (200 OK)

```json
{
  "next": "https://api.replicate.com/v1/predictions?cursor=cD0yMDIyL...",
  "previous": null,
  "results": [
    {
      "id": "gm3qorzdhgbfurvjtvhg6dckhu",
      "model": "black-forest-labs/flux-schnell",
      "version": "39ed52f2...",
      "urls": { "get": "...", "cancel": "..." },
      "created_at": "2024-01-15T10:30:00.000Z",
      "source": "api",
      "status": "succeeded"
    }
  ]
}
```

---

### Cancel a Prediction

**POST** `/v1/predictions/{prediction_id}/cancel`

Cancel a running prediction.

#### Response (200 OK)

Returns the prediction object with `status: "canceled"`.

---

## Models

### Get a Model

**GET** `/v1/models/{model_owner}/{model_name}`

#### Response

```json
{
  "url": "https://replicate.com/stability-ai/sdxl",
  "owner": "stability-ai",
  "name": "sdxl",
  "description": "A text-to-image generative AI model",
  "visibility": "public",
  "github_url": null,
  "paper_url": null,
  "license_url": null,
  "run_count": 1000000,
  "cover_image_url": "https://...",
  "default_example": {...},
  "latest_version": {
    "id": "39ed52f2...",
    "created_at": "2024-01-01T00:00:00.000Z",
    "cog_version": "0.9.0",
    "openapi_schema": {...}
  }
}
```

### List Models

**GET** `/v1/models`

Returns paginated list of public models.

### Create a Model

**POST** `/v1/models`

```json
{
  "owner": "your-username",
  "name": "my-model",
  "description": "My custom model",
  "visibility": "public",
  "hardware": "gpu-a100-large"
}
```

---

## Model Versions

### List Versions

**GET** `/v1/models/{model_owner}/{model_name}/versions`

### Get a Version

**GET** `/v1/models/{model_owner}/{model_name}/versions/{version_id}`

### Delete a Version

**DELETE** `/v1/models/{model_owner}/{model_name}/versions/{version_id}`

---

## Collections

### List Collections

**GET** `/v1/collections`

### Get a Collection

**GET** `/v1/collections/{collection_slug}`

Returns models in the collection.

---

## Trainings

### Create a Training

**POST** `/v1/trainings`

```json
{
  "model": "stability-ai/sdxl",
  "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
  "input": {
    "input_images": "https://example.com/training-images.zip",
    "token_string": "TOK",
    "max_train_steps": 1000
  },
  "destination": "your-username/my-fine-tuned-model",
  "webhook": "https://example.com/webhook"
}
```

### Get a Training

**GET** `/v1/trainings/{training_id}`

### Cancel a Training

**POST** `/v1/trainings/{training_id}/cancel`

### List Trainings

**GET** `/v1/trainings`

---

## Hardware

### List Available Hardware

**GET** `/v1/hardware`

#### Response

```json
[
  {"name": "CPU", "sku": "cpu"},
  {"name": "Nvidia T4 GPU", "sku": "gpu-t4-nano"},
  {"name": "Nvidia L40S GPU", "sku": "gpu-l40s-medium"},
  {"name": "Nvidia A100 (80GB) GPU", "sku": "gpu-a100-large"},
  {"name": "Nvidia H100 GPU", "sku": "gpu-h100-medium"}
]
```

---

## Deployments

### Get a Deployment

**GET** `/v1/deployments/{deployment_owner}/{deployment_name}`

### Create/Update Deployment

**POST** `/v1/deployments`

```json
{
  "name": "my-model-deployment",
  "model": "stability-ai/sdxl",
  "version": "39ed52f2...",
  "hardware": "gpu-a100-large",
  "min_instances": 1,
  "max_instances": 5,
  "scale_down_delay": 300
}
```

### Create Prediction via Deployment

**POST** `/v1/deployments/{deployment_owner}/{deployment_name}/predictions`

Same body as regular prediction creation, but routes to the specific deployment.

---

## Webhooks

### Get Webhook Signing Secret

**GET** `/v1/webhooks/default/secret`

Returns the signing secret for verifying webhook authenticity.

```json
{
  "key": "whsec_C2FVsBQIhrscChlQIMV+b5sSYspob7oD"
}
```

---

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "You did not pass an authentication token"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "version"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests

```json
{
  "detail": "You have exceeded the request rate limit. Please wait before retrying."
}
```

---

## cURL Examples

### Create a Prediction

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    "input": {"prompt": "an astronaut riding a horse"}
  }' \
  https://api.replicate.com/v1/predictions
```

### Get a Prediction

```bash
curl -s \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu
```

### Synchronous Prediction (wait for result)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait=60" \
  -d '{
    "model": "black-forest-labs/flux-schnell",
    "input": {"prompt": "an astronaut riding a horse"}
  }' \
  https://api.replicate.com/v1/predictions
```
