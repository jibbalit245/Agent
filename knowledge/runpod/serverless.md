# RunPod Serverless Endpoints
> Source: https://docs.runpod.io/serverless/overview, https://medium.com/@musharafhussainabid/how-to-deploy-a-serverless-ai-inference-worker-on-runpod-a-complete-production-guide-19104972e573, https://github.com/runpod-workers/worker-template, https://docs.runpod.io/serverless/pricing
> Fetched: 2026-06-20

## What are Serverless Endpoints?

RunPod Serverless provides auto-scaling AI inference infrastructure. You define a **handler function** that processes one job at a time. RunPod manages:
- Docker container lifecycle
- Scaling up workers as queue depth grows
- Scaling down to zero when idle
- Job routing and result storage
- Per-millisecond billing

Compared to GPU Pods, serverless is better for production inference APIs with variable traffic. You don't pay for idle time (unless you set minimum workers > 0).

## Handler Function

The handler is the core of your serverless worker. It's a Python function that receives a job and returns a result.

### Minimal example

```python
# handler.py
import runpod

def handler(job):
    job_input = job["input"]
    prompt = job_input.get("prompt", "Hello!")

    # Your inference logic here
    result = f"Processed: {prompt}"

    return result

runpod.serverless.start({"handler": handler})
```

### Handler with model loading (recommended pattern)

Load the model once at container startup (outside the handler) to avoid reloading on every request:

```python
import runpod
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load at startup — runs once per worker lifecycle
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)
model.eval()

def handler(job):
    job_input = job["input"]
    prompt = job_input["prompt"]
    max_new_tokens = job_input.get("max_new_tokens", 512)

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7
        )

    generated = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"generated_text": generated}

runpod.serverless.start({"handler": handler})
```

### Async handler (for streaming or long jobs)

```python
import runpod

async def async_handler(job):
    job_input = job["input"]
    # Use async/await for non-blocking operations
    result = await some_async_inference(job_input)
    return result

runpod.serverless.start({"handler": async_handler})
```

### Generator handler (streaming output)

```python
import runpod

def generator_handler(job):
    job_input = job["input"]

    # Yield tokens as they're generated
    for token in stream_generate(job_input["prompt"]):
        yield token

runpod.serverless.start({"handler": generator_handler})
```

## Worker Template (Dockerfile)

```dockerfile
# Use the RunPod base image — includes CUDA, Python, uv package manager
FROM runpod/base:0.6.2-cuda12.4.1

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy your handler
COPY handler.py /

# Start the serverless worker
CMD ["python", "-u", "/handler.py"]
```

```
# requirements.txt
runpod>=1.7.0
torch>=2.4.0
transformers>=4.44.0
accelerate>=0.33.0
```

## Deployment Methods

### Method 1: GitHub Integration (Recommended)

1. Push your code to GitHub
2. In RunPod console: **Serverless > New Endpoint > GitHub**
3. Connect your repo and branch
4. RunPod auto-builds and deploys on push

### Method 2: Manual Docker Build

```bash
# Build
docker build -t my-worker:v1 .

# Push to Docker Hub or ECR
docker tag my-worker:v1 myuser/my-worker:v1
docker push myuser/my-worker:v1

# Or push to RunPod's container registry
```

Then in RunPod console: **Serverless > New Endpoint > Custom Image** > enter image URL.

## Scaling Configuration

When creating or editing an endpoint:

| Setting | Description | Recommendation |
|---------|-------------|----------------|
| Min Workers | Always-on workers (billed even if idle) | 0 for cost; 1+ for latency |
| Max Workers | Upper scaling limit | 3–10 for most use cases |
| Idle Timeout | Seconds before scaling down a worker | 5–60s for cost; higher for latency |
| Active (Execution) Timeout | Max seconds per job | Match your model's P99 latency |
| FlashBoot | Pre-warm cached containers | Enable for faster cold starts |

### Scale-to-zero (lowest cost)

```
Min Workers: 0
Idle Timeout: 5 seconds
```

- Workers fully spin down when no requests
- Cold start on first request after idle period
- No cost during silence

### Low-latency setup

```
Min Workers: 1-2
Idle Timeout: 300 seconds
```

- 1-2 workers always warm — no cold start for baseline traffic
- Cost: ~$0.03–0.07/hr for a mid-tier GPU always warm
- A 2026 production guide notes 2 always-on workers eliminate cold starts for baseline load

## Cold Start Times

Cold start = time from job arrival to handler first execution when no workers are ready.

Factors affecting cold start:
1. **Image pull time**: Smaller images start faster. Pre-cache images using FlashBoot.
2. **Model loading time**: Loading a 7B model from disk: 5–30s. From network volume: 10–60s depending on bandwidth.
3. **Python import time**: Minimize imports in handler.py.

Strategies to minimize:
- **Bake model into image**: Pre-download weights into the Docker image. Increases image size but eliminates network download at runtime. Sub-5s cold starts possible.
- **FlashBoot**: RunPod's container caching layer. Enable in endpoint settings. Achieves sub-200ms cold starts for cached containers.
- **Set Min Workers > 0**: Eliminates cold starts for baseline traffic.
- **Use smaller quantized models**: 4-bit quantized 7B model loads 2–4x faster than FP16.

## Testing Endpoints

### Via RunPod console

Go to **Serverless > Your Endpoint > Test** and submit a JSON payload.

### Via REST API

```python
import requests

ENDPOINT_ID = "your-endpoint-id"
API_KEY = "your-runpod-api-key"

url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/run"
headers = {"Authorization": f"Bearer {API_KEY}"}

payload = {
    "input": {
        "prompt": "What is 2+2?",
        "max_new_tokens": 100
    }
}

# Async run (returns job ID)
response = requests.post(url, json=payload, headers=headers)
job_id = response.json()["id"]

# Poll for result
result_url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/status/{job_id}"
while True:
    result = requests.get(result_url, headers=headers).json()
    if result["status"] in ["COMPLETED", "FAILED"]:
        break
    time.sleep(1)

print(result["output"])
```

### Synchronous run (waits for result)

```python
url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/runsync"
response = requests.post(url, json=payload, headers=headers, timeout=120)
print(response.json()["output"])
```

## Pricing

Serverless is billed per **GPU second** (or "compute unit").

Representative rates:
| GPU | Cost per second | Cost per hour equiv |
|-----|----------------|---------------------|
| RTX 4090 | ~$0.000210/s | ~$0.76/hr |
| A100 80GB | ~$0.000583/s | ~$2.10/hr |
| H100 PCIe | ~$0.000833/s | ~$3.00/hr |

You are billed only while a worker is processing or warming up. A worker idle with Min Workers = 0 incurs no cost.

For a 7B model generating ~100 tokens in 3 seconds on an RTX 4090:
- Cost per request: 3s × $0.000210/s = **$0.00063 per inference**
- 1,000 requests/day = **$0.63/day**
