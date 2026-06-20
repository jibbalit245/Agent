# Amazon Bedrock Pricing
> Source: https://aws.amazon.com/bedrock/pricing/, https://www.nops.io/blog/amazon-bedrock-pricing/, https://cloudchipr.com/blog/amazon-bedrock-pricing, https://pecollective.com/tools/aws-bedrock-pricing/
> Fetched: 2026-06-20

## Pricing Models Overview

Amazon Bedrock offers three pricing modes:

| Mode | Best For | Discount vs On-Demand |
|------|----------|-----------------------|
| On-Demand | Variable / bursty traffic, experimentation | Baseline |
| Batch Inference | Large async jobs, cost-sensitive workloads | ~50% off |
| Provisioned Throughput | Steady high-volume, latency SLA requirements | Varies; cost-effective at scale |

## On-Demand Pricing (per 1M tokens, as of April 2026)

Prices are per million tokens (input / output).

### Anthropic Claude

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|----------------|
| Claude Opus 4.6 | $5.00 | $25.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Claude 3.5 Sonnet (20241022) | $3.00 | $15.00 |
| Claude 3 Haiku | $0.25 | $1.25 |

### Amazon Nova / Titan

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|----------------|
| Amazon Nova Pro | $0.80 | $3.20 |
| Amazon Nova Lite | $0.06 | $0.24 |
| Amazon Nova Micro | $0.035 | $0.14 |
| Titan Text Premier | $0.50 | $1.50 |

### Meta Llama

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|----------------|
| Llama 3.3 70B Instruct | $0.72 | $0.72 |
| Llama 3 8B Instruct | $0.30 | $0.60 |

### Mistral

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|----------------|
| Mistral Large 2 | $3.00 | $9.00 |
| Mixtral 8x7B | $0.45 | $0.70 |

### Cohere

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|----------------|
| Command R+ | $3.00 | $15.00 |
| Command R | $0.50 | $1.50 |

## Batch Inference

- **Discount**: ~50% off equivalent on-demand rates
- **Turnaround**: Up to 24 hours
- **Use case**: Large-scale async processing (document classification, embeddings, bulk summarization)
- **Not suitable for**: Real-time or interactive workloads

```python
# Batch inference requires S3 for input/output
# Submit via: bedrock.create_model_invocation_job(...)
```

## Provisioned Throughput

Provisioned Throughput (PT) reserves dedicated model capacity measured in **Model Units (MUs)**. You are charged hourly regardless of actual usage.

Commitment options:
- **No commitment** (hourly, cancel anytime) — highest per-unit rate
- **1-month commitment** — moderate discount
- **6-month commitment** — steepest discount

Representative rates (1-month commitment, 1 MU):

| Provider | ~Hourly Rate per MU |
|----------|---------------------|
| Meta Llama models | ~$21.18/hr |
| Anthropic Claude | ~$35–$50/hr (varies by model) |
| Stability AI | ~$49.86/hr |

**When PT makes sense**: You have consistent, predictable traffic that saturates on-demand quotas, or you need guaranteed low latency (PT bypasses per-account token quotas).

**When PT wastes money**: Bursty or intermittent traffic — you pay for idle capacity.

## Cross-Region Inference

- Routing requests via cross-region inference profiles (`us.*`, `eu.*`, `global.*` prefixes) may add a small markup or change effective rate.
- Cross-region inference is primarily for **availability and quota**, not cost savings.
- Check the pricing page for your specific cross-region profile to confirm rates.

## Cost Avoidance Tips

1. **Start with Nova Micro or Haiku** — 10-100x cheaper than Opus/Sonnet for tasks that don't require frontier capability.
2. **Use Batch mode** for offline workloads (embeddings, classification) — instant 50% savings.
3. **Cache prompt prefixes** — Bedrock supports prompt caching for Claude models; repeated system prompts are cheaper.
4. **Monitor with CloudWatch** — Track `InvocationLatency`, `InputTokenCount`, `OutputTokenCount` metrics. Set billing alerts.
5. **Avoid Provisioned Throughput until needed** — PT costs are fixed; only commit once you've validated traffic patterns.
6. **Limit max_tokens** — You're charged for output tokens generated, not tokens requested. But setting `maxTokens` too low causes truncation. Find the right balance.
7. **Compress prompts** — Shorter, precise prompts cost less. Avoid unnecessary verbosity in system prompts.

## Token Counting

To estimate cost before sending a large batch:

```python
# Use the management client to count tokens
mgmt = boto3.client("bedrock", region_name="us-east-1")

# Note: token counting API may vary; check current Bedrock docs
# For Claude via Anthropic SDK:
# import anthropic; client.beta.messages.count_tokens(...)
```

## Free Tier

Amazon Bedrock does not have a traditional free tier. All usage is billed. Use AWS Cost Explorer and set up billing alarms before running large workloads.
