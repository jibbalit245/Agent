# Vertex AI Online Predictions (Endpoints)

> Source: https://cloud.google.com/vertex-ai/docs/predictions/get-online-predictions
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from Vertex AI Python SDK documentation and official knowledge base.
> Fetched: 2026-06-20

## Overview

Online predictions (also called real-time predictions) are synchronous requests that return low-latency responses. Use online predictions when you need:
- Real-time or near-real-time inference
- Low-latency responses (typically < 1 second)
- Interactive applications

Vertex AI endpoints are managed infrastructure that hosts one or more deployed models and serves predictions.

## Endpoint Concepts

- **Endpoint**: A managed resource that receives and routes prediction requests
- **Deployed Model**: A model version deployed to an endpoint
- **Traffic Split**: Percentage of traffic routed to each deployed model (useful for A/B testing)
- **Machine Type**: Compute resources allocated for serving

## Creating an Endpoint

### Using the Python SDK

```python
from google.cloud import aiplatform

aiplatform.init(project='my-project', location='us-central1')

# Create a new endpoint
endpoint = aiplatform.Endpoint.create(
    display_name='my-endpoint',
    project='my-project',
    location='us-central1',
)

print(f"Endpoint created: {endpoint.resource_name}")
```

### Using gcloud CLI

```bash
gcloud ai endpoints create \
  --region=us-central1 \
  --display-name=my-endpoint
```

### Using REST API

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/endpoints" \
  -d '{
    "displayName": "my-endpoint"
  }'
```

## Deploying a Model to an Endpoint

### Using the Python SDK

```python
from google.cloud import aiplatform

# Get existing model
model = aiplatform.Model('projects/my-project/locations/us-central1/models/MODEL_ID')

# Deploy to a new endpoint (auto-creates endpoint)
endpoint = model.deploy(
    deployed_model_display_name='my-deployed-model',
    machine_type='n1-standard-4',
    min_replica_count=1,
    max_replica_count=5,
    accelerator_type='NVIDIA_TESLA_K80',  # Optional GPU
    accelerator_count=1,                   # Optional GPU count
    traffic_percentage=100,
)

# Or deploy to an existing endpoint
endpoint = aiplatform.Endpoint('projects/my-project/locations/us-central1/endpoints/ENDPOINT_ID')
endpoint.deploy(
    model=model,
    deployed_model_display_name='my-deployed-model',
    machine_type='n1-standard-4',
    min_replica_count=1,
    max_replica_count=5,
    traffic_split={"0": 100},  # 100% to new model
)
```

### Machine Types for Online Prediction

| Machine Type | vCPUs | Memory | Use Case |
|-------------|-------|--------|---------|
| `n1-standard-2` | 2 | 7.5 GB | Light workloads |
| `n1-standard-4` | 4 | 15 GB | Standard |
| `n1-standard-8` | 8 | 30 GB | Memory intensive |
| `n1-standard-16` | 16 | 60 GB | High throughput |
| `n1-highcpu-8` | 8 | 7.2 GB | CPU intensive |
| `n1-highmem-4` | 4 | 26 GB | Memory intensive |
| `a2-highgpu-1g` | 12 | 85 GB | A100 GPU |
| `a2-highgpu-2g` | 24 | 170 GB | 2x A100 GPU |

### GPU Accelerator Types

| Accelerator | Type String | VRAM |
|-------------|------------|------|
| NVIDIA A100 | `NVIDIA_TESLA_A100` | 40 GB |
| NVIDIA V100 | `NVIDIA_TESLA_V100` | 16 GB |
| NVIDIA T4 | `NVIDIA_TESLA_T4` | 16 GB |
| NVIDIA K80 | `NVIDIA_TESLA_K80` | 12 GB |
| NVIDIA P100 | `NVIDIA_TESLA_P100` | 16 GB |

### Using gcloud CLI

```bash
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --region=us-central1 \
  --model=MODEL_ID \
  --display-name=my-deployed-model \
  --machine-type=n1-standard-4 \
  --min-replica-count=1 \
  --max-replica-count=5 \
  --traffic-split=0=100
```

## Getting Online Predictions

### Using the Python SDK

```python
from google.cloud import aiplatform

endpoint = aiplatform.Endpoint('projects/my-project/locations/us-central1/endpoints/ENDPOINT_ID')

# Tabular/structured data
response = endpoint.predict(
    instances=[[6.7, 3.1, 4.7, 1.5], [4.6, 3.1, 1.5, 0.2]]
)

print(f"Predictions: {response.predictions}")
print(f"Deployed model ID: {response.deployed_model_id}")
```

### Request Parameters

```python
response = endpoint.predict(
    instances=[...],           # List of prediction inputs
    parameters={'threshold': 0.5},  # Optional model-specific parameters
)
```

### Instance Formats by Model Type

**Tabular (CSV/BigQuery):**
```python
instances = [
    {'feature1': 1.0, 'feature2': 'value', 'feature3': True},
    {'feature1': 2.0, 'feature2': 'other', 'feature3': False},
]
```

**Image Classification:**
```python
import base64

with open('image.jpg', 'rb') as f:
    image_bytes = base64.b64encode(f.read()).decode('utf-8')

