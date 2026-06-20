# Google AI Pricing (Gemini API + Vertex AI)  
> Source: https://ai.google.dev/pricing, https://cloud.google.com/vertex-ai/pricing  
> Fetched: 2026-06-20

## Gemini API (Google AI Studio) Pricing

Prices are per million tokens. As of mid-2026, the current generation includes Gemini 2.5 and Gemini 3 series.

### Current Model Pricing (approximate, verify at ai.google.dev/pricing)

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Context |
|-------|--------------------|--------------------|---------|
| gemini-3.5-flash | ~$1.50 | ~$9.00 | 1M |
| gemini-3.1-pro | Higher | Higher | 2M |
| gemini-2.5-flash | ~$0.30 | ~$2.50 | 1M |
| gemini-2.5-pro | ~$1.25 | ~$10.00 | 2M |
| gemini-2.0-flash | ~$0.10 | ~$0.40 | 1M |
| gemini-1.5-flash | ~$0.075 | ~$0.30 | 1M |
| gemini-1.5-pro | ~$1.25 | ~$5.00 | 2M |

General range: $0.10–$4.00/M input tokens, $0.40–$18.00/M output tokens (as of early 2026).

Note: Gemini-2.0-flash-001 discontinued June 1, 2026.

### Free Tier (Google AI Studio)

- **As of April 2026**: Free tier limited to Flash and Flash-Lite models only. Pro models require a paid plan.
- **Token limits**: ~250,000 tokens per minute
- **Rate limits**: ~10 RPM, ~1,500 RPD for Flash models
- **No credit card required** for free tier
- **Important**: Google reduced free tier quotas by ~50-80% in December 2025

Free tier is suitable for development and prototyping. Not for production workloads.

### Context Caching Pricing

Context caching (storing prompt context to avoid re-sending it) is available for some models:
- Cache write: ~$0.50/M tokens
- Cache read (hits): ~$0.10/M tokens (much cheaper than regular input)
- Cache storage: charged per hour per million tokens

Caching is very useful for long system prompts or documents reused across many requests.

## Vertex AI Gemini Pricing

Vertex AI uses the same Gemini models but pricing may differ slightly and includes enterprise billing through Google Cloud.

### Key Differences from AI Studio Pricing

- No free tier on Vertex AI (all usage is billed)
- Billed to Google Cloud project
- Enterprise agreements may offer committed use discounts
- Same underlying models, similar per-token rates

### Vertex AI Inference Pricing

Pricing for Gemini on Vertex AI is comparable to AI Studio:
- Gemini 2.5 Flash: ~$0.30/$2.50 per 1M input/output
- Gemini 2.5 Pro: ~$1.25/$10.00 per 1M input/output

Check the [Vertex AI pricing page](https://cloud.google.com/vertex-ai/pricing) for authoritative rates — they update frequently.

## Vertex AI Model Garden / Self-Deploy Pricing

When you deploy models on dedicated endpoints, you pay for:

### Compute Costs (runs 24/7 while endpoint is active)

| Instance Type | GPU | Approx. Cost/Hour |
|--------------|-----|-------------------|
| g2-standard-4 | 1x L4 24GB | ~$0.70 |
| a2-highgpu-1g | 1x A100 40GB | ~$3.67 |
| a2-highgpu-2g | 2x A100 40GB | ~$7.34 |
| a2-highgpu-4g | 4x A100 40GB | ~$14.69 |
| a2-ultragpu-1g | 1x A100 80GB | ~$5.19 |
| a3-highgpu-8g | 8x H100 80GB | ~$40+ |

Monthly cost for a single A100: ~$2,650/month if running 24/7.

### MaaS Pricing (Model-as-a-Service)

For partner models (Llama, Mistral) accessed via MaaS on Vertex:
- Pay per token, similar structure to Gemini
- Infrastructure costs are included in the per-token price
- Varies by model — check the Model Garden page for each model's pricing

## Cost Optimization Tips

1. **Use Flash models for prototyping**: 10-30x cheaper than Pro models
2. **Context caching**: If you repeat the same large system prompt, caching saves money
3. **Batch requests**: Some APIs offer batch discounts (~50%)
4. **Delete idle endpoints**: Self-deployed endpoints charge even when idle
5. **Use free tier during development**: Google AI Studio free tier is plenty for dev/testing
6. **Monitor usage**: Set budget alerts in Google Cloud Console

## Estimating Costs

Rough estimates for common use cases:
- 1M tokens through gemini-2.5-flash: ~$0.30 input + ~$2.50 output
- A chatbot processing 100K conversations/day at 1K tokens each = 100M tokens/day
  - At flash pricing: ~$30/day input + ~$250/day output = ~$280/day

## References

- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Gemini API Pricing Guide 2025](https://blog.laozhang.ai/ai-models/gemini-api-price-guide-2025/)
- [Full 2026 Pricing Analysis](https://www.metacto.com/blogs/the-true-cost-of-google-gemini-a-guide-to-api-pricing-and-integration)
