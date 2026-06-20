# Amazon Bedrock Complete Model Catalog
> Source: AWS Documentation, Amazon Bedrock Models pages, hidekazu-konishi.com, codewords.ai, ai-sdk.dev
> Fetched: 2026-06-20

## Model ID Format

Every Bedrock model invocation requires a model ID. The standard format is:
```
{provider}.{model-name}-{date}-v{version}:{minor_version}
```

Example: `anthropic.claude-3-5-sonnet-20241022-v2:0`

Newer models (2025+) often use simplified IDs without dates:
```
anthropic.claude-sonnet-4-6-v1:0
```

Cross-region inference adds a geographic prefix:
- In-region US: `us.anthropic.claude-sonnet-4-6-v1:0`
- In-region EU: `eu.anthropic.claude-sonnet-4-6-v1:0`
- Global (auto-route): `global.anthropic.claude-sonnet-4-6`

## How to List All Available Models

```python
import boto3

bedrock = boto3.client("bedrock", region_name="us-east-1")
response = bedrock.list_foundation_models()

for model in response["modelSummaries"]:
    print(f"{model['modelId']} | {model['providerName']} | {model['modelName']}")
```

---

## Anthropic Claude Models

Claude 4.x models (2026): support tool use, prompt caching, guardrails, knowledge bases, 1M token context.

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Claude Opus 4.6 | `anthropic.claude-opus-4-6-v1:0` | 1M tokens | Most capable, highest cost |
| Claude Opus 4.5 | `anthropic.claude-opus-4-5-20251101-v1:0` | 200K tokens | Previous Opus flagship |
| Claude Sonnet 4.6 | `anthropic.claude-sonnet-4-6-v1:0` | 200K tokens | Best balance cost/performance |
| Claude Sonnet 4.5 | `anthropic.claude-sonnet-4-5-20250929-v1:0` | 200K tokens | Previous Sonnet |
| Claude Haiku 4.5 | `anthropic.claude-haiku-4-5-20251001-v1:0` | 200K tokens | Fast & affordable |
| Claude 3.5 Sonnet v2 | `anthropic.claude-3-5-sonnet-20241022-v2:0` | 200K tokens | Strong, still widely used |
| Claude 3.5 Sonnet v1 | `anthropic.claude-3-5-sonnet-20240620-v1:0` | 200K tokens | Older release |
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | 200K tokens | Very fast, cheapest Claude 3 |
| Claude 3 Opus | `anthropic.claude-3-opus-20240229-v1:0` | 200K tokens | Legacy flagship |
| Claude 3 Sonnet | `anthropic.claude-3-sonnet-20240229-v1:0` | 200K tokens | Legacy middle tier |
| Claude 2.1 | `anthropic.claude-v2:1` | 200K tokens | Legacy |
| Claude Instant 1.2 | `anthropic.claude-instant-v1` | 100K tokens | Legacy fast |

Cross-region variants (prefix with `us.`, `eu.`, or `global.`):
```
us.anthropic.claude-sonnet-4-6-v1:0
eu.anthropic.claude-sonnet-4-6-v1:0
global.anthropic.claude-sonnet-4-6-v1:0
global.anthropic.claude-opus-4-6-v1
```

---

## Amazon Nova Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Nova Premier | `amazon.nova-premier-v1:0` | 1M tokens | Most capable Nova |
| Nova Pro | `amazon.nova-pro-v1:0` | 300K tokens | Multimodal (text, image, video) |
| Nova Lite | `amazon.nova-lite-v1:0` | 300K tokens | Fast multimodal |
| Nova Micro | `amazon.nova-micro-v1:0` | 128K tokens | Text-only, cheapest |
| Nova Canvas | `amazon.nova-canvas-v1:0` | N/A | Image generation |
| Nova Reel | `amazon.nova-reel-v1:0` | N/A | Video generation |

Nova 2 additions (late 2025 / early 2026):
- `amazon.nova-2-lite-v1:0`
- `amazon.nova-sonic-v1:0` (speech/audio model)

---

