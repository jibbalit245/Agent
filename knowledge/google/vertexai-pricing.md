# Vertex AI Generative AI Pricing

> Source: https://cloud.google.com/vertex-ai/generative-ai/pricing
> Fetched: 2026-06-20

## Overview

You're charged only for requests that return a 200 response code. Requests returning any other response codes (4xx, 5xx) are not charged for input or output.

For all other Agent Platform pricing including ML Platform and MLOps services, refer to the [Agent Platform pricing page](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing).

---

## Google Models Pricing

### Gemini 3

#### Standard Tier

| Model | Type | Price (/1M tokens) ≤200K input | Price (/1M tokens) >200K input | Price (/1M tokens) ≤200K cached | Price (/1M tokens) >200K cached |
|-------|------|------|------|------|------|
| **Gemini 3.1 Pro Preview** | Input (text, image, video, audio) | $2 | $4 | $0.2 | $0.4 |
| | Text output | $12 | $18 | N/A | N/A |
| **Gemini 3.1 Flash Live API** | 1M input text tokens | $0.75 | $0.75 | N/A | N/A |
| | 1M input audio tokens | $3 | $3 | N/A | N/A |
| | 1M input video/image tokens | $1 | $1 | N/A | N/A |
| | 1M output text tokens | $4.5 | $4.5 | N/A | N/A |
| | 1M output audio tokens | $12 | $12 | N/A | N/A |
| | 1M output video tokens (Live Avatar) | $2 | $2 | N/A | N/A |
| **Gemini 3.5 Flash** | Input (text, image, video, audio) | $1.50 (Global) $1.65 (Non-global)* | $1.50 (Global) $1.65 (Non-global)* | $0.15 (Global) $0.165 (Non-global)* | $0.15 (Global) $0.165 (Non-global)* |
| | Text output | $9.00 (Global) $9.90 (Non-global)* | $9.00 (Global) $9.90 (Non-global)* | N/A | N/A |
| **Gemini 3 Flash Preview** | Input (text, image, video) | $0.5 | $0.5 | $0.05 | $0.05 |
| | Input (audio) | $1 | $1 | $0.1 | $0.1 |
| | Text output | $3 | $3 | N/A | N/A |
| **Gemini 3.1 Flash-Lite** | Input (text, image, video) | $0.25 (Global) $0.275 (Non-global)* | $0.25 (Global) $0.275 (Non-global)* | $0.025 (Global) $0.0275 (Non-global)* | $0.025 (Global) $0.0275 (Non-global)* |
| | Input (audio) | $0.5 (Global) $0.55 (Non-global)* | $0.5 (Global) $0.55 (Non-global)* | $0.05 (Global) $0.055 (Non-global)* | $0.05 (Global) $0.055 (Non-global)* |
| | Text output | $1.5 (Global) $1.65 (Non-global)* | $1.5 (Global) $1.65 (Non-global)* | N/A | N/A |
| **Gemini 3 Pro Image** | Input (text, image) | $2 | N/A | N/A | N/A |
| | Text output | $12 | N/A | N/A | N/A |
| | Image Output** | $120 | N/A | N/A | N/A |
| **Gemini 3.1 Flash Image** | Input (text, image, video) | $0.50 | N/A | N/A | N/A |
| | Text output | $3 | N/A | N/A | N/A |
| | Image Output*** | $60 | N/A | N/A | N/A |

#### Priority Tier

