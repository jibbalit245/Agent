# Vertex AI Batch Predictions

> Source: https://cloud.google.com/vertex-ai/docs/predictions/batch-predictions
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from Vertex AI Python SDK documentation and official knowledge base.
> Fetched: 2026-06-20

## Overview

Batch predictions process large volumes of data asynchronously without requiring a deployed endpoint. Use batch predictions when you need to:

- Process large datasets (thousands to millions of records)
- Don't require real-time responses (asynchronous results)
- Optimize costs (typically 50% discount vs. online predictions)
- Run inference on scheduled intervals

## When to Use Batch vs. Online Predictions

| Feature | Batch Predictions | Online Predictions |
|---------|------------------|--------------------|
| Latency | Minutes to hours | Milliseconds to seconds |
| Scale | Very large (millions of records) | Lower concurrency |
| Cost | Lower (50% discount) | Higher |
| Response | Async, written to GCS/BigQuery | Synchronous |
| Infrastructure | No endpoint needed | Requires deployed endpoint |
| Best for | Bulk processing, nightly jobs | Real-time applications |

## Batch Prediction with Generative AI Models (GenAI SDK)

### BigQuery Source and Destination

```python
from google import genai
from google.genai import types
import time

client = genai.Client(vertexai=True, project='my-project', location='us-central1')

# Create batch job from BigQuery table
job = client.batches.create(
    model='gemini-2.5-flash',
    src='bq://my-project.my-dataset.input-table',
    config=types.CreateBatchJobConfig(
        dest='bq://my-project.my-dataset.output-table',
    )
)

print(f"Batch job created: {job.name}")
print(f"State: {job.state}")

# Poll for completion
completed_states = {
    'JOB_STATE_SUCCEEDED',
    'JOB_STATE_FAILED',
    'JOB_STATE_CANCELLED',
    'JOB_STATE_PAUSED',
}

while job.state not in completed_states:
    print(f"Current state: {job.state}")
    job = client.batches.get(name=job.name)
    time.sleep(30)

print(f"Job completed with state: {job.state}")
```

### GCS Source and Destination

```python
from google import genai
from google.genai import types
import time

client = genai.Client(vertexai=True, project='my-project', location='us-central1')

# Create batch job from GCS JSONL file
job = client.batches.create(
    model='gemini-2.5-flash',
    src='gs://my-bucket/input-requests.jsonl',
    config=types.CreateBatchJobConfig(
        dest='gs://my-bucket/output-results/',
    )
)

# Wait for completion
completed_states = {
    'JOB_STATE_SUCCEEDED',
    'JOB_STATE_FAILED', 
    'JOB_STATE_CANCELLED',
}

while job.state not in completed_states:
    job = client.batches.get(name=job.name)
    time.sleep(60)

print(f"Final state: {job.state}")
```

### Input File Format (JSONL for GCS)

Each line in the JSONL file is one prediction request:

```jsonl
{"request": {"contents": [{"role": "user", "parts": [{"text": "What is the capital of France?"}]}]}}
{"request": {"contents": [{"role": "user", "parts": [{"text": "Write a haiku about mountains."}]}]}}
{"request": {"contents": [{"role": "user", "parts": [{"text": "Explain quantum entanglement simply."}]}]}}
```

With generation config:
```jsonl
{"request": {"contents": [{"role": "user", "parts": [{"text": "Summarize: ..."}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500}}}
```

### BigQuery Input Table Schema

For BigQuery input, the table must have a `request` column (JSON):

```sql
CREATE TABLE my-dataset.input-table (
  request JSON
);

INSERT INTO my-dataset.input-table VALUES
  (JSON '{"contents": [{"role": "user", "parts": [{"text": "What is AI?"}]}]}'),
  (JSON '{"contents": [{"role": "user", "parts": [{"text": "Explain ML."}]}]}');
```

### List Batch Jobs

```python
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project='my-project', location='us-central1')

# List all batch jobs
for job in client.batches.list(config=types.ListBatchJobsConfig(page_size=10)):
    print(f"{job.name}: {job.state}")

# Paginated
pager = client.batches.list(config=types.ListBatchJobsConfig(page_size=10))
print(pager[0])
pager.next_page()
```

