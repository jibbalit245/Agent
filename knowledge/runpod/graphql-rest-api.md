# RunPod GraphQL and REST API Reference
> Source: https://docs.runpod.io/sdks/graphql/configurations, https://graphql-spec.runpod.io/, https://www.runpod.io/blog/runpod-rest-api-gpu-management
> Fetched: 2026-06-20

## Overview

RunPod has two API layers:

1. **GraphQL API** — For managing infrastructure (pods, volumes, templates, endpoints, billing)
   - URL: `https://api.runpod.io/graphql`
   - Auth: `?api_key=YOUR_KEY` query parameter
   
2. **REST API** — For serverless job management (submit, status, cancel, health)
   - Base URL: `https://api.runpod.io/v2/{endpoint_id}/`
   - Auth: `Authorization: Bearer YOUR_KEY` header

---

## GraphQL API

### Authentication

```bash
# API key as query parameter
curl -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ myself { id email } }"}'
```

```python
import requests

API_KEY = "your-api-key"
GRAPHQL_URL = f"https://api.runpod.io/graphql?api_key={API_KEY}"

def graphql(query, variables=None):
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}}
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data["data"]
```

### Queries — Reading Data

```graphql
# Get account info
query {
  myself {
    id
    email
    balance
    spendLimit
    clientBalance
  }
}

# List all pods
query {
  myself {
    pods {
      id
      name
      imageName
      desiredStatus
      runtime {
        uptimeInSeconds
        ports {
          ip
          isIpPublic
          privatePort
          publicPort
          type
        }
        gpus {
          id
          gpuUtilPercent
          memoryUtilPercent
        }
        container {
          cpuPercent
          memoryPercent
        }
      }
      machine {
        podHostId
      }
    }
  }
}

# Get specific pod
query GetPod($podId: String!) {
  pod(input: {podId: $podId}) {
    id
    name
    imageName
    desiredStatus
    gpuCount
    vcpuCount
    memoryInGb
    volumeInGb
    runtime {
      uptimeInSeconds
      gpus {
        id
        gpuUtilPercent
      }
    }
  }
}

# List available GPU types
query {
  gpuTypes {
    id
    displayName
    memoryInGb
    secureCloud
    communityCloud
    lowestPrice(input: {gpuCount: 1}) {
      minimumBidPrice
      uninterruptablePrice
    }
  }
}

# List network volumes
query {
  myself {
    networkVolumes {
      id
      name
      size
      dataCenterId
    }
  }
}

# List serverless endpoints
query {
  myself {
    endpoints {
      id
      name
      templateId
      type
      workersMin
      workersMax
      idleTimeout
      scalerType
      scalerValue
    }
  }
}
```

### Mutations — Modifying Data

```graphql
# Create a pod
mutation CreatePod {
  podFindAndDeployOnDemand(input: {
    name: "my-training-pod"
    imageName: "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
    gpuTypeId: "NVIDIA GeForce RTX 4090"
    cloudType: SECURE
    gpuCount: 1
    volumeInGb: 50
    containerDiskInGb: 20
    minMemoryInGb: 32
    minVcpuCount: 4
    ports: "8888/http,22/tcp"
    env: [
      {key: "MODEL_NAME", value: "mistral-7b"},
      {key: "HF_TOKEN", value: "hf_xxx"}
    ]
  }) {
    id
    imageName
    machineId
    desiredStatus
  }
}

# Create spot (interruptible) pod
mutation CreateSpotPod {
  podRentInterruptable(input: {
    name: "spot-training"
    imageName: "runpod/pytorch:latest"
    gpuTypeId: "NVIDIA A100 80GB PCIe"
    cloudType: COMMUNITY
    gpuCount: 1
    bidPerGpu: 0.50  # Max price you'll pay
    volumeInGb: 30
    containerDiskInGb: 20
  }) {
    id
    desiredStatus
    costPerHr
  }
}

# Stop a pod
mutation StopPod($podId: String!) {
  podStop(input: {podId: $podId}) {
    id
    desiredStatus
  }
}

# Resume a stopped pod
mutation ResumePod($podId: String!, $gpuCount: Int!) {
  podResume(input: {podId: $podId, gpuCount: $gpuCount}) {
    id
    desiredStatus
    lastStatusChange
  }
}

# Terminate a pod (irreversible)
mutation TerminatePod($podId: String!) {
  podTerminate(input: {podId: $podId})
}

# Create network volume
mutation CreateVolume {
  saveNetworkVolume(input: {
    name: "model-weights"
    size: 100
    dataCenterId: "US-TX-3"
  }) {
    id
    name
    size
    dataCenterId
  }
}

# Delete network volume
mutation DeleteVolume($volumeId: String!) {
  deleteNetworkVolume(input: {id: $volumeId})
}

# Create serverless endpoint
mutation CreateEndpoint {
  saveEndpoint(input: {
    name: "my-llm-endpoint"
    templateId: "template-abc123"
    gpuIds: "NVIDIA GeForce RTX 4090"
    workersMin: 0
    workersMax: 3
    idleTimeout: 5
    scalerType: QUEUE_DELAY
    scalerValue: 4
    networkVolumeId: "vol-abc123"
  }) {
    id
    name
    type
  }
}
```

