# AWS SageMaker JumpStart — Foundation Model Deployment
> Source: https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models-latest.html, https://aws.amazon.com/blogs/machine-learning/deploy-and-fine-tune-foundation-models-in-amazon-sagemaker-jumpstart-with-two-lines-of-code/, https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-jumpstart-model.html
> Fetched: 2026-06-20

## What is SageMaker JumpStart?

SageMaker JumpStart is a hub within Amazon SageMaker that provides pre-built, pre-trained foundation models you can deploy with minimal code. It differs from Bedrock in an important way:

| | Bedrock | JumpStart |
|-|---------|-----------|
| Infrastructure | Fully serverless, AWS-managed | You manage endpoints; choose instance types |
| Customization | Limited fine-tuning for select models | Fine-tune on your data, control environment |
| Cost model | Per-token | Per-hour for endpoint uptime |
| Control | Low (managed) | High (full container access) |
| Best for | Quickest path to inference | Custom models, fine-tuning, specific instance control |

**Key consideration**: With JumpStart, you pay per endpoint-hour even when idle. An endpoint running 24/7 with no traffic still costs money. Always delete or pause endpoints when not in use.

## Deploying a Foundation Model (Python SDK)

### Install prerequisites

```bash
pip install sagemaker boto3
```

### Two-line deployment

```python
from sagemaker.jumpstart.model import JumpStartModel

model = JumpStartModel(model_id="meta-textgeneration-llama-3-3-70b-instruct")
predictor = model.deploy(accept_eula=True)  # Picks instance type automatically
```

### Explicit deployment with instance type

```python
from sagemaker.jumpstart.model import JumpStartModel
import sagemaker

role = sagemaker.get_execution_role()  # Or pass your IAM role ARN

model = JumpStartModel(
    model_id="meta-textgeneration-llama-3-3-70b-instruct",
    role=role,
    region_name="us-east-1"
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.12xlarge",
    accept_eula=True,
    endpoint_name="my-llama-endpoint"  # Optional custom name
)
```

### Invoking the endpoint

```python
payload = {
    "inputs": "What is machine learning?",
    "parameters": {
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9
    }
}

response = predictor.predict(payload)
print(response[0]["generated_text"])
```

### Using boto3 directly (after endpoint is created)

```python
import boto3
import json

runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")

response = runtime.invoke_endpoint(
    EndpointName="my-llama-endpoint",
    ContentType="application/json",
    Body=json.dumps(payload)
)

result = json.loads(response["Body"].read())
```

## Instance Types for Inference

### GPU Instances (ml.g5 family — most common for LLMs)

| Instance | GPUs | GPU Memory | vCPUs | RAM | Use Case |
|----------|------|-----------|-------|-----|----------|
| ml.g5.2xlarge | 1x A10G (24GB) | 24 GB | 8 | 32 GB | Small models (7B) |
| ml.g5.4xlarge | 1x A10G (24GB) | 24 GB | 16 | 64 GB | Small models, higher CPU |
| ml.g5.12xlarge | 4x A10G (96GB) | 96 GB | 48 | 192 GB | Medium models (13B-40B) |
| ml.g5.48xlarge | 8x A10G (192GB) | 192 GB | 192 | 768 GB | Large models (70B) |

### Inferentia Instances (ml.inf2 — cost-optimized)

| Instance | Accelerators | Accelerator Memory | Use Case |
|----------|-------------|-------------------|----------|
| ml.inf2.xlarge | 1x Inferentia2 | 32 GB | Small compiled models |
| ml.inf2.8xlarge | 1x Inferentia2 | 32 GB | Medium compiled models |
| ml.inf2.24xlarge | 6x Inferentia2 | 192 GB | Large compiled models |
| ml.inf2.48xlarge | 12x Inferentia2 | 384 GB | Very large compiled models |

**Important**: Inf2 instances require model compilation with AWS Neuron SDK. JumpStart provides pre-compiled images for supported models. Check model compatibility before choosing Inf2.

### Trainium (ml.trn1 — for training, but also inference)

Used primarily for fine-tuning. Available as ml.trn1.2xlarge, ml.trn1.32xlarge.

## Cost Management

### The Core Problem

SageMaker endpoints charge per-hour from creation to deletion, regardless of traffic. A `ml.g5.12xlarge` running 24/7 costs roughly $16–$25/day.

### Strategy 1: Delete Endpoints When Done

```python
# Always clean up after development/testing
predictor.delete_endpoint()

# Or via boto3
sm = boto3.client("sagemaker")
sm.delete_endpoint(EndpointName="my-llama-endpoint")
```

### Strategy 2: Asynchronous Endpoints (Scale to Zero)

Async endpoints automatically scale down to zero instances when there are no requests:

```python
from sagemaker.async_inference import AsyncInferenceConfig

async_config = AsyncInferenceConfig(
    output_path="s3://my-bucket/async-output/",
    max_concurrent_invocations_per_instance=4,
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.12xlarge",
    async_inference_config=async_config,
)

# Optionally configure auto-scaling to 0
# Use Application Auto Scaling with scale-in policy
```

With async endpoints and `MinCapacity=0` auto-scaling, the endpoint shuts down during idle periods.

### Strategy 3: JumpStart Cost Optimization Tool

For popular LLMs, AWS pre-benchmarks instance types. In the JumpStart console, you can select "Cost per hour" vs "Best performance" to see ranked options:

```python
from sagemaker.jumpstart.model import JumpStartModel

# JumpStart can suggest optimal instance type
model = JumpStartModel(model_id="meta-textgeneration-llama-3-3-70b-instruct")
# Check model.benchmark_metrics() for cost/performance tradeoffs
```

### Rough Cost Estimates (2025, US East)

| Instance | ~$/hr | Notes |
|----------|-------|-------|
| ml.g5.2xlarge | ~$1.50 | Single A10G, good for 7B models |
| ml.g5.12xlarge | ~$6.00 | 4x A10G, good for Falcon-40B |
| ml.g5.48xlarge | ~$20.00 | 8x A10G, needed for 70B models |
| ml.inf2.xlarge | ~$0.76 | Great cost/perf if model is compiled |

## Common Pitfalls

- **Forgetting to delete endpoints**: The most common cost overrun. Set CloudWatch billing alarms.
- **Instance too small**: Models fail to load with OOM errors. Falcon-40B needs at least `ml.g5.12xlarge`.
- **Inf2 requires Neuron compilation**: Not all JumpStart models have pre-compiled Inf2 images. Verify before choosing Inf2.
- **EULA acceptance**: Many foundation models (Llama, etc.) require `accept_eula=True` and you must accept the model license separately in the JumpStart console.
- **IAM role needs S3 access**: For async inference, the execution role must have S3 read/write permissions for the output bucket.