### Delete a Batch Job

```python
client.batches.delete(name=job.name)
```

## Batch Prediction with Custom/AutoML Models

### Using the Vertex AI Python SDK

```python
from google.cloud import aiplatform

aiplatform.init(project='my-project', location='us-central1')

model = aiplatform.Model('projects/my-project/locations/us-central1/models/MODEL_ID')

# Create batch prediction job
batch_prediction_job = model.batch_predict(
    job_display_name='my-batch-prediction-job',
    gcs_source=['gs://path/to/my/input.jsonl'],
    gcs_destination_prefix='gs://path/to/output/',
    instances_format='jsonl',
    predictions_format='jsonl',
    machine_type='n1-standard-4',
    service_account='my-sa@my-project.iam.gserviceaccount.com',
    sync=True  # Wait for completion (set to False for async)
)
```

### Asynchronous Batch Prediction

```python
# Start job without waiting
batch_prediction_job = model.batch_predict(
    job_display_name='my-batch-job',
    gcs_source=['gs://my-bucket/input.jsonl'],
    gcs_destination_prefix='gs://my-bucket/output/',
    machine_type='n1-standard-4',
    sync=False  # Non-blocking
)

# Wait for resource creation (faster than wait())
batch_prediction_job.wait_for_resource_creation()

# Check state
print(batch_prediction_job.state)

# Block until complete
batch_prediction_job.wait()
```

### Batch Prediction Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_display_name` | str | Name for the batch job |
| `gcs_source` | list[str] | GCS URIs for input files |
| `bigquery_source` | str | BigQuery table URI |
| `gcs_destination_prefix` | str | GCS prefix for output |
| `bigquery_destination_prefix` | str | BigQuery dataset URI |
| `instances_format` | str | `'jsonl'`, `'csv'`, `'bigquery'`, `'file-list'` |
| `predictions_format` | str | `'jsonl'`, `'csv'`, `'bigquery'` |
| `machine_type` | str | Machine type for processing |
| `accelerator_type` | str | Optional GPU type |
| `accelerator_count` | int | Number of GPUs |
| `starting_replica_count` | int | Initial replica count |
| `max_replica_count` | int | Maximum replica count |
| `service_account` | str | Service account email |
| `sync` | bool | Wait for completion |
| `model_parameters` | dict | Model-specific parameters |

### Input/Output Formats

**JSONL (JSON Lines):**
```json
{"instances": [{"feature1": 1.0, "feature2": "value"}]}
{"instances": [{"feature1": 2.0, "feature2": "other"}]}
```

**CSV:**
```csv
feature1,feature2,feature3
1.0,value,true
2.0,other,false
```

**BigQuery source:**
```python
batch_prediction_job = model.batch_predict(
    job_display_name='bq-batch-job',
    bigquery_source='bq://my-project.my-dataset.input-table',
    bigquery_destination_prefix='bq://my-project.my-dataset',
    instances_format='bigquery',
    predictions_format='bigquery',
    machine_type='n1-standard-4',
)
```

### REST API

Create batch prediction job:
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/batchPredictionJobs" \
  -d '{
    "displayName": "my-batch-job",
    "model": "projects/PROJECT_ID/locations/us-central1/models/MODEL_ID",
    "inputConfig": {
      "instancesFormat": "jsonl",
      "gcsSource": {
        "uris": ["gs://my-bucket/input.jsonl"]
      }
    },
    "outputConfig": {
      "predictionsFormat": "jsonl",
      "gcsDestination": {
        "outputUriPrefix": "gs://my-bucket/output/"
      }
    },
    "dedicatedResources": {
      "machineSpec": {
        "machineType": "n1-standard-4"
      },
      "startingReplicaCount": 1,
      "maxReplicaCount": 5
    }
  }'
```

List batch prediction jobs:
```bash
curl -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/batchPredictionJobs"
```

### gcloud CLI

```bash
# Create batch prediction job
gcloud ai batch-prediction-jobs create \
  --region=us-central1 \
  --display-name=my-batch-job \
  --model=MODEL_ID \
  --input-paths='gs://my-bucket/input.jsonl' \
  --input-format=jsonl \
  --output-path='gs://my-bucket/output/' \
  --output-format=jsonl \
  --machine-type=n1-standard-4

