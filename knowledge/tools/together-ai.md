# Together AI  
> Source: https://docs.together.ai/docs/quickstart  
> Fetched: 2026-06-20

## What Is Together AI?

Together AI is a cloud inference platform providing:
- Access to 200+ open-source models (Llama, Mistral, Qwen, FLUX, etc.)
- OpenAI-compatible REST API
- Serverless inference (pay-per-token)
- Fine-tuning (PEFT/LoRA and full fine-tuning)
- Dedicated endpoint deployment
- Batch API for async workloads

New users get **$25 in free credits** to experiment.

## Quick Setup

### Get API Key

1. Sign up at [api.together.xyz](https://api.together.xyz)
2. Go to Settings → API Keys
3. Create a new key

### Install SDK

```bash
pip install together
# Or use OpenAI SDK (Together is OpenAI-compatible)
pip install openai
```

### Environment Variable

```bash
export TOGETHER_API_KEY="your-api-key-here"
```

## Python Usage — Together SDK

```python
from together import Together

client = Together()  # reads TOGETHER_API_KEY from env

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    max_tokens=512,
    temperature=0.7,
)

print(response.choices[0].message.content)
```

## Python Usage — OpenAI SDK (Compatible)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-together-api-key",
    base_url="https://api.together.xyz/v1"
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

## API Base URL

```
https://api.together.xyz/v1
```

Compatible with any OpenAI-format client.

## Streaming

```python
from together import Together

client = Together()

stream = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## Available Model Categories

### Chat/Instruction Models
- `meta-llama/Llama-3.3-70B-Instruct-Turbo` — Fast, capable 70B
- `meta-llama/Llama-3.1-405B-Instruct-Turbo` — Largest Llama
- `meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo` — Multimodal
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` — Fast/cheap
- `mistralai/Mistral-7B-Instruct-v0.3`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `Qwen/Qwen2.5-72B-Instruct-Turbo`
- `google/gemma-2-27b-it`
- `deepseek-ai/DeepSeek-V3`
- `deepseek-ai/DeepSeek-R1`

### Code Models
- `Qwen/Qwen2.5-Coder-32B-Instruct`
- `meta-llama/CodeLlama-70b-Instruct-hf`

### Embedding Models
- `togethercomputer/m2-bert-80M-8k-retrieval`
- `BAAI/bge-large-en-v1.5`

### Image Generation (FLUX)
- `black-forest-labs/FLUX.1-schnell`
- `black-forest-labs/FLUX.1.1-pro`

## Pricing (approximate, mid-2026)

| Model | Input $/1M tokens | Output $/1M tokens |
|-------|------------------|--------------------|
| Llama-3.3 70B Turbo | ~$0.88 | ~$0.88 |
| Llama-3.1 8B Turbo | ~$0.18 | ~$0.18 |
| Llama-3.1 405B Turbo | ~$3.50 | ~$3.50 |
| Mixtral 8x7B | ~$0.60 | ~$0.60 |
| DeepSeek-V3 | ~$1.25 | ~$1.25 |

Together AI pricing is often competitive vs. closed-source APIs for equivalent capability.

**Batch API**: Up to 50% lower cost than synchronous inference for async workloads (processes up to 30B tokens per model asynchronously).

## Batch API (Async Inference)

```python
from together import Together

client = Together()

# Submit batch job
job = client.batches.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    requests=[
        {"messages": [{"role": "user", "content": f"Question {i}"}]}
        for i in range(100)
    ]
)

# Poll for completion
import time
while job.status != "completed":
    time.sleep(30)
    job = client.batches.retrieve(job.id)

# Get results
results = client.batches.results(job.id)
```

## Fine-Tuning

Together AI supports fine-tuning on major model families:

```python
from together import Together

client = Together()

# Upload training data
file = client.files.upload(file=("train.jsonl", open("train.jsonl"), "application/json"))

# Start fine-tuning job
job = client.fine_tuning.create(
    training_file=file.id,
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Reference",
    n_epochs=3,
    learning_rate=1e-5,
    suffix="my-custom-model",
)

print(f"Fine-tuning job ID: {job.id}")
```

**Supported for fine-tuning**: Every major Llama, Mistral, and Qwen size (including 405B flagship).

**Fine-tuning cost**: Roughly $8-$12 per million training tokens.

## Dedicated Endpoints

For consistent latency and guaranteed capacity:

```python
# Deploy a dedicated endpoint
endpoint = client.endpoints.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    hardware="80GB A100",
    min_replicas=1,
    max_replicas=3,
)
```

GPU instances available: H100s, A100s (80GB), A100s (40GB).
On-demand H100 clusters available at ~$3.49/hour (Together Instant GPU Clusters).

## Vision / Multimodal

```python
response = client.chat.completions.create(
    model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    }]
)
```

## References

- [Together AI Docs](https://docs.together.ai/)
- [Model List](https://docs.together.ai/docs/inference-models)
- [Pricing](https://docs.together.ai/docs/inference/pricing)
- [Fine-Tuning Guide](https://docs.together.ai/docs/fine-tuning)
- [API Reference](https://docs.together.ai/reference)
