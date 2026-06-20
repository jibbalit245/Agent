# Replicate Webhooks

> Source: https://replicate.com/docs/topics/webhooks
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Webhooks allow you to receive real-time push notifications about prediction status changes, instead of polling the API. When a prediction reaches a new state, Replicate sends an HTTP POST request to your specified URL.

## Setting Up Webhooks

Include a `webhook` URL in your prediction request:

```python
import replicate

prediction = replicate.predictions.create(
    version="39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={"prompt": "a photo of an astronaut"},
    webhook="https://your-server.com/webhooks/replicate",
    webhook_events_filter=["completed"]
)
```

### Via HTTP API

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "39ed52f2...",
    "input": {"prompt": "an astronaut"},
    "webhook": "https://your-server.com/webhooks/replicate",
    "webhook_events_filter": ["start", "completed"]
  }' \
  https://api.replicate.com/v1/predictions
```

## Webhook Events

You can filter which events trigger webhook requests using `webhook_events_filter`:

| Event | When Triggered | Always Sent |
|-------|---------------|-------------|
| `start` | Immediately when prediction begins processing | Yes |
| `output` | Each time the prediction generates new output | No |
| `logs` | Each time log output is generated | No |
| `completed` | When prediction reaches terminal state (succeeded/failed/canceled) | Yes |

### Event Filtering Behavior

- `start` and `completed` are **always sent**, regardless of your filter
- `output` and `logs` events are throttled to at most **once every 500ms**
- Default behavior (no filter): sends on new outputs and completion

### Example Filter Configurations

```python
# Only notify when done
webhook_events_filter=["completed"]

# Get all events
webhook_events_filter=["start", "output", "logs", "completed"]

