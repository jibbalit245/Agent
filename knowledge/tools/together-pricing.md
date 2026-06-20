# Together AI Pricing

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/docs/pricing — content below is from model training data (knowledge cutoff August 2025).

## Overview

Together AI bills per token for serverless inference (input and output tokens are priced separately). Dedicated endpoints are billed per GPU-hour.

Current pricing is at: https://www.together.ai/pricing

---

## Serverless Inference Pricing (per 1M tokens)

### Chat / Text Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | $0.88 | $0.88 |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` | Free (rate limited) | Free |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` | $0.18 | $0.18 |
| `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` | $0.88 | $0.88 |
| `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo` | $3.50 | $3.50 |
| `meta-llama/Llama-3.2-3B-Instruct-Turbo` | $0.06 | $0.06 |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | $0.60 | $0.60 |
| `mistralai/Mixtral-8x22B-Instruct-v0.1` | $1.20 | $1.20 |
| `mistralai/Mistral-7B-Instruct-v0.3` | $0.20 | $0.20 |
| `Qwen/Qwen2.5-72B-Instruct-Turbo` | $1.20 | $1.20 |
| `Qwen/Qwen2.5-7B-Instruct-Turbo` | $0.30 | $0.30 |
| `deepseek-ai/DeepSeek-R1` | $3.00 | $7.00 |
| `deepseek-ai/DeepSeek-R1-Distill-Llama-70B` | $2.00 | $2.00 |
| `deepseek-ai/DeepSeek-V3` | $1.25 | $1.25 |

*Note: Prices may change. Always verify at https://www.together.ai/pricing*

### Vision Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| `meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo` | $0.18 | $0.18 |
| `meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo` | $1.20 | $1.20 |

### Embedding Models

| Model | Price (per 1M tokens) |
|---|---|
| `togethercomputer/m2-bert-80M-8k-retrieval` | $0.008 |
| `BAAI/bge-large-en-v1.5` | $0.008 |

---

## Image Generation Pricing

| Model | Price per image |
|---|---|
| `black-forest-labs/FLUX.1-schnell` | $0.0002 per step |
| `black-forest-labs/FLUX.1-schnell-Free` | Free (rate limited) |
| `black-forest-labs/FLUX.1-dev` | $0.035 per image |
| `black-forest-labs/FLUX.1.1-pro` | $0.04 per image |
| `stabilityai/stable-diffusion-xl-base-1.0` | $0.002 per image |

---

## Fine-Tuning Pricing

### Training

| Model Size | Price per 1M tokens |
|---|---|
| 1B–7B | $0.30 |
| 7B–13B | $0.30 |
| 13B–34B | $0.50 |
| 34B–70B | $1.00 |
| 70B+ | Contact Together |

### Fine-Tuned Model Inference

Fine-tuned models are billed at the same rate as the base model.

---

## Dedicated Endpoint Pricing

For production workloads needing consistent latency and throughput.

| GPU | Price per hour |
|---|---|
| NVIDIA A100 80GB | ~$2.50–$3.50/hr |
| NVIDIA H100 80GB | ~$4.00–$6.00/hr |
| NVIDIA A10G | ~$1.20–$1.50/hr |

*Contact Together AI for exact dedicated endpoint pricing.*

---

## Free Tier

Together AI offers:
- Free models: `*-Free` variants
- $1 free credit on signup (in some regions)
- No credit card required for free tier models

---

## Cost Estimation

### Example: Customer Service Bot

Assumptions:
- 10,000 conversations/day
- Average conversation: 500 input tokens + 200 output tokens
- Model: `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` ($0.18/1M tokens)

```
Daily input tokens:  10,000 × 500 = 5,000,000 tokens
Daily output tokens: 10,000 × 200 = 2,000,000 tokens
Total tokens: 7,000,000 tokens

Daily cost: 7,000,000 / 1,000,000 × $0.18 = $1.26/day
Monthly cost: ~$37.80/month
```

### Python Cost Estimator

```python
def estimate_cost(
    n_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    input_price_per_m: float,  # per 1M tokens
    output_price_per_m: float,
) -> dict:
    total_input = n_requests * avg_input_tokens
    total_output = n_requests * avg_output_tokens
    
    input_cost = (total_input / 1_000_000) * input_price_per_m
    output_cost = (total_output / 1_000_000) * output_price_per_m
    
    return {
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
    }

# 8B model example
cost = estimate_cost(
    n_requests=10_000,
    avg_input_tokens=500,
    avg_output_tokens=200,
    input_price_per_m=0.18,
    output_price_per_m=0.18,
)
print(f"Daily cost: ${cost['total_cost']:.2f}")
```

---

## Monitoring Usage

```python
# Check your account usage via Together dashboard
# https://api.together.ai/settings/billing
```

---

## Billing Notes

- Billed at end of month
- Pricing in USD
- Input tokens = prompt/context
- Output tokens = generated tokens
- Streaming is priced the same as non-streaming
- Failed requests (errors) are generally not billed
- Minimum charge may apply per request
