# Mistral AI Pricing

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/getting-started/pricing/ — content below is from model training data (knowledge cutoff August 2025).

## Overview

Mistral AI bills per million tokens (input and output separately) for La Plateforme API usage. Prices are in USD.

Current pricing at: https://mistral.ai/technology/#pricing

---

## La Plateforme API Pricing (per 1M tokens)

### Premier Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| `mistral-large-latest` (`mistral-large-2411`) | $2.00 | $6.00 |
| `pixtral-large-latest` (`pixtral-large-2411`) | $2.00 | $6.00 |
| `mistral-medium-latest` | $2.70 | $8.10 |

### Efficient Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| `mistral-small-latest` (`mistral-small-2409`) | $0.20 | $0.60 |
| `open-mistral-nemo` | $0.15 | $0.15 |
| `open-mistral-7b` | $0.25 | $0.25 |
| `open-mixtral-8x7b` | $0.70 | $0.70 |
| `open-mixtral-8x22b` | $2.00 | $6.00 |

### Specialized Models

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| `codestral-latest` | $0.20 | $0.60 |
| `pixtral-12b-latest` | $0.15 | $0.15 |
| `mistral-embed` | $0.10 | — |
| `mistral-moderation-latest` | $0.10 | — |

*Note: Prices are approximate and subject to change. Always verify at https://mistral.ai/technology/#pricing*

---

## Fine-Tuning Pricing

### Training

| Tier | Price per 1M tokens |
|---|---|
| Mistral 7B fine-tuning | $2.00 |
| Mistral Small fine-tuning | $3.00 |
| Mistral Large fine-tuning | Contact Mistral |

### Fine-Tuned Model Inference

| Tier | Input | Output |
|---|---|---|
| Fine-tuned 7B | $0.25 | $0.25 |
| Fine-tuned Small | $0.20 | $0.60 |

---

## Free Tier

- Free tier available with rate limits
- No credit card required to start
- Free access to some models via le Chat (consumer product)

| Plan | Limits |
|---|---|
| Free | 1 RPM, 500K TPM (tokens per minute) |
| Development | Increased limits (paid) |
| Production | Custom / Enterprise limits |

---

## Cost Estimation

### Example: RAG Application

Assumptions:
- 1,000 queries/day
- Average query: 2,000 input tokens (context + question) + 500 output tokens
- Model: `mistral-small-latest` ($0.20 input / $0.60 output per 1M)

```
Daily input tokens:  1,000 × 2,000 = 2,000,000 tokens
Daily output tokens: 1,000 × 500 = 500,000 tokens

Input cost:  2,000,000 / 1,000,000 × $0.20 = $0.40/day
Output cost: 500,000 / 1,000,000 × $0.60 = $0.30/day
Total: $0.70/day = ~$21/month
```

### Example: Embedding for RAG

Assumptions:
- 100,000 documents to embed
- Average document: 500 tokens
- Model: `mistral-embed` ($0.10 per 1M tokens)

```
Total tokens: 100,000 × 500 = 50,000,000 tokens
Cost: 50,000,000 / 1,000,000 × $0.10 = $5.00 (one-time)
```

### Python Cost Estimator

```python
def estimate_mistral_cost(
    n_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model: str = "mistral-small-latest",
) -> dict:
    pricing = {
        "mistral-large-latest": (2.00, 6.00),
        "mistral-small-latest": (0.20, 0.60),
        "open-mistral-nemo": (0.15, 0.15),
        "open-mistral-7b": (0.25, 0.25),
        "open-mixtral-8x7b": (0.70, 0.70),
        "codestral-latest": (0.20, 0.60),
        "mistral-embed": (0.10, 0.0),
    }
    
    if model not in pricing:
        raise ValueError(f"Unknown model: {model}")
    
    input_price, output_price = pricing[model]
    
    total_input = n_requests * avg_input_tokens
    total_output = n_requests * avg_output_tokens
    
    input_cost = (total_input / 1_000_000) * input_price
    output_cost = (total_output / 1_000_000) * output_price
    
    return {
        "model": model,
        "requests": n_requests,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "input_cost_usd": round(input_cost, 4),
        "output_cost_usd": round(output_cost, 4),
        "total_cost_usd": round(input_cost + output_cost, 4),
    }

# Example
result = estimate_mistral_cost(
    n_requests=10_000,
    avg_input_tokens=500,
    avg_output_tokens=200,
    model="mistral-small-latest"
)
print(result)
# {'model': 'mistral-small-latest', 'total_cost_usd': 2.2}
```

---

## Monitoring Usage

```python
# Check usage in the Mistral console:
# https://console.mistral.ai/usage

# In code, track usage from responses:
from mistralai import Mistral

client = Mistral()
total_tokens_used = 0

response = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "Hello!"}],
)

total_tokens_used += response.usage.total_tokens
print(f"Tokens used: {response.usage.prompt_tokens} in, {response.usage.completion_tokens} out")
print(f"Running total: {total_tokens_used}")
```

---

## Batch API Pricing

Mistral may offer batch processing at discounted rates for offline workloads. Check the latest documentation for availability.

---

## Comparison with Competitors

| Provider | Model (similar quality) | Input / 1M | Output / 1M |
|---|---|---|---|
| Mistral | `mistral-large-latest` | $2.00 | $6.00 |
| OpenAI | `gpt-4o` | $2.50 | $10.00 |
| Anthropic | `claude-3-5-sonnet` | $3.00 | $15.00 |
| Google | `gemini-1.5-pro` | $1.25 | $5.00 |
| Mistral | `mistral-small-latest` | $0.20 | $0.60 |
| OpenAI | `gpt-4o-mini` | $0.15 | $0.60 |

*Prices are approximate; check each provider's pricing page for current rates.*

---

## Enterprise Plans

For high-volume usage, Mistral offers:
- Volume discounts
- Dedicated capacity
- Priority support
- Custom SLAs
- Data processing agreements (DPA)

Contact: enterprise@mistral.ai