# List batch jobs
gcloud ai batch-prediction-jobs list --region=us-central1

# Describe a job
gcloud ai batch-prediction-jobs describe JOB_ID --region=us-central1

# Cancel a job
gcloud ai batch-prediction-jobs cancel JOB_ID --region=us-central1
```

## Job States

| State | Description |
|-------|-------------|
| `JOB_STATE_QUEUED` | Job waiting to start |
| `JOB_STATE_PENDING` | Job is being prepared |
| `JOB_STATE_RUNNING` | Job is executing |
| `JOB_STATE_SUCCEEDED` | Job completed successfully |
| `JOB_STATE_FAILED` | Job failed |
| `JOB_STATE_CANCELLING` | Job is being cancelled |
| `JOB_STATE_CANCELLED` | Job was cancelled |
| `JOB_STATE_PAUSED` | Job is paused |

## Output Format

### JSONL Output

```json
{"instance": {"feature1": 1.0}, "prediction": {"scores": [0.9, 0.1], "classes": ["cat", "dog"]}, "status": ""}
{"instance": {"feature1": 2.0}, "prediction": {"scores": [0.2, 0.8], "classes": ["cat", "dog"]}, "status": ""}
```

### BigQuery Output

The output table contains these columns:
- All input columns (copied from source)
- `prediction` column (STRUCT with model outputs)
- `status` column (empty if successful, error message if failed)

## Monitoring Batch Jobs

### Console

Navigate to: Vertex AI > Batch Predictions in Cloud Console

### Python SDK

```python
# Refresh job state
batch_prediction_job.refresh()
print(f"State: {batch_prediction_job.state}")
print(f"Completion %: {batch_prediction_job.completion_stats}")

# Get errors
if batch_prediction_job.has_error:
    print(f"Error: {batch_prediction_job.error}")
```

### Batch Job Completion Statistics

```python
stats = batch_prediction_job.completion_stats
print(f"Successful count: {stats.successful_count}")
print(f"Failed count: {stats.failed_count}")
print(f"Incomplete count: {stats.incomplete_count}")
```

## Cost Optimization

### Batch Discounts

- Batch predictions typically cost **50% less** than equivalent online predictions
- For Gemini models, see the Flex/Batch tier pricing in the pricing documentation

### Resource Optimization

```python
# Start with fewer replicas, allow scaling
batch_prediction_job = model.batch_predict(
    job_display_name='optimized-batch-job',
    gcs_source=['gs://my-bucket/input.jsonl'],
    gcs_destination_prefix='gs://my-bucket/output/',
    machine_type='n1-standard-4',
    starting_replica_count=1,
    max_replica_count=10,  # Will auto-scale as needed
)
```

## Error Handling

```python
from google.api_core import exceptions

try:
    batch_prediction_job = model.batch_predict(
        job_display_name='my-job',
        gcs_source=['gs://my-bucket/input.jsonl'],
        gcs_destination_prefix='gs://my-bucket/output/',
        machine_type='n1-standard-4',
    )
except exceptions.GoogleAPIError as e:
    print(f"Error creating batch job: {e}")

# Check for job-level errors after completion
if batch_prediction_job.state == 'JOB_STATE_FAILED':
    print(f"Job failed: {batch_prediction_job.error}")
```

## Quotas and Limits

| Resource | Default Limit |
|----------|--------------|
| Batch prediction jobs per project | 100 active jobs |
| Maximum input file size | No specific limit (GCS) |
| Maximum input rows (BigQuery) | No specific limit |
| Job timeout | 7 days |
| Maximum output file size | No specific limit |

## Related Resources

- Online Predictions (Endpoints): https://cloud.google.com/vertex-ai/docs/predictions/get-online-predictions
- Pricing: https://cloud.google.com/vertex-ai/generative-ai/pricing
- Batch Prediction API reference: https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.batchPredictionJobs
