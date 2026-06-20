# Replicate Predictions

> Source: https://replicate.com/docs/topics/predictions
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## What is a Prediction?

A prediction is a single run of a model on Replicate. You provide inputs, the model processes them, and you get outputs back. Predictions are the core unit of work on Replicate.

## Prediction Modes

### Synchronous (Sync) Mode

Optimized for returning model output as quickly as possible. The HTTP connection stays open until the prediction completes or times out.

**Best for:** Real-time applications, interactive UIs, when you need immediate results.

```python
import replicate

# Waits up to 60 seconds for result
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "an astronaut"},
    wait=60
)
print(output)
```

**HTTP with Prefer header:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait=60" \
  -d '{"model": "black-forest-labs/flux-schnell", "input": {"prompt": "..."}}' \
  https://api.replicate.com/v1/predictions
```

### Asynchronous (Async) Mode

Returns immediately with a prediction ID. You then poll for the result or use webhooks.

**Best for:** Long-running tasks, batch processing, background jobs.

```python
import replicate

# Returns immediately with prediction object
prediction = replicate.predictions.create(
    model="black-forest-labs/flux-schnell",
    input={"prompt": "an astronaut"},
)

print(prediction.id)     # "gm3qorzdhgbfurvjtvhg6dckhu"
print(prediction.status) # "starting"

# Poll until complete
prediction.wait()

print(prediction.status) # "succeeded"
print(prediction.output)
```

## Creating Predictions

### Using `replicate.run()` (Recommended for Simple Cases)

```python
import replicate

output = replicate.run(
    "owner/model-name:version-hash",
    input={
        "prompt": "a photo of a dog",
        "width": 512,
        "height": 512,
        "num_outputs": 1
    }
)
```

### Using `replicate.predictions.create()` (Full Control)

```python
prediction = replicate.predictions.create(
    version="39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={"prompt": "a photo of a dog"},
    webhook="https://example.com/webhook",
    webhook_events_filter=["completed"],
    stream=False
)
```

## Prediction Lifecycle

```
[created] → [starting] → [processing] → [succeeded]
                                      ↘ [failed]
              ↓
           [canceled]
```

### Status Values

| Status | Description |
|--------|-------------|
| `starting` | Queued, waiting for hardware |
| `processing` | Model is actively running |
| `succeeded` | Output generated successfully |
| `failed` | Error occurred during processing |
| `canceled` | Manually canceled by user |

## Polling for Results

```python
import time
import replicate

prediction = replicate.predictions.create(
    model="black-forest-labs/flux-schnell",
    input={"prompt": "an astronaut"}
)

# Manual polling
while prediction.status not in ["succeeded", "failed", "canceled"]:
    time.sleep(1)
    prediction.reload()
    print(f"Status: {prediction.status}")

# Or use built-in wait
prediction.wait()  # Blocks until terminal state

print(prediction.output)
```

## Prediction Object Properties

```python
prediction = replicate.predictions.get("gm3qorzdhgbfurvjtvhg6dckhu")

prediction.id            # "gm3qorzdhgbfurvjtvhg6dckhu"
prediction.model         # "black-forest-labs/flux-schnell"
prediction.version       # "39ed52f2..."
prediction.status        # "succeeded"
prediction.input         # {"prompt": "..."}
prediction.output        # ["https://..."] or streaming object
prediction.error         # None or error message string
prediction.logs          # Model log output as string
prediction.created_at    # datetime
prediction.started_at    # datetime
prediction.completed_at  # datetime
prediction.metrics       # {"predict_time": 6.5, "total_time": 7.0}
prediction.urls          # {"get": "...", "cancel": "..."}
```

## Output Types

Different models produce different output types:

| Model Type | Output Type | Example |
|------------|-------------|---------|
| Image generation | Array of FileOutput/URL | `[<FileOutput>]` |
| Language model | String or stream | `"Once upon a time..."` |
| Audio generation | FileOutput/URL | `<FileOutput>` |
| Video generation | FileOutput/URL | `<FileOutput>` |

## Canceling Predictions

```python
# Cancel by prediction object
prediction = replicate.predictions.create(...)
prediction.cancel()

# Verify cancellation
prediction.reload()
print(prediction.status)  # "canceled"
```

```bash
# Cancel via HTTP API
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/predictions/{prediction_id}/cancel
```

## Listing Predictions

```python
# Get first page (100 predictions)
page = replicate.predictions.list()

# Paginate
while page:
    for pred in page.results:
        print(pred.id, pred.status)
    page = replicate.predictions.list(page.next) if page.next else None
```

## Streaming Predictions

For models that support streaming (e.g., language models):

```python
# Stream from the run() method
for event in replicate.stream(
    "meta/meta-llama-3-70b-instruct",
    input={"prompt": "Tell me a story"}
):
    print(str(event), end="", flush=True)

# Stream from a prediction object
prediction = replicate.predictions.create(
    model="meta/meta-llama-3-70b-instruct",
    input={"prompt": "Tell me a story"},
    stream=True,
)

for event in prediction.stream():
    print(str(event), end="", flush=True)
```

## Using Webhooks for Async Predictions

Instead of polling, receive push notifications when predictions complete:

```python
prediction = replicate.predictions.create(
    model="black-forest-labs/flux-schnell",
    input={"prompt": "an astronaut"},
    webhook="https://your-server.com/webhooks/replicate",
    webhook_events_filter=["completed"]
)
# Your webhook endpoint will receive a POST when the prediction is done
```

## Concurrent Predictions

```python
import asyncio
import replicate

async def run_multiple():
    prompts = ["a cat", "a dog", "a bird", "a fish"]
    
    tasks = [
        replicate.async_run(
            "black-forest-labs/flux-schnell",
            input={"prompt": prompt}
        )
        for prompt in prompts
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

## Error Handling

```python
from replicate.exceptions import ModelError

try:
    output = replicate.run("some-model", input={...})
except ModelError as e:
    print(f"Prediction {e.prediction.id} failed")
    print(f"Error: {e.prediction.error}")
    print(f"Logs: {e.prediction.logs}")
```

## Prediction Metrics

After completion, predictions include timing metrics:

```json
{
  "metrics": {
    "predict_time": 6.5,
    "total_time": 7.0
  }
}
```

- `predict_time`: Time the model was actually running (billable)
- `total_time`: Total elapsed time including setup/queue

## Create Prediction via HTTP

### Full API Request

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    "input": {
      "prompt": "a photo of an astronaut riding a horse",
      "width": 768,
      "height": 768,
      "num_outputs": 1,
      "guidance_scale": 7.5
    },
    "webhook": "https://example.com/hooks/replicate",
    "webhook_events_filter": ["start", "completed"]
  }' \
  https://api.replicate.com/v1/predictions
```
