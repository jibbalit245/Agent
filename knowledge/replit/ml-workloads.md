# Replit ML/AI Workloads
> Source: https://docs.replit.com, https://p0stman.com/guides/replit-limitations
> Fetched: 2026-06-20

## Overview

Replit is primarily designed as a **development and deployment environment**, not a dedicated ML infrastructure platform. Understanding its capabilities and limitations is critical for AI/ML use cases.

## GPU Availability

### Current Status (2025-2026)

**Standard Replit deployments and development Repls do NOT include GPU access.**

Replit's standard infrastructure is CPU-only:
- No CUDA/GPU acceleration by default
- No support for PyTorch GPU operations (`cuda:0` not available)
- `torch.cuda.is_available()` returns `False` in standard Repls

### GPU Beta (Limited Availability)

A GPU-enabled Repl configuration exists but is in **limited/private beta** as of 2025-2026:
- Not generally available to all users
- Available to select partners/enterprise users
- Check [replit.com/@mattatreplit/Python-Data-Science-GPU-Enabled](https://replit.com/@mattatreplit/Python-Data-Science-GPU-Enabled) for status

For serious GPU workloads, Replit is generally not the right platform — consider:
- Hugging Face Spaces (T4, A10G, A100)
- Modal (serverless GPU)
- Google Colab (free T4)
- AWS/GCP/Azure GPU instances
- Lambda Labs

## Memory and CPU Limits

### Development (Free Tier)
- **RAM**: 512 MB (hard limit; app crashes on OOM)
- **CPU**: 0.5 vCPU
- **Storage**: 1 GB (some sources say up to 10 GB, but practical limit is lower)
- **Inactivity sleep**: Repls sleep after ~5 minutes of inactivity

### Development (Core/Paid)
- Higher RAM and CPU available
- Persistent Repls (don't sleep as quickly)

### Deployment Machine Types
Up to 16 GB RAM and multiple vCPUs (see deployments.md for full table).

## ML Library Support

Replit supports installation of ML libraries via pip:

```python
# requirements.txt or direct install
pip install torch torchvision
pip install transformers
pip install numpy pandas scikit-learn
pip install sentence-transformers
pip install openai anthropic huggingface_hub
```

> **Warning**: Large libraries (PyTorch ~2GB, TensorFlow ~1GB) may hit storage limits on free tier. Consider using lighter alternatives or connecting to external APIs instead.

### Recommended Approach for Heavy ML

Instead of running models locally in Replit, **call external inference APIs**:

```python
# Instead of loading a local model (memory-intensive):
# model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")

# Use an external API (zero local memory overhead):
from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    provider="featherless-ai",
    api_key=os.environ["HF_TOKEN"],
)

response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Connecting to External AI APIs

This is the **recommended pattern** for ML workloads on Replit — offload computation to external services while Replit handles the web serving, orchestration, and UI.

### HuggingFace Inference Router

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],  # Set in Replit Secrets
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct:featherless-ai",
    messages=[{"role": "user", "content": "Summarize this text..."}],
)
```

### OpenAI API

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Anthropic Claude

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}],
)
```

### Replicate (GPU models via API)

```python
import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = os.environ["REPLICATE_TOKEN"]

output = replicate.run(
    "meta/llama-3.1-405b-instruct",
    input={"prompt": "Tell me a joke"}
)
```

## Practical ML Architecture on Replit

### Recommended Pattern: API Gateway

Build Replit as the **orchestration layer** — it handles business logic, routing, and user interaction, while AI computation runs on external GPU infrastructure:

```
User Request
    ↓
Replit App (CPU, Flask/FastAPI)
    ↓
External AI API (HuggingFace, OpenAI, Anthropic, etc.)
    ↓
Response back to Replit
    ↓
User Response
```

### What Replit Is Good At

- Building web APIs that wrap AI services
- Creating chatbot UIs (with Gradio or custom HTML)
- Orchestrating multiple AI calls
- Running lightweight NLP (small models via transformers CPU inference)
- Rapid prototyping AI-powered apps
- Deploying AI agents that call external LLM APIs

### What Replit Is NOT Good At

- Training ML models (no GPU, limited RAM)
- Fine-tuning large models locally
- Running inference on large models locally (LLaMA 7B+ needs 4-16 GB VRAM/RAM)
- High-throughput batch ML processing
- Long-running ML jobs on free tier (Repls sleep)

## Lightweight Local ML (CPU-Based)

For small models that fit in 512 MB–2 GB RAM, Replit can run them locally:

```python
# Lightweight sentence embeddings (fits in free tier)
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # ~80 MB
embeddings = model.encode(["Hello world", "Machine learning"])

# Lightweight text classification
from transformers import pipeline

classifier = pipeline("sentiment-analysis",
                       model="distilbert-base-uncased-finetuned-sst-2-english")
result = classifier("I love Replit!")
```

## Replit Agent for AI App Development

The Replit Agent itself is an AI tool that helps build apps. For AI/ML projects:

1. Describe the AI app you want: "Build a chatbot that uses the OpenAI API"
2. The agent generates the full code (Flask server, HTML frontend, API integration)
3. Configures environment variable usage (tells you which secrets to set)
4. Deploys automatically

**Known limitations of the Agent**:
- Can be slow compared to other AI app builders
- May unintentionally modify code in unintended ways
- Costs can add up with heavy Agent usage
- Free tier: 10 Agent checkpoints/month

## Storage for ML Artifacts

- **Standard Repl storage**: 1–10 GB (not suitable for large model weights)
- **For model caching**: Set `TRANSFORMERS_CACHE` or `HF_HOME` to avoid re-downloading
- **Database**: PostgreSQL via Replit DB or external (Neon, Supabase, PlanetScale)

For model weights, use HuggingFace Hub as the source and download at runtime (but this is slow on free tier due to bandwidth/storage limits).

## References

- [Replit Free Tier Limitations](https://p0stman.com/guides/replit-limitations)
- [Best REPL Environments for LLM Output (Modal Blog)](https://modal.com/resources/best-repl-environments-llm-output)
- [Replit vs Google Colab Comparison](https://www.lowcode.agency/blog/replit-vs-google-colab)
- [HuggingFace Inference Client](https://huggingface.co/docs/huggingface_hub/en/guides/inference)
