# OpenAI Batch API
> Source: https://platform.openai.com/docs/guides/batch
> Fetched: 2026-06-20

## Overview

The Batch API allows you to send large volumes of requests asynchronously at **50% off** standard API prices. Batches complete within 24 hours (typically 1–6 hours).

**Best for:** Data processing, classification, evaluation, offline generation — any task where real-time response is not required.

---

## Key Benefits

- **50% discount** on input and output tokens
- **Higher rate limits** than the synchronous API (separate quota)
- **Stacks with caching**: Cached tokens get 50% off *on top of* the batch discount (total ~75% off)
- **Stacks with Batch + Caching**: Theoretical minimum of 25% of standard cost

---

## Supported Endpoints

- `/v1/chat/completions` — Chat Completions
- `/v1/embeddings` — Embeddings
- `/v1/responses` — Responses API

---

## Supported Models

Most chat completion and embedding models are supported. Check current support at the pricing page. Each input file must contain requests for only a **single model** — you cannot mix models in one batch.

---

## Request Format

Each line in the JSONL input file represents one API request:

```jsonl
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}], "max_tokens": 100}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Classify this review as positive or negative: 'Great product!'"}]}}
{"custom_id": "request-3", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "The quick brown fox"}}
```

### Required Fields per Request

| Field | Description |
|-------|-------------|
| `custom_id` | Your unique identifier for this request (string, max 64 chars) |
| `method` | HTTP method — always `"POST"` |
| `url` | Endpoint path — `/v1/chat/completions` or `/v1/embeddings` |
| `body` | Standard API request parameters for that endpoint |

---

## Limits

| Property | Limit |
|----------|-------|
| Max requests per batch file | 50,000 |
| Max input file size | 200 MB |
| Max in-flight batch size | 200,000 requests across all pending batches |
| Max in-flight tokens | 50 million tokens across all pending batches |
| Completion window | 24 hours (most complete in 1–6 hours) |
| Default queued quota | 100,000 queued tokens per model per minute |

---

## Complete Workflow

### Step 1: Create the JSONL file

```python
import json

requests = [
    {
        "custom_id": f"req-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": f"Classify sentiment: {text}"}
            ],
            "max_tokens": 10
        }
    }
    for i, text in enumerate(["Great!", "Terrible.", "It was okay.", "Loved it!"])
]

with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")
```

### Step 2: Upload the file

```python
from openai import OpenAI

client = OpenAI()

with open("batch_input.jsonl", "rb") as f:
    batch_file = client.files.create(
        file=f,
        purpose="batch"
    )

print(f"File ID: {batch_file.id}")
```

### Step 3: Create the batch

```python
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
        "description": "Sentiment classification job"
    }
)

print(f"Batch ID: {batch.id}")
print(f"Status: {batch.status}")  # "validating" initially
```

### Step 4: Monitor status

```python
import time

while batch.status not in ["completed", "failed", "cancelled", "expired"]:
    time.sleep(60)  # check every minute
    batch = client.batches.retrieve(batch.id)
    print(f"Status: {batch.status} | "
          f"Completed: {batch.request_counts.completed} | "
          f"Failed: {batch.request_counts.failed} | "
          f"Total: {batch.request_counts.total}")
```

### Step 5: Retrieve results

```python
if batch.status == "completed":
    output_content = client.files.content(batch.output_file_id)
    
    results = {}
    for line in output_content.text.splitlines():
        result = json.loads(line)
        custom_id = result["custom_id"]
        
        if result["error"]:
            print(f"{custom_id}: Error - {result['error']}")
            continue
        
        response_body = result["response"]["body"]
        content = response_body["choices"][0]["message"]["content"]
        results[custom_id] = content
        print(f"{custom_id}: {content}")
    
    # Handle errors file (partial failures)
    if batch.error_file_id:
        error_content = client.files.content(batch.error_file_id)
        for line in error_content.text.splitlines():
            error = json.loads(line)
            print(f"Error for {error['custom_id']}: {error['error']}")
```

---

## Output Format

