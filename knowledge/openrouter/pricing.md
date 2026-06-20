# OpenRouter Pricing
> Source: https://openrouter.ai/docs/provider-routing, https://openrouter.ai/pricing
> Fetched: 2026-06-20

## How Pricing Works

OpenRouter uses a **pass-through pricing model**:
- OpenRouter charges a **5.5% platform fee** on credit purchases
- Provider token prices are passed through exactly (no per-token markup)
- You pay only for what you use — no monthly fees or minimums

## Credit System

### Buying Credits
- **Minimum purchase**: $5
- Credits are added to your account balance and consumed as you use the API
- Credits expire after **12 months of account inactivity**
- Promotional/free credits expire after **30 days**

### Unlocking Higher Limits
- Purchase **$10+ of credits** (cumulative, at any point) → daily free model limit increases from 50 to 1,000 requests/day
- Your balance does not need to stay above $10 — the purchase history is what matters

## Free Tier

No credit card required. Free models end with `:free`.

| Limit | Free (<$10 purchased) | After $10+ purchased |
|-------|----------------------|---------------------|
| Requests/minute (free models) | 20 RPM | 20 RPM |
| Requests/day (free models) | 50 | 1,000 |
| Paid model access | Yes (uses credits) | Yes |

Free models available: 28+ as of June 2026, including DeepSeek R1, DeepSeek V3, Llama 3.3 70B, Qwen3 Coder 480B, Gemma 3, and others.

## Rate Limits

Rate limits vary by model and your account tier. Key limits:

| Category | Default Limit |
|----------|--------------|
| Free models (`:free`) | 20 RPM, 50 req/day (or 1K/day with $10+ history) |
| Paid models | Varies by provider; typically 60 RPM per key |
| Custom limits | Available for high-volume users — contact OpenRouter |

OpenRouter automatically falls back to other providers if you are rate-limited by the primary provider.

## Pricing by Major Model (June 2026)

Prices shown in USD per million tokens (MTok). These are provider pass-through rates.

### Anthropic (via OpenRouter)
| Model | Input ($/MTok) | Output ($/MTok) |
|-------|---------------|-----------------|
| `anthropic/claude-fable-5` | $10.00 | $50.00 |
| `anthropic/claude-opus-4-8` | $5.00 | $25.00 |
| `anthropic/claude-sonnet-4-6` | $3.00 | $15.00 |
| `anthropic/claude-haiku-4-5` | $1.00 | $5.00 |

### OpenAI (via OpenRouter)
| Model | Input ($/MTok) | Output ($/MTok) |
|-------|---------------|-----------------|
| `openai/gpt-4o` | ~$2.50 | ~$10.00 |
| `openai/gpt-4o-mini` | ~$0.15 | ~$0.60 |

### Google (via OpenRouter)
| Model | Input ($/MTok) | Output ($/MTok) |
|-------|---------------|-----------------|
| `google/gemini-2.5-pro` | ~$1.25 | ~$10.00 |
| `google/gemini-flash-1.5` | ~$0.075 | ~$0.30 |

### DeepSeek (via OpenRouter)
| Model | Input ($/MTok) | Output ($/MTok) |
|-------|---------------|-----------------|
| `deepseek/deepseek-chat` | ~$0.27 | ~$1.10 |
| `deepseek/deepseek-r1` | ~$0.55 | ~$2.19 |

### Free Models
All `:free` models cost $0.00/token (subject to free tier rate limits).

## Checking Live Prices

OpenRouter token prices can change when providers update their rates. Always check the live pricing page:
- https://openrouter.ai/models
- https://openrouter.ai/pricing

Or via API:
```python
import requests

models = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
).json()["data"]

for model in models:
    pricing = model.get("pricing", {})
    print(f"{model['id']}: input={pricing.get('prompt')}/tok, output={pricing.get('completion')}/tok")
```

Note: API returns prices per token (not per million), so multiply by 1,000,000 for $/MTok.

## Cost Optimization Tips

1. **Use free models** for development/testing — 28+ free options available
2. **Use cheaper models for simple tasks** — Haiku or GPT-4o-mini are often sufficient
3. **Enable caching** — some providers via OpenRouter support prompt caching
4. **Use `:free` variants first** to prototype before switching to paid models
5. **Monitor usage** at https://openrouter.ai/activity to track per-model spend

## Account & Billing

- Dashboard: https://openrouter.ai/settings/credits
- Usage logs: https://openrouter.ai/activity
- No refunds on consumed credits
- API key can be scoped with spending limits per key