| Model | Type | Price (/1M tokens) ≤200K with Priority | Price (/1M tokens) >200K with Priority | Price (/1M tokens) ≤200K cached with Priority | Price (/1M tokens) >200K cached with Priority |
|-------|------|------|------|------|------|
| **Gemini 3.1 Pro Preview** | Input (text, image, video, audio) | $3.6 | $7.2 | $0.36 | $0.72 |
| | Text output | $21.6 | $32.4 | N/A | N/A |
| **Gemini 3.5 Flash** | Input (text, image, video, audio) | $2.70 (Global) $2.97 (Non-global)* | $2.70 (Global) $2.97 (Non-global)* | $0.27 (Global) $0.297 (Non-global)* | $0.27 (Global) $0.297 (Non-global)* |
| | Text output | $16.20 (Global) $17.82 (Non-global)* | $16.20 (Global) $17.82 (Non-global)* | N/A | N/A |
| **Gemini 3 Flash Preview** | Input (text, image, video) | $0.9 | $0.9 | $0.09 | $0.09 |
| | Input (audio) | $1.8 | $1.8 | $0.18 | $0.18 |
| | Text output | $5.40 | $5.40 | N/A | N/A |
| **Gemini 3.1 Flash-Lite** | Input (text, image, video) | $0.45 (Global) $0.495 (Non-global)* | $0.45 (Global) $0.495 (Non-global)* | $0.045 (Global) $0.0495 (Non-global)* | $0.045 (Global) $0.0495 (Non-global)* |
| | Input (audio) | $0.9 (Global) $0.99 (Non-global)* | $0.9 (Global) $0.99 (Non-global)* | $0.09 (Global) $0.099 (Non-global)* | $0.09 (Global) $0.099 (Non-global)* |
| | Text output | $2.7 (Global) $2.97 (Non-global)* | $2.7 (Global) $2.97 (Non-global)* | N/A | N/A |

#### Flex/Batch Tier

| Model | Type | Price (/1M tokens) ≤200K Flex/Batch | Price (/1M tokens) >200K Flex/Batch | Price (/1M tokens) ≤200K cached Flex/Batch | Price (/1M tokens) >200K cached Flex/Batch |
|-------|------|------|------|------|------|
| **Gemini 3.1 Pro Preview** | Input (text, image, video, audio) | $1 | $2 | N/A | N/A |
| | Text output | $6 | $9 | N/A | N/A |
| **Gemini 3.5 Flash** | Input (text, image, video, audio) | $0.75 (Global) $0.825 (Non-global)* | $0.75 (Global) $0.825 (Non-global)* | Batch: $0.075 (Global) Flex: $0.08 (Global) $0.0825 (Non-global)* | Batch: $0.075 (Global) Flex: $0.08 (Global) $0.0825 (Non-global)* |
| | Text output | $4.50 (Global) $4.95 (Non-global)* | $4.50 (Global) $4.95 (Non-global)* | N/A | N/A |
| **Gemini 3 Flash Preview** | Input (text, image, video) | $0.25 | $0.25 | N/A | N/A |
| | Input (audio) | $0.5 | $0.5 | N/A | N/A |
| | Text output | $1.5 | $1.5 | N/A | N/A |
| **Gemini 3.1 Flash-Lite** | Input (text, image, video) | $0.125 (Global) $0.1375 (Non-global)* | $0.125 (Global) $0.1375 (Non-global)* | $0.0125 (Global) $0.01375 (Non-global)* | $0.0125 (Global) $0.01375 (Non-global)* |
| | Input (audio) | $0.25 (Global) $0.275 (Non-global)* | $0.25 (Global) $0.275 (Non-global)* | $0.025 (Global) $0.0275 (Non-global)* | $0.025 (Global) $0.0275 (Non-global)* |
| | Text output | $0.75 (Global) $0.825 (Non-global)* | $0.75 (Global) $0.825 (Non-global)* | N/A | N/A |
| **Gemini 3 Pro Image** | Input (text, image) | $1 | N/A | N/A | N/A |
| | Text output | $6 | N/A | N/A | N/A |
| | Image Output** | $60 | N/A | N/A | N/A |
| **Gemini 3.1 Flash Image** | Input (text, image, video) | $0.25 | N/A | N/A | N/A |
| | Text output | $1.50 | N/A | N/A | N/A |
| | Image Output*** | $30 | N/A | N/A | N/A |

#### Gemini 3 Features