### Python Examples

```python
# Create pod via GraphQL
mutation = """
mutation {
  podFindAndDeployOnDemand(input: {
    name: "%s"
    imageName: "%s"
    gpuTypeId: "NVIDIA GeForce RTX 4090"
    cloudType: SECURE
    gpuCount: 1
    volumeInGb: 50
    containerDiskInGb: 20
    ports: "8888/http,22/tcp"
  }) {
    id
    imageName
    desiredStatus
  }
}
""" % (pod_name, image_name)

result = graphql(mutation)
pod_id = result["podFindAndDeployOnDemand"]["id"]
print(f"Created pod: {pod_id}")

# List pods
pods_query = """
query {
  myself {
    pods {
      id
      name
      desiredStatus
      runtime { uptimeInSeconds }
    }
  }
}
"""
pods = graphql(pods_query)["myself"]["pods"]
for pod in pods:
    print(f"{pod['id']}: {pod['name']} ({pod['desiredStatus']})")
```

---

## REST API (Serverless Job Management)

### Authentication

```bash
# Authorization header (recommended)
curl -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
     https://api.runpod.io/v2/{endpoint_id}/health
```

### Endpoints

#### POST /run — Submit Async Job

```bash
curl -X POST "https://api.runpod.io/v2/{ENDPOINT_ID}/run" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "What is 2+2?",
      "max_new_tokens": 100,
      "temperature": 0.7
    },
    "webhook": "https://your-server.com/webhook"
  }'

# Response:
# {"id": "sync-abc123", "status": "IN_QUEUE"}
```

#### POST /runsync — Submit Sync Job (Wait up to 90s)

```bash
curl -X POST "https://api.runpod.io/v2/{ENDPOINT_ID}/runsync" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Hello!"}}' \
  --max-time 120

# Response (if completed within 90s):
# {"id": "sync-abc123", "status": "COMPLETED", "output": {...}, "executionTime": 2340}

# Response (if exceeded 90s):
# {"id": "sync-abc123", "status": "IN_PROGRESS"}
# Then poll /status/{job_id}
```

#### GET /status/{job_id} — Check Job Status

```bash
curl "https://api.runpod.io/v2/{ENDPOINT_ID}/status/{JOB_ID}" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"

# Response:
# {
#   "id": "job-abc123",
#   "status": "COMPLETED",      # IN_QUEUE | IN_PROGRESS | COMPLETED | FAILED | CANCELLED | TIMED_OUT
#   "output": {"generated_text": "The answer is 4."},
#   "executionTime": 2340,      # milliseconds
#   "delayTime": 150,           # Queue wait time in ms
#   "retries": 0
# }
```

#### POST /cancel/{job_id} — Cancel Job

```bash
curl -X POST "https://api.runpod.io/v2/{ENDPOINT_ID}/cancel/{JOB_ID}" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"
```

