# RunPod Python SDK and REST API
> Source: https://github.com/runpod/runpod-python, https://docs.runpod.io/serverless/endpoints/send-requests, https://pypi.org/project/runpod/
> Fetched: 2026-06-20

## Installation

```bash
pip install runpod
```

Requires Python 3.10 or higher.

## Authentication

```python
import runpod
import os

# Set your API key (get from Settings > API Keys in RunPod console)
runpod.api_key = os.environ.get("RUNPOD_API_KEY")
```

## SDK: Two Modes

The `runpod` library serves two distinct roles:

1. **Client SDK**: Manage pods, endpoints, volumes; submit jobs from outside RunPod
2. **Worker SDK**: Build serverless handler functions that run *inside* RunPod workers

## Client SDK — Managing Resources and Submitting Jobs

### Pod Management

```python
import runpod

runpod.api_key = "your_key"

# List all pods
pods = runpod.get_pods()
for pod in pods:
    print(pod["id"], pod["name"], pod["desiredStatus"])

# Get a specific pod
pod = runpod.get_pod("pod_id_here")

# Create a pod
pod = runpod.create_pod(
    name="my-training-pod",
    image_name="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
    gpu_type_id="NVIDIA GeForce RTX 4090",
    cloud_type="SECURE",        # "COMMUNITY" or "SECURE"
    gpu_count=1,
    volume_in_gb=20,            # Container disk (ephemeral)
    container_disk_in_gb=20,
    min_memory_in_gb=16,
    ports="8888/http,22/tcp",   # Port mappings
    env={"MY_VAR": "value"},
    data_center_id="US-TX-3"    # Optional
)

# Stop a pod (saves state, reduces cost)
runpod.stop_pod(pod_id="abc123")

# Resume a stopped pod
runpod.resume_pod(pod_id="abc123", gpu_count=1)

# Terminate a pod (permanent; frees resources)
runpod.terminate_pod(pod_id="abc123")
```

### Submitting Jobs to Serverless Endpoints

```python
import runpod

runpod.api_key = "your_key"

# Get an endpoint object
endpoint = runpod.Endpoint("your-endpoint-id")

# Async run — returns a job handle immediately
run_request = endpoint.run({
    "prompt": "Explain transformers in one paragraph",
    "max_new_tokens": 200
})

print(f"Job ID: {run_request.job_id}")

# Poll for status
status = run_request.status()  # "IN_QUEUE", "IN_PROGRESS", "COMPLETED", "FAILED"

# Wait and get result (blocks until done)
output = run_request.output()
print(output)
```

### run_sync — Synchronous Job Submission

`run_sync` submits a job and waits until it completes, returning the output directly:

```python
endpoint = runpod.Endpoint("your-endpoint-id")

# Blocks until job finishes or times out
output = endpoint.run_sync(
    {"prompt": "What is 42?", "max_new_tokens": 50},
    timeout=120  # seconds to wait
)
print(output)
```

`run_sync` is equivalent to submitting a job and immediately polling until completion. Use it for:
- Simple scripting where you don't need async control flow
- Testing and debugging
- Sequential batch processing

### Health check

```python
health = endpoint.health()
print(health)
# Returns: {"workers": {"idle": 2, "running": 0}, "jobs": {"queued": 0, ...}}
```

### Network Volumes

```python
# Create a volume
volume = runpod.create_network_volume(
    name="model-storage",
    size=100,          # GB
    data_center_id="US-TX-3"
)
print(volume["id"])

# List volumes
volumes = runpod.get_network_volumes()

# Delete a volume (irreversible)
runpod.delete_network_volume(volume_id="vol_abc123")
```

## Worker SDK — Building Serverless Handlers

### serverless.start()

`runpod.serverless.start()` is the entry point for deploying a serverless worker. It initializes the worker loop, connects to RunPod's job queue, and calls your handler for each incoming job.

```python
import runpod

def handler(job):
    job_input = job["input"]
    # Process the input
    return {"result": "processed"}

# Start the worker (blocks — runs until container exits)
runpod.serverless.start({"handler": handler})
```

Configuration options:
```python
runpod.serverless.start({
    "handler": handler,
    "return_aggregate_stream": False,   # For generator handlers
    "concurrency_modifier": None,       # Custom concurrency function
})
```

### Job input/output format

**Input** (what your handler receives):
```python
job = {
    "id": "job-abc123",
    "input": {
        # Whatever the caller sent in the "input" field
        "prompt": "Hello world",
        "max_tokens": 100
    },
    "webhook": None  # Optional webhook URL for result delivery
}
```

**Output** (what your handler should return):
- Any JSON-serializable Python object (dict, list, string, number)
- For errors: raise an exception (RunPod catches it and marks job as FAILED)

### Generator / streaming handler

```python
import runpod

def stream_handler(job):
    job_input = job["input"]
    prompt = job_input["prompt"]

    for chunk in generate_tokens(prompt):
        yield {"token": chunk}  # Each yield is a stream event

runpod.serverless.start({
    "handler": stream_handler,
    "return_aggregate_stream": True  # Collects all yields as a list in final output
})
```

## REST API

All RunPod functionality is also available via REST API (the Python SDK is a wrapper around this).

### Base URL

```
https://api.runpod.io/v2/{endpoint_id}/
```

### Authentication header

```
Authorization: Bearer {RUNPOD_API_KEY}
```

### Submit a job (async)

```bash
curl -X POST "https://api.runpod.io/v2/{endpoint_id}/run" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Hello!", "max_new_tokens": 100}}'

# Response: {"id": "job-abc123", "status": "IN_QUEUE"}
```

### Submit a job (synchronous)

```bash
curl -X POST "https://api.runpod.io/v2/{endpoint_id}/runsync" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Hello!"}}' \
  --max-time 120

# Response includes output directly when job completes
```

### Check job status

```bash
curl "https://api.runpod.io/v2/{endpoint_id}/status/{job_id}" \
  -H "Authorization: Bearer $RUNPOD_API_KEY"

# Response: {"id": "job-abc123", "status": "COMPLETED", "output": {...}}
```

Job statuses: `IN_QUEUE`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `CANCELLED`, `TIMED_OUT`

### Cancel a job

```bash
curl -X POST "https://api.runpod.io/v2/{endpoint_id}/cancel/{job_id}" \
  -H "Authorization: Bearer $RUNPOD_API_KEY"
```

### Check endpoint health

```bash
curl "https://api.runpod.io/v2/{endpoint_id}/health" \
  -H "Authorization: Bearer $RUNPOD_API_KEY"
```

### GraphQL API (Pod Management)

Pod management uses a GraphQL API at `https://api.runpod.io/graphql`:

```python
import requests

query = """
query {
  myself {
    pods {
      id
      name
      desiredStatus
      runtime {
        uptimeInSeconds
        gpus { id gpuUtilPercent }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.runpod.io/graphql",
    json={"query": query},
    headers={"Authorization": f"Bearer {api_key}"}
)
print(response.json())
```

## Local Testing

Test your handler before deploying:

```python
# test_handler.py
import runpod

# The SDK supports local testing mode
if __name__ == "__main__":
    test_input = {
        "id": "test-job-1",
        "input": {
            "prompt": "What is 2+2?",
            "max_new_tokens": 50
        }
    }
    result = handler(test_input)
    print(result)
```

Or use the `test_input.json` file pattern from the worker template:
```bash
python handler.py  # Reads from test_input.json automatically in local mode
```