| Feature | Pricing |
|---------|---------|
| **Grounding with Google Web Search and Image Search & Web Grounding for Enterprise** | Includes 5,000 search queries/month at no charge, aggregated across all Gemini 3 models. Excess: **$14 per 1,000 search queries**. Billing starts January 5, 2026. Input tokens from grounding are not charged. Contact account team for >1M grounded prompts/day. |
| **Grounding with Google Maps** | Includes 5,000 queries/month at no charge, aggregated across all Gemini 3 models. Excess: **$14 per 1,000 queries**. Billing starts January 5, 2026. Input tokens from Google Maps are not charged. |
| **Grounding with your data** | **$2.50 per 1,000 prompts** |
| **Computer Use Tool** | Pricing based on total input and output tokens using respective model prices. Function declarations included in input token count starting with Gemini 3.5. |

### Gemini 3 Agents

| Model | Type | Price (/1M tokens) | Price (/M cached input tokens) |
|-------|------|-------|-------|
| **Gemini Deep Research Agent** | Input (text) | $2 | $0.2 |
| | Text output | $12 | N/A |

---

### Gemini 2.5

#### Standard Tier

| Model | Type | Price (/1M tokens) ≤200K | Price (/1M tokens) >200K | Price (/1M tokens) ≤200K cached | Price (/1M tokens) >200K cached |
|-------|------|------|------|------|------|
| **Gemini 2.5 Pro** | Input (text, image, video, audio) | $1.25 | $2.50 | $0.13 | $0.25 |
| | Text output | $10 | $15 | N/A | N/A |
| **Gemini 2.5 Pro Computer Use-Preview** | Input (text, image, video, audio) | $1.25 | $2.5 | N/A | N/A |
| | Text output | $10.00 | $15.00 | N/A | N/A |
| **Gemini 2.5 Flash** | Input (text, image, video) | $0.30 | $0.30 | $0.03 | $0.03 |
| | Audio Input | $1 | $1 | $0.10 | $0.10 |
| | Text output | $2.50 | $2.50 | N/A | N/A |
| **Gemini 2.5 Flash Image** | Input (text, image)*** | $0.30 | N/A | N/A | N/A |
| | Text output | $2.50 | N/A | N/A | N/A |
| | Image output*** | $30 | N/A | N/A | N/A |
| **Gemini 2.5 Flash Live API** | 1M input text tokens | $0.5 | $0.5 | N/A | N/A |
| | 1M input audio tokens | $3 | $3 | N/A | N/A |
| | 1M input video/image tokens | $3 | $3 | N/A | N/A |
| | 1M output text tokens | $2 | $2 | N/A | N/A |
| | 1M output audio tokens | $12 | $12 | N/A | N/A |
| **Gemini 2.5 Flash Lite** | Input (text, image, video) | $0.10 | $0.10 | $0.01 | $0.01 |
| | Audio Input | $0.30 | $0.30 | $0.03 | $0.03 |
| | Text output | $0.40 | $0.40 | N/A | N/A |

#### Priority Tier

| Model | Type | Price (/1M tokens) ≤200K Priority | Price (/1M tokens) >200K Priority | Price (/1M tokens) ≤200K cached Priority | Price (/1M tokens) >200K cached Priority |
|-------|------|------|------|------|------|
| **Gemini 2.5 Pro** | Input (text, image, video, audio) | $2.25 | $4.50 | $0.23 | $0.45 |
| | Text output | $18 | $27 | N/A | N/A |
| **Gemini 2.5 Flash** | Input (text, image, video) | $0.54 | $0.54 | $0.05 | $0.05 |
| | Audio Input | $1.80 | $1.80 | $0.18 | $0.18 |
| | Text output | $4.50 | $4.50 | N/A | N/A |
| **Gemini 2.5 Flash Lite** | Input (text, image, video) | $0.18 | $0.18 | $0.02 | $0.02 |
| | Audio Input | $0.54 | $0.54 | $0.05 | $0.05 |
| | Text output | $0.72 | $0.72 | N/A | N/A |

#### Flex/Batch Tier