## Amazon Titan Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Titan Text Premier | `amazon.titan-text-premier-v1:0` | 32K tokens | Best Titan text model |
| Titan Text Express | `amazon.titan-text-express-v1` | 8K tokens | Older general-purpose |
| Titan Text Lite | `amazon.titan-text-lite-v1` | 4K tokens | Economy option |
| Titan Embeddings V2 | `amazon.titan-embed-text-v2:0` | 8K tokens | Text embeddings |
| Titan Embeddings V1 | `amazon.titan-embed-text-v1` | 8K tokens | Older embeddings |
| Titan Multimodal Embeddings | `amazon.titan-embed-image-v1` | - | Image + text embeddings |
| Titan Image Generator V2 | `amazon.titan-image-generator-v2:0` | N/A | Image generation |

---

## Meta Llama Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Llama 4 Maverick 17B | `meta.llama4-maverick-17b-instruct-v1:0` | 1M tokens | Latest, MoE architecture |
| Llama 4 Scout 17B | `meta.llama4-scout-17b-instruct-v1:0` | 10M tokens | Ultra-long context |
| Llama 3.3 70B | `meta.llama3-3-70b-instruct-v1:0` | 128K tokens | Latest Llama 3.x |
| Llama 3.2 90B | `meta.llama3-2-90b-instruct-v1:0` | 128K tokens | Multimodal (vision) |
| Llama 3.2 11B | `meta.llama3-2-11b-instruct-v1:0` | 128K tokens | Mid-size multimodal |
| Llama 3.2 3B | `meta.llama3-2-3b-instruct-v1:0` | 128K tokens | Small, fast |
| Llama 3.2 1B | `meta.llama3-2-1b-instruct-v1:0` | 128K tokens | Smallest, edge deploy |
| Llama 3.1 405B | `meta.llama3-1-405b-instruct-v1:0` | 128K tokens | Largest open model |
| Llama 3.1 70B | `meta.llama3-1-70b-instruct-v1:0` | 128K tokens | Strong open model |
| Llama 3.1 8B | `meta.llama3-1-8b-instruct-v1:0` | 128K tokens | Fast, affordable |
| Llama 3 70B | `meta.llama3-70b-instruct-v1:0` | 8K tokens | Older Llama 3 |
| Llama 3 8B | `meta.llama3-8b-instruct-v1:0` | 8K tokens | Older Llama 3 |

---

## Mistral AI Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Mistral Large 3 | `mistral.mistral-large-3` | 128K tokens | Latest flagship |
| Mistral Large 2407 | `mistral.mistral-large-2407-v1:0` | 128K tokens | Previous large |
| Mistral Large 2402 | `mistral.mistral-large-2402-v1:0` | 32K tokens | Older large |
| Ministral 3 3B | `mistral.ministral-3-3b-instruct` | 128K tokens | Tiny, edge deploy |
| Ministral 3 8B | `mistral.ministral-3-8b-instruct` | 128K tokens | Small efficient |
| Ministral 3 14B | `mistral.ministral-3-14b-instruct` | 128K tokens | Mid-size |
| Magistral Small 1.2 | `mistral.magistral-small-1-2` | 128K tokens | Reasoning model |
| Voxtral Mini 1.0 | `mistral.voxtral-mini-1-0` | - | Audio model |
| Voxtral Small 1.0 | `mistral.voxtral-small-1-0` | - | Audio model |
| Mixtral 8x7B | `mistral.mixtral-8x7b-instruct-v0:1` | 32K tokens | MoE model |
| Mistral 7B | `mistral.mistral-7b-instruct-v0:2` | 32K tokens | Small |

---

## Cohere Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Command R+ | `cohere.command-r-plus-v1:0` | 128K tokens | Strongest text gen |
| Command R | `cohere.command-r-v1:0` | 128K tokens | Good, affordable |
| Embed English v3 | `cohere.embed-english-v3` | 512 tokens | Text embeddings |
| Embed Multilingual v3 | `cohere.embed-multilingual-v3` | 512 tokens | 100+ language embed |

---

