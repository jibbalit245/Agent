# Anthropic Claude API Pricing
> Source: https://www.anthropic.com/pricing
> Fetched: 2026-06-20

## Standard API Pricing (Per Million Tokens)

| Model | Input ($/MTok) | Output ($/MTok) | Ratio |
|-------|---------------|-----------------|-------|
| Claude Fable 5 | $10.00 | $50.00 | 1:5 |
| Claude Opus 4.8 | $5.00 | $25.00 | 1:5 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | 1:5 |
| Claude Haiku 4.5 | $1.00 | $5.00 | 1:5 |

Output tokens cost 5x input tokens across all current models.

## Batch API Pricing (50% Discount)

The Batch API processes requests asynchronously, typically within 24 hours.

| Model | Input ($/MTok) | Output ($/MTok) |
|-------|---------------|-----------------|
| Claude Fable 5 | $5.00 | $25.00 |
| Claude Opus 4.8 | $2.50 | $12.50 |
| Claude Sonnet 4.6 | $1.50 | $7.50 |
| Claude Haiku 4.5 | $0.50 | $2.50 |

## Prompt Caching Pricing

Context caching stores prompt segments server-side to avoid re-processing on subsequent requests. Cache hits require 100% identical prompt segments.

### Cache Write Costs

| TTL | Cost Multiplier | Sonnet 4.6 ($/MTok) | Opus 4.8 ($/MTok) |
|-----|----------------|---------------------|-------------------|
| 5 minutes | 1.25x input | $3.75 | $6.25 |
| 1 hour | 2.0x input | $6.00 | $10.00 |

### Cache Read Costs

| Model | Read Cost ($/MTok) | vs. Standard Input |
|-------|-------------------|-------------------|
| Claude Sonnet 4.6 | $0.30 | 0.1x (90% off) |
| Claude Opus 4.8 | $0.50 | 0.1x (90% off) |

Cache reads cost 90% less than standard input tokens — the primary cost optimization for repeated-context workloads.

### Cache Limitations
- Up to **4 cache_control markers** per request
- Markers can be placed anywhere in the request (system prompt, tools, messages)
- Cache reads generally do NOT count against ITPM (input tokens per minute) rate limits
- Cache TTL silently regressed from 1h to 5min around early March 2026 (bug) — check your TTL settings

## Stacking Discounts

| Strategy | Effective Discount |
|---------|--------------------|
| Batch API alone | 50% off |
| Prompt caching alone | Up to 90% off cached tokens |
| Both together | Up to 95%+ off effective spend |

## Cost Calculation Examples

### Simple chat (Sonnet 4.6, 1K input + 500 output tokens)
- Input: 1,000 / 1,000,000 × $3.00 = $0.003
- Output: 500 / 1,000,000 × $15.00 = $0.0075
- **Total: ~$0.0105 per call**

### With cached system prompt (1K cached + 200 new input + 500 output)
- Cache read: 1,000 / 1,000,000 × $0.30 = $0.0003
- New input: 200 / 1,000,000 × $3.00 = $0.0006
- Output: 500 / 1,000,000 × $15.00 = $0.0075
- **Total: ~$0.0084 per call (20% cheaper)**

## Free Tier

Anthropic offers a free Build tier for development with very low rate limits (~5 RPM). No credit card required to start, but spending requires a payment method.

## Billing Notes

- Pricing is per **million tokens** (MTok)
- Billed on actual token usage, not reserved capacity
- No monthly minimums or subscription fees for API access (Claude.ai plans are separate)
- Usage tracked by API key / workspace