| Model | Type | Price (/1M tokens) ≤200K Flex/Batch | Price (/1M tokens) >200K Flex/Batch |
|-------|------|------|------|
| **Gemini 2.5 Pro** | Input (text, image, video, audio) | $0.625 | $1.25 |
| | Text output | $5 | $7.5 |
| **Gemini 2.5 Flash** | Input (text, image, video) | $0.15 | $0.15 |
| | Audio Input | $0.5 | $0.5 |
| | Text output | $1.25 | $1.25 |
| **Gemini 2.5 Flash Image** | Input (text, image, video)*** | $0.15 | N/A |
| | Text output | $1.25 | N/A |
| | Image output*** | $15 | N/A |
| **Gemini 2.5 Flash Lite** | Input (text, image, video) | $0.05 | $0.05 |
| | Audio Input | $0.15 | $0.15 |
| | Text output | $0.2 | $0.2 |

#### Gemini 2.5 Features

| Feature | Pricing |
|---------|---------|
| **Grounding with Google Search** | **Gemini 2.5 Flash** and **2.5 Flash-Lite**: 1,500 grounded prompts/day included. **Gemini 2.5 Pro**: 10,000 grounded prompts/day. Excess: **$35 per 1,000 grounded prompts**. A grounded prompt = 1 request with 1+ Google Search queries. Contact account team for >1M grounded prompts/day. Customers can opt to not display Search Suggestions (alternate pricing applies). |
| **Web Grounding for enterprise** | **$45 per 1,000 grounded prompts**. A grounded prompt = 1 request with 1+ Web Grounding queries. Contact account team for >1M grounded prompts/day. Customers can opt to not display Search Suggestions (alternate pricing applies). |
| **Grounding with your data** | **$2.5 per 1,000 requests** (starting June 16, 2025) |
| **Grounding with Google Maps** | **Flash** and **Flash-Lite**: 1,500 grounded prompts/day. **Pro**: 10,000 grounded prompts/day. Excess: **$25 per 1,000 grounded prompts**. Contact account team for >1M grounded prompts/day. |

---

### Gemini 2.0

#### Token-Based Pricing

| Model | Type | Price | Price with Batch API |
|-------|------|-------|-------|
| **Gemini 2.0 Flash** | 1M Input text tokens | $0.15 | $0.075 |
| | 1M Input audio tokens | $1.00 | $0.50 |
| | 1M Output text tokens | $0.60 | $0.30 |
| | Tuning for 1M training tokens | $3.00 | N/A |
| **Gemini 2.0 Flash Image Generation** | 1M input text tokens | $0.15 | N/A |
| | 1M input audio tokens | $1.00 | N/A |
| | 1M input video tokens | $3 | N/A |
| | 1M output text tokens | $0.60 | N/A |
| | 1M output image tokens | $30.00 | N/A |
| **Gemini 2.0 Flash Live API** | 1M input text tokens | $0.5 | N/A |
| | 1M input audio tokens | $3 | N/A |
| | 1M input video/image tokens | $3 | N/A |
| | 1M output text tokens | $2 | N/A |
| | 1M output audio tokens | $12 | N/A |
| **Gemini 2.0 Flash Lite** | 1M Input text tokens | $0.075 | $0.0375 |
| | 1M Input audio tokens | $0.075 | $0.0375 |
| | 1M Output text tokens | $0.30 | $0.15 |
| | Tuning for 1M training tokens | $1.00 | N/A |

#### Modality-Based Pricing (Reference)

**Conversion Rates:**
- 4 characters ≈ 1 text token (including whitespace)
- 1024x1024 image = 1290 tokens
- Video input = 258 tokens/second (1 fps sample rate)
- Audio input = 25 tokens/second (without timestamp)

