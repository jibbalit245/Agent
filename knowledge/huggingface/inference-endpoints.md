# HuggingFace Inference Endpoints (Dedicated)
> Sources: https://huggingface.co/docs/inference-endpoints/pricing, https://huggingface.co/docs/inference-endpoints/en/guides/access, https://huggingface.co/docs/huggingface_hub/guides/inference_endpoints, https://huggingface.co/learn/cookbook/en/enterprise_dedicated_endpoints, https://huggingface.co/inference-endpoints/dedicated, https://www.oreateai.com/blog/decoding-hugging-face-inference-endpoints-aws-pricing-insights/, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

Inference Endpoints provide **dedicated, managed ML inference infrastructure** for production workloads. Unlike the Serverless Inference API (shared, rate-limited), Inference Endpoints give you:

- Your own dedicated compute (no cold starts, no shared queues)
- Guaranteed capacity and predictable latency
- Auto-scaling (including scale-to-zero)
- Private networking options
- Multi-cloud: AWS, Azure, GCP
- Any model from the Hub (or private models)

**Access:** https://ui.endpoints.huggingface.co

**Requires:** Active HuggingFace account + credit card on file

---

## When to Use Inference Endpoints vs Serverless

| Use Case | Use Serverless (Router) | Use Dedicated Endpoints |
|----------|------------------------|------------------------|
| Prototyping / experimentation | Yes | Overkill |
| Bursty low-volume traffic | Yes | Overkill |
| Cost-sensitive, variable load | Yes | More expensive |
| Production with SLA requirements | No | Yes |
| Need guaranteed latency | No | Yes |
| Private model (not on Hub) | Limited | Yes |
| High throughput, sustained | No | Yes |
| Private networking / VPC | No | Yes |

---

## How to Create an Endpoint

### Via UI

1. Go to https://ui.endpoints.huggingface.co
2. Click **"New Endpoint"**
3. Choose the model (Hub model ID or private model)
4. Select:
   - **Cloud provider**: AWS, Azure, GCP
   - **Region**: us-east-1, eu-west-1, etc.
   - **Instance type**: CPU, T4, A10G, A100, etc.
   - **Framework**: Transformers, TGI, Diffusers, Custom
5. Configure auto-scaling (min/max replicas)
6. Set access level: Public, Protected (token), or Private (VPC)
7. Deploy

### Via Python API (huggingface_hub)

```python
from huggingface_hub import HfApi
from huggingface_hub.inference._client import InferenceEndpointType

api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Create an endpoint
endpoint = api.create_inference_endpoint(
    name="my-llama-endpoint",
    repository="meta-llama/Llama-3.1-8B-Instruct",
    framework="text-generation-inference",
    task="text-generation",
    accelerator="gpu",
    vendor="aws",
    region="us-east-1",
    instance_size="x1",
    instance_type="nvidia-a10g",
    min_replica=0,  # Scale to zero
    max_replica=2,
    type="protected",  # "public" | "protected" | "private"
)

# Wait for it to be ready
endpoint.wait(timeout=300)
print(f"Endpoint URL: {endpoint.url}")

# Use the endpoint
client = endpoint.client()
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100,
)
```

### Via InferenceClient with Endpoint URL

```python
from huggingface_hub import InferenceClient

# Use your endpoint directly
client = InferenceClient(
    model="https://your-endpoint-name.us-east-1.aws.endpoints.huggingface.cloud",
    token="hf_xxxxxxxxxxxxxxxx",
)

response = client.chat_completion(
    messages=[{"role": "user", "content": "What is machine learning?"}],
    max_tokens=200,
)
print(response.choices[0].message.content)
```

### Via OpenAI Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-endpoint-name.us-east-1.aws.endpoints.huggingface.cloud/v1",
    api_key="hf_xxxxxxxxxxxxxxxx",
)

