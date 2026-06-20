# Amazon Bedrock Advanced Features
> Source: AWS Documentation, AWS Builder Center, AWS re:Post
> Fetched: 2026-06-20

## Batch Inference

Process thousands of prompts asynchronously at 50% off on-demand pricing.

### When to Use

- Generating embeddings for large document corpora
- Bulk summarization or classification
- Offline evaluation pipelines
- Any workload that can wait up to 24 hours for results

### Input Data Format (JSONL)

Each line is a complete inference request:

**InvokeModel format** (varies per model):
```jsonl
{"recordId": "RECORD-001", "modelInput": {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": [{"role": "user", "content": "Summarize: The quick brown fox..."}]}}
{"recordId": "RECORD-002", "modelInput": {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1024, "messages": [{"role": "user", "content": "Classify the sentiment: I love this product!"}]}}
```

**Converse format** (model-agnostic, as of February 2026):
```jsonl
{"recordId": "001", "modelInput": {"messages": [{"role": "user", "content": [{"text": "What is 2+2?"}]}], "inferenceConfig": {"maxTokens": 100}}}
```

### Submitting a Batch Job

```python
import boto3
import json

bedrock = boto3.client("bedrock", region_name="us-east-1")

# 1. Upload JSONL to S3
s3 = boto3.client("s3")
s3.put_object(
    Bucket="my-batch-bucket",
    Key="input/prompts.jsonl",
    Body=b'{"recordId": "001", "modelInput": {...}}\n'
)

# 2. Create batch job
response = bedrock.create_model_invocation_job(
    jobName="batch-summarization-2024-12",
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    roleArn="arn:aws:iam::123456789012:role/BedrockBatchRole",
    
    inputDataConfig={
        "s3InputDataConfig": {
            "s3Uri": "s3://my-batch-bucket/input/",
            "s3InputFormat": "JSONL"
        }
    },
    
    outputDataConfig={
        "s3OutputDataConfig": {
            "s3Uri": "s3://my-batch-bucket/output/"
        }
    }
)

job_arn = response["jobArn"]
print(f"Batch job ARN: {job_arn}")

# 3. Monitor job status
while True:
    job = bedrock.get_model_invocation_job(jobIdentifier=job_arn)
    status = job["status"]
    print(f"Status: {status}")
    if status in ["Completed", "Failed", "Stopped"]:
        break
    time.sleep(60)

# 4. Read output from S3
# Output is in s3://my-batch-bucket/output/{job-id}/
# Each line of output JSONL: {"recordId": "001", "modelOutput": {...}}
```

### Output Format

```jsonl
{"recordId": "RECORD-001", "modelOutput": {"content": [{"type": "text", "text": "The text was about a fox..."}]}}
{"recordId": "RECORD-002", "modelOutput": {"content": [{"type": "text", "text": "Sentiment: Positive"}]}}
```

### IAM Role for Batch Jobs

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-batch-bucket",
        "arn:aws:s3:::my-batch-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-batch-bucket/output/*"
    },
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "*"
    }
  ]
}
```

---

## Provisioned Throughput

Purchase dedicated model capacity to guarantee throughput and bypass per-account quotas.

### When to Use PT

- Consistent high-volume traffic (>1M tokens/day)
- Latency SLA requirements (PT bypasses throttling queues)
- Fine-tuned custom models (require PT to deploy)

### Model Units (MUs)

One MU = one unit of processing capacity. Each model defines how many tokens/minute one MU handles.

### Creating Provisioned Throughput

```python
bedrock = boto3.client("bedrock", region_name="us-east-1")

# Create provisioned throughput
pt_response = bedrock.create_provisioned_model_throughput(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    provisionedModelName="prod-sonnet-pt",
    modelUnits=2,  # Number of model units
    commitmentDuration="ONE_MONTH"  # "NO_COMMITMENT", "ONE_MONTH", "SIX_MONTHS"
)

pt_arn = pt_response["provisionedModelArn"]
print(f"Provisioned throughput ARN: {pt_arn}")