# Get start and completion only
webhook_events_filter=["start", "completed"]
```

## Webhook Request Format

Replicate sends an HTTP POST request to your URL with:
- **Method:** POST
- **Content-Type:** application/json
- **Body:** Same as the GET prediction response body

### Example Webhook Payload

```json
{
  "id": "gm3qorzdhgbfurvjtvhg6dckhu",
  "model": "black-forest-labs/flux-schnell",
  "version": "39ed52f2...",
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
    "prompt": "a photo of an astronaut"
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

## Webhook Verification

Replicate signs every webhook request with a unique key to prevent unauthorized requests.

### Getting Your Signing Secret

```bash
curl -s \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/webhooks/default/secret
```

Response:
```json
{
  "key": "whsec_C2FVsBQIhrscChlQIMV+b5sSYspob7oD"
}
```

Store the secret as an environment variable:
```bash
export REPLICATE_WEBHOOK_SIGNING_SECRET=whsec_C2FVsBQIhrscChlQIMV+b5sSYspob7oD
```

### How Signature Verification Works

Replicate includes these headers with each webhook request:

| Header | Description |
|--------|-------------|
| `webhook-id` | Unique ID for the webhook message |
| `webhook-timestamp` | Unix timestamp of when the webhook was sent |
| `webhook-signature` | HMAC-SHA256 signature(s) |

### Signed Content Format

The signed content is constructed as:
```
{webhook_id}.{webhook_timestamp}.{body}
```

Where `body` is the raw JSON request body string.

### Computing the Expected Signature

```python
import base64
import hashlib
import hmac
import os

def verify_webhook(webhook_id: str, webhook_timestamp: str, 
                   body: str, signature_header: str) -> bool:
    """Verify a Replicate webhook signature."""
    
    secret = os.environ["REPLICATE_WEBHOOK_SIGNING_SECRET"]
    
    # Remove "whsec_" prefix and decode base64
    secret_bytes = base64.b64decode(secret.removeprefix("whsec_"))
    
    # Build signed content
    signed_content = f"{webhook_id}.{webhook_timestamp}.{body}"
    
    # Compute expected signature
    expected_sig = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()
    
    # Compare against received signatures (may be multiple)
    received_sigs = signature_header.split(" ")
    for sig in received_sigs:
        sig_value = sig.split(",", 1)[1] if "," in sig else sig
        if hmac.compare_digest(expected_sig, sig_value):
            return True
    
    return False
```

### Using the Python Client's validateWebhook

```python
import replicate
import os

def handle_webhook(request):
    secret = os.environ["REPLICATE_WEBHOOK_SIGNING_SECRET"]
    
    is_valid = replicate.webhooks.validate(
        request=request,  # Must be a web-standard Request object
        secret=secret
    )
    
    if not is_valid:
        return {"error": "Invalid webhook signature"}, 401
    
    # Process the webhook
    body = request.json()
    print(f"Prediction {body['id']} status: {body['status']}")
```

## Receiving Webhooks

### FastAPI Example

```python
from fastapi import FastAPI, Request, HTTPException, Header
import replicate
import os

app = FastAPI()

@app.post("/webhooks/replicate")
async def handle_replicate_webhook(
    request: Request,
    webhook_id: str = Header(None),
    webhook_timestamp: str = Header(None),
    webhook_signature: str = Header(None)
):
    body = await request.body()
    
    # Verify signature
    secret = os.environ["REPLICATE_WEBHOOK_SIGNING_SECRET"]
    signed_content = f"{webhook_id}.{webhook_timestamp}.{body.decode()}"
    
    import base64, hashlib, hmac
    secret_bytes = base64.b64decode(secret.removeprefix("whsec_"))
    expected_sig = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()
    
    sigs = webhook_signature.split(" ")
    valid = any(
        hmac.compare_digest(expected_sig, s.split(",")[1] if "," in s else s)
        for s in sigs
    )
    
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = await request.json()
    
    if data["status"] == "succeeded":
        print(f"Prediction succeeded: {data['output']}")
    elif data["status"] == "failed":
        print(f"Prediction failed: {data['error']}")
    
    return {"received": True}
```

### Flask Example

```python
from flask import Flask, request, jsonify
import os, base64, hashlib, hmac

app = Flask(__name__)

@app.route("/webhooks/replicate", methods=["POST"])
def handle_webhook():
    webhook_id = request.headers.get("webhook-id")
    webhook_timestamp = request.headers.get("webhook-timestamp")
    webhook_signature = request.headers.get("webhook-signature")
    body = request.get_data(as_text=True)
    
    # Verify signature
    secret = os.environ["REPLICATE_WEBHOOK_SIGNING_SECRET"]
    secret_bytes = base64.b64decode(secret.removeprefix("whsec_"))
    signed_content = f"{webhook_id}.{webhook_timestamp}.{body}"
    expected_sig = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()
    
    sigs = webhook_signature.split(" ")
    valid = any(
        hmac.compare_digest(expected_sig, s.split(",")[1] if "," in s else s)
        for s in sigs
    )
    
    if not valid:
        return jsonify({"error": "Invalid signature"}), 401
    
    data = request.get_json()
    print(f"Prediction {data['id']}: {data['status']}")
    
    return jsonify({"received": True})
```

## Replay Attack Prevention

To prevent replay attacks, validate the webhook timestamp:

```python
import time

def is_timestamp_valid(webhook_timestamp: str, tolerance_seconds: int = 300) -> bool:
    """Reject webhooks older than 5 minutes."""
    ts = int(webhook_timestamp)
    now = int(time.time())
    return abs(now - ts) < tolerance_seconds
```

## Testing Webhooks Locally

Use tools like ngrok to expose your local server:

```bash
# Start your server
python -m uvicorn main:app --port 8000

# In another terminal, expose it publicly
ngrok http 8000

# Use the ngrok URL as your webhook URL
# e.g., https://abc123.ngrok.io/webhooks/replicate
```

## Webhook Delivery

- Replicate will retry webhook delivery if your endpoint returns a non-2xx response
- Webhooks are delivered at least once (may occasionally be duplicated)
- Use the `webhook-id` header to deduplicate if needed
- Recommended: return 200 quickly and process asynchronously