#### GET /stream/{job_id} — Stream Results

For generator handlers, poll streaming results:

```bash
curl "https://api.runpod.io/v2/{ENDPOINT_ID}/stream/{JOB_ID}" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"

# Response includes partial results as they're yielded
```

#### POST /purge-queue — Clear Job Queue

```bash
curl -X POST "https://api.runpod.io/v2/{ENDPOINT_ID}/purge-queue" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"
```

#### GET /health — Endpoint Health

```bash
curl "https://api.runpod.io/v2/{ENDPOINT_ID}/health" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"

# Response:
# {
#   "jobs": {
#     "completed": 1523,
#     "failed": 2,
#     "inProgress": 1,
#     "inQueue": 0,
#     "retried": 0
#   },
#   "workers": {
#     "idle": 2,
#     "initializing": 0,
#     "ready": 2,
#     "running": 1,
#     "throttled": 0
#   }
# }
```

### Job Status Values

| Status | Description |
|--------|-------------|
| `IN_QUEUE` | Job waiting for an available worker |
| `IN_PROGRESS` | Worker is actively processing |
| `COMPLETED` | Successfully finished; output available |
| `FAILED` | Handler raised an exception |
| `CANCELLED` | Cancelled by client |
| `TIMED_OUT` | Exceeded execution timeout |

### Webhook Format

When specifying a webhook URL, RunPod POSTs this JSON when the job completes:

```json
{
  "id": "job-abc123",
  "status": "COMPLETED",
  "output": {
    "generated_text": "The answer is 4."
  },
  "executionTime": 2340,
  "delayTime": 150
}
```

Your webhook endpoint must return HTTP 200. If it fails, RunPod retries up to 2 more times with 10-second delays.

### Python Client Examples

```python
import requests
import time

API_KEY = "your-api-key"
ENDPOINT_ID = "your-endpoint-id"
BASE_URL = f"https://api.runpod.io/v2/{ENDPOINT_ID}"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def submit_job(input_data):
    """Submit async job and return job ID."""
    response = requests.post(
        f"{BASE_URL}/run",
        json={"input": input_data},
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()["id"]

def wait_for_job(job_id, poll_interval=1.0, timeout=300):
    """Poll until job completes, return output."""
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(
            f"{BASE_URL}/status/{job_id}",
            headers=HEADERS
        )
        result = response.json()
        status = result["status"]
        
        if status == "COMPLETED":
            return result["output"]
        elif status in ("FAILED", "CANCELLED", "TIMED_OUT"):
            raise RuntimeError(f"Job {job_id} ended with status: {status}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

# Usage
job_id = submit_job({"prompt": "What is 2+2?", "max_new_tokens": 50})
output = wait_for_job(job_id)
print(output)

# Synchronous (one-liner, up to 90 seconds)
sync_response = requests.post(
    f"{BASE_URL}/runsync",
    json={"input": {"prompt": "Hello!"}},
    headers=HEADERS,
    timeout=120
).json()

if sync_response["status"] == "COMPLETED":
    print(sync_response["output"])
else:
    # Timed out - fall back to polling
    output = wait_for_job(sync_response["id"])
    print(output)
```

---

## REST API for Pod Management (Newer API)

RunPod also offers a REST API for pod management (in addition to GraphQL):

```bash
# Create pod
curl -X POST "https://api.runpod.io/v1/pods" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-pod",
    "imageName": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
    "gpuTypeId": "NVIDIA GeForce RTX 4090",
    "cloudType": "SECURE",
    "gpuCount": 1
  }'

# Get pod status
curl "https://api.runpod.io/v1/pods/{pod_id}" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"

# Stop pod
curl -X POST "https://api.runpod.io/v1/pods/{pod_id}/stop" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"

# Terminate pod
curl -X DELETE "https://api.runpod.io/v1/pods/{pod_id}" \
  -H "Authorization: Bearer ${RUNPOD_API_KEY}"
```

Note: The REST API for pod management is newer and may not have feature parity with GraphQL. Use GraphQL for complex operations.