# Use PT in inference
response = bedrock_runtime.converse(
    modelId=pt_arn,  # Use the PT ARN instead of model ID
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
```

### Commitment Costs

| Commitment | Cost vs No Commitment |
|-----------|----------------------|
| No commitment | Base rate (hourly) |
| 1-month | ~10-20% discount |
| 6-month | ~30-40% discount |

Break-even: PT is cost-effective when consistent utilization > ~60%.

---

## Cross-Region Inference

Route requests across regions for higher throughput and availability.

### How It Works

Instead of `anthropic.claude-sonnet-4-6-v1:0`, use:
- `us.anthropic.claude-sonnet-4-6-v1:0` — Routes within US regions
- `eu.anthropic.claude-sonnet-4-6-v1:0` — Routes within EU regions  
- `global.anthropic.claude-sonnet-4-6-v1:0` — Routes globally

Bedrock automatically selects the region with available capacity.

```python
# Using cross-region inference profile
response = bedrock_runtime.converse(
    modelId="us.anthropic.claude-sonnet-4-6-v1:0",  # US cross-region
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)

# Global routing (broadest availability, most redundancy)
response = bedrock_runtime.converse(
    modelId="global.anthropic.claude-sonnet-4-6",
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
```

### Benefits

- Up to 2x higher throughput vs single region
- Automatic failover if a region has capacity issues
- No additional cost vs same-region for most profiles
- Required permission: `bedrock:InvokeModel` (same as always)

### When NOT to Use Cross-Region

- Strict data residency requirements (EU data must stay in EU)
- Compliance regulations requiring specific region
- Latency-sensitive workloads (cross-region adds 10-50ms)

---

## Quotas and Limits

### Default On-Demand Quotas (Per Account, Per Region)

Quotas vary by model and account tier. Contact AWS to request increases.

| Quota Type | Typical Default | Notes |
|-----------|-----------------|-------|
| Requests per minute (RPM) | 10-60 RPM | Varies by model |
| Tokens per minute (TPM) | 40K-500K TPM | Varies by model |
| Concurrent requests | 5-20 | |
| Max input tokens | 200K (model limit) | Varies by model |
| Max output tokens | 4K-128K | Varies by model |
| Batch inference job size | 50K records | |

### Common Quota Error

```
ThrottlingException: Too many requests. Reduce the frequency of requests.
HTTP Status: 429
```

### Handling Throttling

```python
import time
import random
import boto3
from botocore.exceptions import ClientError

def invoke_with_retry(client, max_retries=5, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.converse(**kwargs)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ThrottlingException":
                if attempt == max_retries - 1:
                    raise
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Throttled. Retrying in {wait_time:.1f}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise

# Usage
response = invoke_with_retry(
    bedrock_runtime,
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    messages=[{"role": "user", "content": [{"text": "Hello"}]}]
)
```

### Token Reservation

Bedrock reserves quota based on `max_tokens`, not actual tokens generated. If you set `max_tokens=4096`, it reserves 4096 tokens against your TPM quota even if the response is only 100 tokens.

Optimization: Set `max_tokens` to a realistic upper bound, not the model's max.

### Checking Current Quotas

```bash
# Via AWS CLI
aws service-quotas list-service-quotas --service-code bedrock --region us-east-1

# Via Console
# AWS Console > Service Quotas > Amazon Bedrock
```

### Requesting Quota Increases

```python
sq = boto3.client("service-quotas", region_name="us-east-1")

response = sq.request_service_quota_increase(
    ServiceCode="bedrock",
    QuotaCode="L-XXXXXXXXXX",  # Get quota code from list-service-quotas
    DesiredValue=100  # New quota value
)
```

---

## Model Evaluation

Test and compare model performance before committing to one.

### Automatic Evaluation

```python
bedrock = boto3.client("bedrock", region_name="us-east-1")

response = bedrock.create_evaluation_job(
    jobName="model-comparison-eval",
    jobDescription="Compare Sonnet vs Haiku on summarization tasks",
    roleArn="arn:aws:iam::123456789012:role/BedrockEvalRole",
    
    inferenceConfig={
        "models": [
            {
                "bedrockModel": {
                    "modelIdentifier": "anthropic.claude-sonnet-4-6-v1:0",
                    "inferenceParams": json.dumps({"max_tokens": 1024})
                }
            },
            {
                "bedrockModel": {
                    "modelIdentifier": "anthropic.claude-haiku-4-5-20251001-v1:0",
                    "inferenceParams": json.dumps({"max_tokens": 1024})
                }
            }
        ]
    },
    
    outputDataConfig={
        "s3Uri": "s3://my-eval-bucket/results/"
    },
    
    evaluationConfig={
        "automated": {
            "datasetMetricConfigs": [
                {
                    "taskType": "Summarization",
                    "dataset": {
                        "name": "eval-dataset",
                        "datasetLocation": {
                            "s3Uri": "s3://my-eval-bucket/eval-data.jsonl"
                        }
                    },
                    "metricNames": ["BERTScore", "Meteor"]
                }
            ]
        }
    }
)
```

---

## Common Errors and Solutions

| Error | HTTP Status | Cause | Fix |
|-------|-------------|-------|-----|
| `AccessDeniedException` | 403 | Missing IAM permissions or model not enabled | Add `bedrock:InvokeModel` permission; enable model in console |
| `ThrottlingException` | 429 | Exceeding RPM/TPM quota | Implement exponential backoff; request quota increase; use cross-region inference |
| `ModelNotReadyException` | 503 | Model is being loaded | Retry after a few seconds |
| `ModelTimeoutException` | 408 | Inference took too long | Reduce complexity; increase timeout client-side |
| `ValidationException` | 400 | Invalid request format | Check model-specific payload format; use Converse API for unified format |
| `ServiceQuotaExceededException` | 400 | Provisioned throughput limit | Scale PT model units |
| `ResourceNotFoundException` | 404 | Wrong model ID or region | Verify model ID and region; use `list_foundation_models()` |

### Debugging Tips

```python
# Log the full response for debugging
import logging
logging.getLogger('botocore').setLevel(logging.DEBUG)

# Or check response metadata
response = bedrock_runtime.converse(...)
print(response["ResponseMetadata"]["HTTPStatusCode"])
print(response["usage"])  # Token counts
print(response["metrics"])  # Latency
```
