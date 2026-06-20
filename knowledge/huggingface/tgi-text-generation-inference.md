# HuggingFace TGI — Text Generation Inference
> Sources: https://github.com/huggingface/text-generation-inference, https://huggingface.co/docs/text-generation-inference/en/index, https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/consuming_tgi, https://github.com/huggingface/text-generation-inference/blob/main/docs/source/basic_tutorials/gated_model_access.md, https://huggingface.co/docs/text-generation-inference/en/conceptual/quantization, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

Text Generation Inference (TGI) is HuggingFace's production-grade Rust+Python+gRPC server for deploying Large Language Models. It powers HuggingFace Chat and is widely used for self-hosting LLMs.

**IMPORTANT: TGI entered maintenance mode on March 21, 2026.** The project now focuses on bug fixes and documentation. For new deployments, HuggingFace recommends downstream engines like **vLLM** or **SGLang**. Existing TGI deployments continue to work.

---

## Key Features

- **Token streaming** via Server-Sent Events (SSE)
- **Continuous batching** of requests (high throughput)
- **Tensor parallelism** across multiple GPUs
- **Flash Attention** and **Paged Attention** optimizations
- **OpenAI-compatible API** (`/v1/chat/completions`)
- **Speculation** (speculative decoding, ~2x latency improvement)
- **Multiple quantization formats**: bitsandbytes, GPTQ, AWQ, Marlin, EETQ, fp8
- **Structured output** / JSON grammar enforcement
- **OpenTelemetry** distributed tracing + **Prometheus** metrics
- **Stop sequences**, logit warping, log probabilities
- **AMD GPU support** (ROCm)
- **AWS Inferentia**, Intel GPUs, Google TPU support

---

## Supported Hardware

| Hardware | Image/Config |
|----------|-------------|
| NVIDIA GPUs | `ghcr.io/huggingface/text-generation-inference:3.3.5` |
| AMD GPUs (ROCm) | `ghcr.io/huggingface/text-generation-inference:3.3.5-rocm` |
| AWS Inferentia2 | Special Neuron build |
| Intel GPUs | Special Intel build |
| Google TPU | via optimum-tpu |
| CPU-only | Slower but works |

---

## Docker Quick Start

### Basic (public model)

```bash
model=HuggingFaceH4/zephyr-7b-beta
volume=$PWD/data  # Cache models locally

docker run --gpus all \
  --shm-size 1g \
  -p 8080:80 \
  -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id $model
```

### With gated model (requires HF_TOKEN)

```bash
model=meta-llama/Llama-3.1-8B-Instruct
volume=$PWD/data

docker run --gpus all \
  --shm-size 1g \
  -e HF_TOKEN=$HF_TOKEN \
  -p 8080:80 \
  -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id $model
```

### Single GPU (specify GPU index)

```bash
docker run --gpus '"device=0"' \
  --shm-size 1g \
  -p 8080:80 \
  -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id meta-llama/Llama-3.1-8B-Instruct
```

### AMD GPU

```bash
docker run --device /dev/kfd --device /dev/dri \
  --shm-size 1g \
  -p 8080:80 \
  -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5-rocm \
  --model-id $model
```

### Local/custom model

```bash
docker run --gpus all \
  --shm-size 1g \
  -p 8080:80 \
  -v /path/to/models:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id /data/my-custom-model
```

---

## Configuration Parameters

Key Docker/TGI flags (passed after the image name):

| Flag | Default | Description |
|------|---------|-------------|
| `--model-id` | required | HF model ID or local path |
| `--port` | 80 | Port to listen on inside container |
| `--max-input-length` | 1024 | Max tokens in input |
| `--max-total-tokens` | 2048 | Max input + output tokens |
| `--max-batch-total-tokens` | auto | Token budget per batch |
| `--max-batch-prefill-tokens` | 4096 | Prefill budget per batch cycle |
| `--max-concurrent-requests` | 128 | Max simultaneous requests |
| `--quantize` | none | Quantization method (see below) |
| `--num-shard` | auto | Number of GPU shards (tensor parallel) |
| `--sharded` | auto | Enable tensor parallelism |
| `--dtype` | auto | `float16`, `bfloat16`, `float32` |
| `--trust-remote-code` | false | Allow custom model code |
| `--disable-flash-attn` | false | Disable Flash Attention |
| `--max-batch-prefill-tokens` | varies | Prefill phase token budget |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `HF_TOKEN` | HuggingFace token for gated models |
| `HUGGING_FACE_HUB_TOKEN` | Legacy name for HF_TOKEN |
| `MAX_INPUT_LENGTH` | Alternative to `--max-input-length` |
| `MAX_TOTAL_TOKENS` | Alternative to `--max-total-tokens` |
| `CUDA_VISIBLE_DEVICES` | Control GPU visibility |
| `RUST_LOG` | Log level (e.g., `info`, `debug`) |

---

## Quantization Options

Reduces VRAM requirements at some cost to quality/speed:

| Method | Flag | Notes |
|--------|------|-------|
| bitsandbytes INT8 | `--quantize bitsandbytes` | On-the-fly, any GPU, no pre-quantization needed |
| bitsandbytes NF4 | `--quantize bitsandbytes-nf4` | 4-bit quantization |
| bitsandbytes FP4 | `--quantize bitsandbytes-fp4` | 4-bit floating point |
| GPTQ | `--quantize gptq` | Needs pre-quantized checkpoint |
| AWQ | `--quantize awq` | Fast inference, needs pre-quantized weights |
| Marlin | `--quantize marlin` | Optimized for NVIDIA GPUs |
| EETQ | `--quantize eetq` | On-the-fly, efficient |
| fp8 | `--quantize fp8` | For H100/A100 with FP8 support |

Example with quantization:
```bash
docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id meta-llama/Llama-3.1-70B-Instruct \
  --quantize bitsandbytes-nf4
```

---

## API Endpoints

TGI exposes two API styles:

### TGI Native API

```bash
# Streaming text generation
curl 127.0.0.1:8080/generate_stream \
  -X POST \
  -d '{"inputs": "What is Deep Learning?", "parameters": {"max_new_tokens": 200}}' \
  -H 'Content-Type: application/json'

# Non-streaming
curl 127.0.0.1:8080/generate \
  -X POST \
  -d '{"inputs": "Hello, how are", "parameters": {"max_new_tokens": 20}}' \
  -H 'Content-Type: application/json'

# Health check
curl 127.0.0.1:8080/health

# Model info
curl 127.0.0.1:8080/info

# OpenAPI docs
# Go to: http://127.0.0.1:8080/docs
```

### OpenAI-Compatible API (recommended)

```bash
# Chat completions (streaming)
curl 127.0.0.1:8080/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tgi",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is machine learning?"}
    ],
    "stream": true,
    "max_tokens": 500
  }'

# With stop sequences
curl 127.0.0.1:8080/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tgi",
    "messages": [{"role": "user", "content": "Count to 5"}],
    "stop": ["6", "seven"],
    "max_tokens": 100
  }'
```

### Python Client Examples

```python
from huggingface_hub import InferenceClient
from openai import OpenAI

# Using InferenceClient (HF native)
client = InferenceClient(model="http://localhost:8080")

# Chat completion
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "What is AI?"}],
    max_tokens=200,
)
print(response.choices[0].message.content)

# Text generation
for token in client.text_generation(
    prompt="The quick brown fox",
    max_new_tokens=50,
    stream=True,
):
    print(token, end="")

# Using OpenAI client
openai_client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed",  # TGI doesn't require auth by default
)

response = openai_client.chat.completions.create(
    model="tgi",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta.content or "", end="")
```

---

## Multi-GPU Setup (Tensor Parallelism)

```bash
# Automatically uses all available GPUs
docker run --gpus all \
  --shm-size 64g \  # Larger shared memory for multi-GPU
  -p 8080:80 \
  -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id meta-llama/Llama-3.1-70B-Instruct \
  --num-shard 4  # Use 4 GPUs
```

---

## Structured Output (JSON Grammar)

```python
import json
from huggingface_hub import InferenceClient

client = InferenceClient(model="http://localhost:8080")

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "city": {"type": "string"}
    },
    "required": ["name", "age", "city"]
}

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Generate a person profile"}],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "person", "schema": schema}
    },
)
person = json.loads(response.choices[0].message.content)
```

---

## Performance Tuning

```bash
# High throughput (batch-oriented)
docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id meta-llama/Llama-3.1-8B-Instruct \
  --max-batch-prefill-tokens 16384 \   # High: more throughput, worse TTFT
  --max-concurrent-requests 512

# Low latency (interactive use)
docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id meta-llama/Llama-3.1-8B-Instruct \
  --max-batch-prefill-tokens 4096 \    # Low: better TTFT, lower throughput
  --max-concurrent-requests 64
```

---

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tgi-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tgi
  template:
    metadata:
      labels:
        app: tgi
    spec:
      containers:
      - name: tgi
        image: ghcr.io/huggingface/text-generation-inference:3.3.5
        args:
          - "--model-id"
          - "meta-llama/Llama-3.1-8B-Instruct"
          - "--max-input-length"
          - "4096"
          - "--max-total-tokens"
          - "8192"
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-secret
              key: token
        ports:
        - containerPort: 80
        resources:
          limits:
            nvidia.com/gpu: "1"
```

---

## Status (2026)

TGI is in **maintenance mode** as of March 21, 2026. For new deployments:
- **vLLM** — widely adopted, active development, excellent performance
- **SGLang** — strong structured output support, high throughput
- TGI still used in HuggingFace Inference Endpoints (backend) and many existing deployments

---

## References

- [TGI GitHub Repository](https://github.com/huggingface/text-generation-inference)
- [TGI Documentation](https://huggingface.co/docs/text-generation-inference/en/index)
- [Consuming TGI](https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/consuming_tgi)
- [Quantization Guide](https://huggingface.co/docs/text-generation-inference/en/conceptual/quantization)
- [Gated Model Access](https://github.com/huggingface/text-generation-inference/blob/main/docs/source/basic_tutorials/gated_model_access.md)