| Model | Type | Price | Price with Batch API |
|-------|------|-------|-------|
| **Gemini 2.0 Flash** | Input text ($/M char) | $0.0375 | $0.01875 |
| | Input image ($/image) | $0.0001935 | $0.00009675 |
| | Input video ($/sec) | $0.0000387 | $0.00001935 |
| | Input audio ($/sec) | $0.000025 | $0.0000125 |
| | Output text ($/M char) | $0.15 | $0.075 |
| **Gemini 2.0 Flash Image Generation** | Input text ($/M char) | $0.0375 | N/A |
| | Input image ($/image) | $0.0001935 | N/A |
| | Input video ($/sec) | $0.0000387 | N/A |
| | Input audio ($/sec) | $0.000025 | N/A |
| | Output text ($/M char) | $0.15 | N/A |
| | Output image ($/image) | $0.04 | N/A |
| **Gemini 2.0 Flash Lite** | Input text ($/M char) | $0.01875 | $0.009375 |
| | Input image ($/image) | $0.00009675 | $0.000048375 |
| | Input video ($/sec) | $0.00001935 | $0.000009675 |
| | Input audio ($/sec) | $0.000001875 | $0.000000938 |
| | Output text ($/M char) | $0.075 | $0.0375 |

#### Gemini 2.0 Features

| Feature | Pricing |
|---------|---------|
| **Grounding with Google Search** | **Gemini 2.0 Flash** and **2.5 Flash**: 1,500 grounded prompts/day included. Excess: **$35 per 1,000 grounded prompts**. A grounded prompt = 1 request with 1+ Google Search queries. Multiple search queries = 1 charge. Contact account team for >1M grounded prompts/day. |
| **Web Grounding for enterprise** | **$45 per 1,000 grounded prompts**. |
| **Grounding with your data** | **$2.5 per 1,000 requests** (starting June 16, 2025) |
| **Grounding with Google Maps** | **Flash** and **Flash-Lite**: 1,500 grounded prompts/day. **Pro**: 10,000 grounded prompts/day. Excess: **$25 per 1,000 grounded prompts**. |

---

## Special Billing Notes

### Live API Context Window Billing

**LiveAPI Session Context Window**: You are charged per turn for all tokens in the Session Context Window. The context includes new tokens (current turn) + all accumulated tokens from previous turns. This means tokens from past turns are re-processed and charged in each new turn, up to configured context window size.

- A **"turn"** = one user input + model response
- **Proactive Audio Mode**: Input tokens charged while listening. Output tokens charged only on response.
- **Audio-to-text transcription**: All generated text tokens charged at text token output rate.

### Image Output Pricing Notes

#### Gemini 3 Pro Image
- **Input**: 560 tokens ($0.0011) per input image
- **Output**: Token-based scaling by resolution:
  - 1K and 2K (~1MP and ~4MP): 1120 tokens ($0.134)
  - 4K (~16MP): 2000 tokens ($0.24)

#### Gemini 3.1 Flash Image
- **Input**: 1120 tokens ($0.0006) per input image
- **Output**: Token-based scaling by resolution:
  - 512 (~0.25MP): 747 tokens ($0.045)
  - 1K (~1MP): 1120 tokens ($0.067)
  - 2K (~4MP): 1680 tokens ($0.101)
  - 4K (~16MP): 2520 tokens ($0.15)

#### Gemini 3.1 Live API
- **Audio**: 25 tokens/second input/output
- **Images**: 258 tokens per image input
- **Video output (Live Avatar)**: 6192 tokens/second (charged only during active audio response generation, not during listening/idle)

---

## Key Pricing Footnotes

- \* Non-global endpoint pricing effective July 1, 2026. Before this date, Global endpoint pricing applies to Non-global endpoints.
- \*\* Gemini 3 Pro Image charges per image with output scaling by resolution.
- \*\*\* Gemini 3.1 Flash Image charges per image with output scaling by resolution.
- \*\*\*\* Gemini 3.1 Live API: 25 tokens/sec audio, 258 tokens/image, 6192 tokens/sec video output (Live Avatar).
- If a query input context exceeds 200K tokens, all tokens (input and output) are charged at long context rates.
- **Tuned model endpoints** are charged at 1.5x the base model price.

---

## Related Resources

- [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator)
- [Google Cloud Free Tier](https://cloud.google.com/free)
- [Cost Optimization Framework](https://cloud.google.com/architecture/framework/cost-optimization)
- [Cost Management Tools](https://cloud.google.com/cost-management)
- [Full Product Price List](https://cloud.google.com/pricing/list)
