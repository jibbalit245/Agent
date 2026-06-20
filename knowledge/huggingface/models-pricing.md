# HuggingFace Models & Pricing
> Source: https://huggingface.co/pricing
> Fetched: 2026-06-20

## Browsing Models

The HuggingFace Hub hosts over 700,000+ models (as of 2025). Browse at [https://huggingface.co/models](https://huggingface.co/models).

### Filtering Models

Filter by:
- **Task**: text-generation, image-classification, text-to-image, translation, summarization, etc.
- **Library**: transformers, diffusers, sentence-transformers, etc.
- **Dataset**: models trained on specific datasets
- **Language**: models for specific languages
- **License**: apache-2.0, mit, llama-community, etc.
- **Other tags**: quantized, GGUF, AWQ, GPTQ, etc.

### Model Card Format

Each model on the Hub has a **model card** — a `README.md` file that documents:

```yaml
---
language:
  - en
license: apache-2.0
tags:
  - text-generation
  - transformers
datasets:
  - openwebtext
metrics:
  - perplexity
---

# Model Name

## Model Description
...

## Intended Uses & Limitations
...

## Training and Evaluation Data
...

## Training Procedure
...
```

Model cards include:
- Model description and architecture
- Intended uses and limitations
- Training data and procedure
- Evaluation results
- Example usage code
- Citation information

## Gated Models (Require Agreement)

Some models require users to **agree to terms** before downloading or running inference. Common gated models include:
- **Meta LLaMA** series (Llama 2, Llama 3, Llama 3.1, etc.)
- **Google Gemma** series
- **Mistral** models (some)
- **Black Forest Labs FLUX** (FLUX.1-dev, FLUX.1-schnell for dev)
- **Microsoft Phi** series (some)

### Accessing Gated Models

1. Find the model on HuggingFace (e.g., `meta-llama/Llama-3.1-8B-Instruct`)
2. Click "Request access" / "Agree and access repository"
3. Fill in any required form (name, organization, intended use)
4. Wait for approval (usually instant for automatic gates, may take days for manual review)
5. Your `HF_TOKEN` will then work for that model

Without accepting terms, API calls return **HTTP 403** even with a valid token.

## Inference Pricing

### Free Tier (Serverless Inference API)

Every HuggingFace user gets monthly free credits to experiment:
- Free access with rate limits (~1000 requests/day)
- Access to smaller/CPU models via `hf-inference` provider
- First-class access to the Inference Router with credits

### PRO Account ($9/month)

- $2/month of included usage credits
- Higher rate limits on the Inference Router
- ZeroGPU access for Spaces (free H200 GPU for demos)
- After credits exhausted: pay-per-request at provider rates

### Inference Provider Pricing (Pay-as-you-go)

When using the Inference Router (`router.huggingface.co/v1`), pricing is based on:
- **Compute time × hardware cost per second** at the underlying provider
- Billed to your HuggingFace account (unified billing across all providers)

Typical token-based pricing via providers (approximate, varies by provider and model):
- Small models (7B): ~$0.10–$0.20 per 1M tokens
- Medium models (70B): ~$0.50–$1.00 per 1M tokens
- Large models (400B+): ~$1.00–$5.00 per 1M tokens

See exact rates at: [https://huggingface.co/docs/inference-providers/pricing](https://huggingface.co/docs/inference-providers/pricing)

## Inference Endpoints (Dedicated)

For production workloads requiring **dedicated infrastructure** (not shared/serverless), HuggingFace offers Inference Endpoints:

### What Are Inference Endpoints?
- Fully managed, dedicated ML inference infrastructure
- Deploy any model from the Hub to a private endpoint
- Auto-scaling (including scale-to-zero)
- Private networking options (AWS VPC, Azure VNet)
- SLA guarantees

### Getting Started with Inference Endpoints
Requires:
- Active HuggingFace account
- Credit card on file

Access at: [https://ui.endpoints.huggingface.co](https://ui.endpoints.huggingface.co)

### Endpoint Pricing

Pricing is per-hour, calculated per-minute of actual use:

| Instance Type | GPU | RAM | Price/hr |
|---------------|-----|-----|----------|
| CPU (small) | — | 2 GB | ~$0.06 |
| CPU (medium) | — | 4 GB | ~$0.12 |
| T4 | 1x T4 | 14 GB | ~$0.50 |
| A10G | 1x A10G | 24 GB | ~$1.80 |
| A100 (40 GB) | 1x A100 | 80 GB | ~$4.00 |
| A100 (80 GB) | 1x A100 | 80 GB | ~$6.00 |
| Multi-GPU | varies | varies | varies |

Charges apply while endpoints are **running** (not paused/deleted). Scale-to-zero endpoints only charge when handling traffic.

### Key Features of Inference Endpoints
- Protected endpoints (token-required, IAM roles, IP filtering)
- Custom Docker images
- Warm replicas to eliminate cold starts
- Monitoring and logging
- Multiple cloud regions (AWS, Azure, GCP)

See: [https://huggingface.co/docs/inference-endpoints/en/pricing](https://huggingface.co/docs/inference-endpoints/en/pricing)

## HuggingFace Pro vs Free vs Enterprise

| Feature | Free | PRO ($9/mo) | Enterprise |
|---------|------|-------------|------------|
| Model access | Public only | Public + gated | Public + gated + private org |
| Inference credits | Limited | $2/month | Custom |
| Rate limits | Low | Higher | Highest |
| Private repos | 1 | Unlimited | Unlimited |
| ZeroGPU (Spaces) | No | Yes | Yes |
| Priority support | No | No | Yes |
| SSO/SAML | No | No | Yes |

## Popular Model Families (2025)

### Text Generation (LLMs)
- **Meta LLaMA 3.x** — Llama-3.1-8B, 70B, 405B (gated)
- **Mistral/Mixtral** — Mistral-7B, Mixtral-8x7B
- **Qwen** — Qwen2.5-7B, 72B
- **DeepSeek** — DeepSeek-V3, DeepSeek-R1
- **Google Gemma** — Gemma-2B, 7B (gated)
- **Microsoft Phi** — Phi-3-mini, Phi-3-medium

### Embeddings
- **BAAI/bge** series
- **sentence-transformers/all-MiniLM** series
- **nomic-ai/nomic-embed-text**

### Image Generation
- **Stable Diffusion** series
- **FLUX.1** (black-forest-labs) — FLUX.1-schnell (free), FLUX.1-dev (gated)

## References

- [HuggingFace Models](https://huggingface.co/models)
- [Inference Providers Pricing](https://huggingface.co/docs/inference-providers/pricing)
- [Inference Endpoints](https://huggingface.co/inference-endpoints/dedicated)
- [Inference Endpoints Pricing](https://huggingface.co/docs/inference-endpoints/en/pricing)
- [HuggingFace Pricing Page](https://huggingface.co/pricing)
- [PRO Account](https://huggingface.co/pro)
- [Supported Inference Models](https://huggingface.co/inference/models)