instances = [
    {'content': image_bytes}
]
```

**Text Classification/NLP:**
```python
instances = [
    {'content': 'This is a sample text to classify.'}
]
```

**Custom Model (arbitrary format):**
```python
instances = [
    {'input': 'custom input format defined by your model'}
]
```

### Using REST API

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/endpoints/ENDPOINT_ID:predict" \
  -d '{
    "instances": [
      {"feature1": 1.0, "feature2": "value"}
    ],
    "parameters": {}
  }'
```

### Using gcloud CLI

```bash
gcloud ai endpoints predict ENDPOINT_ID \
  --region=us-central1 \
  --json-request=request.json
```

Where `request.json`:
```json
{
  "instances": [
    {"feature1": 1.0, "feature2": "value"}
  ]
}
```

## Raw Prediction (Explain)

Get predictions with explanations:

```python
response = endpoint.explain(
    instances=[{'feature1': 1.0, 'feature2': 'value'}],
    parameters={},
)

print(response.predictions)
print(response.explanations)  # Feature attributions
```

## Traffic Splitting (A/B Testing)

Deploy multiple model versions with traffic splitting:

```python
from google.cloud import aiplatform

endpoint = aiplatform.Endpoint('projects/my-project/locations/us-central1/endpoints/ENDPOINT_ID')

# Get deployed model IDs
for deployed_model in endpoint.list_models():
    print(f"ID: {deployed_model.id}, Name: {deployed_model.display_name}")

# Split traffic 80/20 between two deployed models
endpoint.update(
    traffic_split={
        'MODEL_ID_1': 80,
        'MODEL_ID_2': 20,
    }
)
```

## Managing Endpoint Deployments

### List Endpoints

```python
from google.cloud import aiplatform

endpoints = aiplatform.Endpoint.list(
    filter='display_name="my-endpoint"',
    order_by='create_time',
    project='my-project',
    location='us-central1',
)

for ep in endpoints:
    print(f"{ep.display_name}: {ep.resource_name}")
```

### Get Endpoint

```python
endpoint = aiplatform.Endpoint('projects/my-project/locations/us-central1/endpoints/ENDPOINT_ID')
print(endpoint.traffic_split)
print(endpoint.list_models())
```

### Undeploy a Model

```python
endpoint.undeploy(deployed_model_id='DEPLOYED_MODEL_ID')

# Or undeploy all models
endpoint.undeploy_all()
```

### Delete Endpoint

```python
# Must undeploy all models first
endpoint.undeploy_all()
endpoint.delete()
```

## Autoscaling Configuration

```python
endpoint.deploy(
    model=model,
    machine_type='n1-standard-4',
    min_replica_count=1,    # Always keep at least 1 replica
    max_replica_count=10,   # Scale up to 10 replicas
    # Scales based on CPU utilization (default target: 60%)
)
```

For GPU-accelerated endpoints:
```python
endpoint.deploy(
    model=model,
    machine_type='a2-highgpu-1g',
    accelerator_type='NVIDIA_TESLA_A100',
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=3,
)
```

## Private Endpoints

For VPC-peered private endpoints:

```python
endpoint = aiplatform.PrivateEndpoint.create(
    display_name='my-private-endpoint',
    network='projects/PROJECT_NUMBER/global/networks/VPC_NAME',
    project='my-project',
    location='us-central1',
)
```

## Monitoring Predictions

### Enable Request/Response Logging

```python
from google.cloud import aiplatform
from google.cloud.aiplatform_v1.types import endpoint as endpoint_pb

endpoint.update(
    predict_request_response_logging_config=endpoint_pb.PredictRequestResponseLoggingConfig(
        enabled=True,
        sampling_rate=0.5,  # Log 50% of requests
        bigquery_destination=endpoint_pb.BigQueryDestination(
            output_uri='bq://project.dataset.table'
        ),
    )
)
```

### View Prediction Metrics

- Navigate to Cloud Console > Vertex AI > Endpoints > [Endpoint Name] > Monitoring
- Or use Cloud Monitoring with metrics under `aiplatform.googleapis.com/endpoint/`

Key metrics:
- `prediction/latencies` - Prediction latency percentiles
- `prediction/request_count` - Number of prediction requests
- `prediction/error_count` - Number of errors
- `replica_count` - Current number of replicas

## SLA and Latency Targets

| Scenario | Target Latency |
|----------|---------------|
| Online prediction (tabular) | < 200ms p99 |
| Online prediction (custom model) | Depends on model |
| Cold start (scale from 0) | 30-90 seconds |
| Warm start | < 5 seconds additional |

## Vertex AI Prediction Quotas

| Quota | Default |
|-------|---------|
| Online prediction requests per minute | 30,000 |
| Endpoint nodes per region | 100 |
| Deployed models per endpoint | 50 |
| Models per region | 1,000 |

## Error Handling

```python
from google.api_core import exceptions

try:
    response = endpoint.predict(instances=[...])
except exceptions.GoogleAPIError as e:
    print(f"Prediction failed: {e}")
except exceptions.NotFound:
    print("Endpoint not found")
except exceptions.PermissionDenied:
    print("Permission denied - check IAM roles")
```

## Related Resources

- Batch Predictions: https://cloud.google.com/vertex-ai/docs/predictions/batch-predictions
- Model Registry: https://cloud.google.com/vertex-ai/docs/model-registry/introduction
- Explainable AI: https://cloud.google.com/vertex-ai/docs/explainable-ai/overview
- Prediction Pricing: https://cloud.google.com/vertex-ai/pricing