## AI21 Labs Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| Jamba 1.5 Large | `ai21.jamba-1-5-large-v1:0` | 256K tokens | Hybrid SSM/Transformer |
| Jamba 1.5 Mini | `ai21.jamba-1-5-mini-v1:0` | 256K tokens | Efficient hybrid model |
| Jamba Instruct | `ai21.jamba-instruct-v1:0` | 256K tokens | Chat-tuned Jamba |

---

## DeepSeek Models

| Model | Model ID | Context | Notes |
|-------|----------|---------|-------|
| DeepSeek R1 | `deepseek.r1-v1:0` | 128K tokens | Strong reasoning model |
| DeepSeek R1 671B | `deepseek.r1-671b-v1:0` | 128K tokens | Full-size variant |

---

## Other Providers (2025-2026 Additions)

| Provider | Model | Model ID (approx) | Notes |
|----------|-------|---------|-------|
| Google | Gemma 3 4B | `google.gemma-3-4b-v1:0` | Open-weight |
| Google | Gemma 3 12B | `google.gemma-3-12b-v1:0` | Open-weight |
| Google | Gemma 3 27B | `google.gemma-3-27b-v1:0` | Open-weight |
| NVIDIA | Nemotron Nano | `nvidia.nemotron-nano-v1:0` | Small efficient model |
| Qwen | Qwen3 series | `qwen.qwen3-*` | Various sizes |
| Moonshot AI | Kimi K2 | `moonshot.kimi-k2-v1:0` | Chinese AI model |
| MiniMax | MiniMax M2 | `minimax.m2-v1:0` | |
| OpenAI | GPT open-weight 120B | `openai.gpt-oss-120b-v1:0` | Open-weight variant |
| OpenAI | GPT open-weight 20B | `openai.gpt-oss-20b-v1:0` | Open-weight variant |

---

## Stability AI Models (Image/Video)

| Model | Model ID | Notes |
|-------|----------|-------|
| Stable Diffusion 3.5 Large | `stability.sd3-5-large-v1:0` | Latest text-to-image |
| Stable Image Ultra | `stability.stable-image-ultra-v1:0` | High-quality images |
| Stable Image Core | `stability.stable-image-core-v1:0` | Balanced image gen |

---

## Embedding Models (for Knowledge Bases / RAG)

| Model | Model ID | Dimensions | Notes |
|-------|----------|-----------|-------|
| Titan Embeddings V2 | `amazon.titan-embed-text-v2:0` | 256/512/1024 | Best Amazon embed |
| Titan Embeddings V1 | `amazon.titan-embed-text-v1` | 1536 | Older |
| Cohere Embed English v3 | `cohere.embed-english-v3` | 1024 | English-focused |
| Cohere Embed Multilingual v3 | `cohere.embed-multilingual-v3` | 1024 | 100+ languages |

---

## Model Lifecycle Notes

- Models go through: Active → Legacy (deprecated) → End-of-life
- When a model reaches end-of-life, all calls to it fail
- Migrate before end-of-life dates shown in the model catalog
- Use `list_foundation_models()` and check `modelLifecycle.status` field:
  ```python
  models = bedrock.list_foundation_models()
  for m in models["modelSummaries"]:
      lifecycle = m.get("modelLifecycle", {})
      if lifecycle.get("status") == "LEGACY":
          print(f"DEPRECATED: {m['modelId']}")
  ```

---

## Selecting the Right Model

| Use Case | Recommended Model |
|----------|------------------|
| Complex reasoning, long docs | Claude Opus 4.6 or Sonnet 4.6 |
| Cost-effective chat/summarization | Claude Haiku 4.5 or Nova Micro |
| Embeddings for RAG | Titan Embed V2 or Cohere Embed v3 |
| Image generation | Nova Canvas or Titan Image Generator V2 |
| Code generation | Claude Sonnet 4.6 or Llama 4 Maverick |
| Open-source/reproducible | Llama 4, DeepSeek R1, Mistral Large 3 |
| Ultra-long context | Llama 4 Scout (10M tokens) or Claude Opus 4.6 (1M) |
| Cheapest text inference | Amazon Nova Micro ($0.035/$0.14 per 1M tokens) |