Each line in the output JSONL:

```json
{
  "id": "batch_req_abc123",
  "custom_id": "request-1",
  "response": {
    "status_code": 200,
    "request_id": "req_abc123",
    "body": {
      "id": "chatcmpl-xyz",
      "object": "chat.completion",
      "choices": [{"message": {"content": "4"}, "finish_reason": "stop"}],
      "usage": {"prompt_tokens": 20, "completion_tokens": 2, "total_tokens": 22}
    }
  },
  "error": null
}
```

For failed requests, `response` is null and `error` contains the error details.

---

## Batch Status Values

| Status | Description |
|--------|-------------|
| `validating` | File is being validated |
| `failed` | Validation failed — invalid file |
| `in_progress` | Batch is running |
| `finalizing` | Results are being compiled |
| `completed` | All requests processed |
| `expired` | Batch exceeded 24h window |
| `cancelling` | Cancel in progress |
| `cancelled` | Batch was cancelled |

---

## Managing Batches

```python
# List all batches
batches = client.batches.list(limit=10)
for b in batches.data:
    print(f"{b.id}: {b.status} ({b.request_counts.completed}/{b.request_counts.total})")

# Retrieve specific batch
batch = client.batches.retrieve("batch_abc123")

# Cancel a batch
client.batches.cancel("batch_abc123")
```

---

## Pricing Examples

| Model | Standard Input | Batch Input | Standard Output | Batch Output |
|-------|--------------|------------|----------------|-------------|
| gpt-4o | $2.50/1M | $1.25/1M | $10.00/1M | $5.00/1M |
| gpt-4o-mini | $0.15/1M | $0.075/1M | $0.60/1M | $0.30/1M |
| gpt-4.1 | $2.00/1M | $1.00/1M | $8.00/1M | $4.00/1M |
| gpt-4.1-mini | $0.40/1M | $0.20/1M | $1.60/1M | $0.80/1M |
| gpt-4.1-nano | $0.10/1M | $0.05/1M | $0.40/1M | $0.20/1M |

**With caching + batch**: Cached input is already discounted ~50%, then batch gives another 50% off → ~75% off standard input price.

---

## Large-Scale Processing Pattern

```python
import json
import time
from pathlib import Path
from openai import OpenAI

client = OpenAI()

def run_batch_job(items: list, output_path: str):
    """Process a list of items via Batch API."""
    
    # Create JSONL
    jsonl_lines = [
        json.dumps({
            "custom_id": f"item-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": item}],
                "max_tokens": 200
            }
        })
        for i, item in enumerate(items)
    ]
    
    # Upload
    batch_file = client.files.create(
        file=("\n".join(jsonl_lines)).encode(),
        purpose="batch"
    )
    
    # Submit
    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    
    print(f"Batch {batch.id} submitted. Waiting...")
    
    # Poll
    while batch.status not in ["completed", "failed", "cancelled", "expired"]:
        time.sleep(60)
        batch = client.batches.retrieve(batch.id)
        print(f"  {batch.status}: {batch.request_counts.completed}/{batch.request_counts.total}")
    
    if batch.status != "completed":
        raise RuntimeError(f"Batch failed with status: {batch.status}")
    
    # Download results
    content = client.files.content(batch.output_file_id)
    results = {}
    for line in content.text.splitlines():
        r = json.loads(line)
        if not r["error"]:
            results[r["custom_id"]] = r["response"]["body"]["choices"][0]["message"]["content"]
    
    # Cleanup uploaded file
    client.files.delete(batch_file.id)
    
    return results

# Usage
texts = ["Classify: Great product!", "Classify: Terrible quality!", "Classify: Average."]
results = run_batch_job(texts, "results.json")
print(results)
```

---

## Sources
- [Batch API | OpenAI API](https://developers.openai.com/api/docs/guides/batch)
- [A practical guide to the OpenAI Batch API | eesel AI](https://www.eesel.ai/blog/openai-batch-api)
- [Batch API is now available | OpenAI Community](https://community.openai.com/t/batch-api-is-now-available/718416)