response = client.chat.completions.create(
    model="tgi",  # or the model name
    messages=[{"role": "user", "content": "Hello!"}],
)
```

---

## Instance Types and Pricing

Pricing is **per-minute** (shown as per-hour), based on instance type × number of replicas.

### CPU Instances

| Instance | vCPU | RAM | Price/hr |
|----------|------|-----|----------|
| Intel Sapphire Rapids (small) | 1 | 2 GB | ~$0.06 |
| Intel Sapphire Rapids (medium) | 2 | 4 GB | ~$0.12 |
| Intel Sapphire Rapids (large) | 4 | 8 GB | ~$0.24 |
| Intel Sapphire Rapids (xlarge) | 8 | 16 GB | ~$0.48 |

*Note: AWS Intel Ice Lake (intel-icl) instances deprecated July 2025*

### GPU Instances (AWS)

| Instance | GPU | VRAM | Price/hr |
|----------|-----|------|----------|
| nvidia-t4 x1 | 1x T4 | 14 GB | ~$0.50 |
| nvidia-t4 x4 | 4x T4 | 56 GB | ~$3.00 |
| nvidia-a10g x1 | 1x A10G | 24 GB | ~$1.80 |
| nvidia-a10g x4 | 4x A10G | 96 GB | ~$7.20 |
| nvidia-a100 x1 | 1x A100 80GB | 80 GB | ~$4.00 |
| nvidia-a100 x2 | 2x A100 | 160 GB | ~$8.00 |
| nvidia-a100 x4 | 4x A100 | 320 GB | ~$16.00 |
| nvidia-h100 x1 | 1x H100 80GB | 80 GB | ~$6.00+ |

### AWS Inferentia2 (specialized for inference)

| Instance | Accelerators | Mem | Price/hr |
|----------|-------------|-----|----------|
| inf2.xlarge (x1) | 2 Inferentia2 chips | 32 GB | ~$0.75 |
| inf2.8xlarge (x4) | 8 chips | 128 GB | ~$3.00 |
| inf2.48xlarge (x12) | 24 chips | 384 GB | ~$12.00 |

---

## Cost Formula

```
Monthly cost = (hourly_rate × hours × min_replicas) 
             + (hourly_rate × scale_up_hours × additional_replicas)
```

Example: T4 endpoint with min=1 replica running 24/7:
```
$0.50/hr × 24hr × 30 days = $360/month
```

With scale-to-zero (min=0), you only pay when handling traffic.

---

## Auto-Scaling Configuration

```python
# Create with auto-scaling
endpoint = api.create_inference_endpoint(
    name="my-endpoint",
    repository="meta-llama/Llama-3.1-8B-Instruct",
    min_replica=0,    # Scale to zero when idle (no cost when idle)
    max_replica=4,    # Max 4 replicas under load
    scale_to_zero_timeout=15,  # Minutes of inactivity before scaling to zero
    # Other params...
)
```

**Scale-to-zero pros/cons:**
- Pros: No cost when idle
- Cons: Cold start latency (30–120s) when scaling from zero

**Warm replicas (min_replica > 0):**
- Always have at least N replicas ready
- Eliminates cold starts for production traffic
- Costs continuously even with no requests

---

## Endpoint Access Control

| Type | Authentication | Use case |
|------|---------------|----------|
| `public` | None (anyone can call) | Public demos |
| `protected` | HF User Access Token required | Team/org internal use |
| `private` | AWS/Azure private link | Strict enterprise security |

For `protected` endpoints:
```bash
curl https://your-endpoint.aws.endpoints.huggingface.cloud \
  -H "Authorization: Bearer hf_xxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Hello!"}'
```

---

## Inference Frameworks Supported

| Framework | Best for |
|-----------|----------|
| **TGI** (Text Generation Inference) | LLMs, chat, text generation |
| **Transformers** | Classification, NER, embeddings, any HF model |
| **Diffusers** | Image generation (Stable Diffusion, FLUX) |
| **SentenceTransformers** | Embeddings, semantic search |
| **Custom** | Docker container — any model/framework |

---

## Monitoring an Endpoint

```python
from huggingface_hub import HfApi

api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Get endpoint info
endpoint = api.get_inference_endpoint("my-endpoint")
print(endpoint.status)   # "running", "paused", "failed", etc.
print(endpoint.url)      # Endpoint URL
print(endpoint.compute)  # Instance details

# Update endpoint (e.g., scale up)
api.update_inference_endpoint(
    name="my-endpoint",
    min_replica=1,
    max_replica=8,
)

# Pause (stops billing)
api.pause_inference_endpoint("my-endpoint")

# Resume
api.resume_inference_endpoint("my-endpoint")

# Delete
api.delete_inference_endpoint("my-endpoint")

# List all your endpoints
for ep in api.list_inference_endpoints():
    print(f"{ep.name}: {ep.status} | {ep.url}")
```

---

## When Billing Applies

- **Running:** Billed per minute at instance rate × replica count
- **Paused:** No charge
- **Scaled-to-zero:** No charge
- **Building/deploying:** Check current docs (may or may not bill)
- **Failed:** No charge

---

## References

- [Inference Endpoints Overview](https://huggingface.co/inference-endpoints/dedicated)
- [Inference Endpoints Pricing](https://huggingface.co/docs/inference-endpoints/pricing)
- [Create Endpoint Guide](https://huggingface.co/docs/inference-endpoints/en/guides/access)
- [huggingface_hub Inference Endpoints Guide](https://huggingface.co/docs/huggingface_hub/guides/inference_endpoints)
- [Enterprise Dedicated Endpoints Cookbook](https://huggingface.co/learn/cookbook/en/enterprise_dedicated_endpoints)
