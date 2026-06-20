# OpenRouter Provider Routing
> Source: https://openrouter.ai/docs/provider-routing
> Fetched: 2026-06-20
---

## Overview

OpenRouter routes requests to underlying AI providers (Anthropic, OpenAI, AWS Bedrock, Google Vertex, etc.). Provider routing lets you control which providers handle your requests and in what order.

## The `provider` Object

Include a `provider` key at the top level of your request body to control routing:

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "messages": [...],
  "provider": {
    "order": ["Anthropic", "AWS Bedrock"],
    "allow_fallbacks": true,
    "data_collection": "deny",
    "sort": "price",
    "require_parameters": false,
    "ignore": ["Together"]
  }
}
```

## Provider Routing Parameters

| Parameter | Type | Description |
|---|---|---|
| `order` | string[] | Ordered list of providers to try first |
| `allow_fallbacks` | boolean | Whether to fall back to other providers if `order` list is exhausted (default: `true`) |
| `ignore` | string[] | Providers to never route to for this request |
| `sort` | string | Sort remaining providers by `"price"`, `"latency"`, or `"throughput"` |
| `require_parameters` | boolean | Only use providers that support all requested parameters (default: `false`) |
| `data_collection` | string | `"allow"` (default) or `"deny"` — restricts to providers with no-training agreements |
| `quantizations` | string[] | Filter by quantization type: `"int4"`, `"int8"`, `"fp8"`, `"fp16"`, `"bf16"`, `"unknown"` |
| `context_length` | integer | Minimum required context length |

## Provider Names

Common provider names used in `order` and `ignore`:

| Provider Name | Notes |
|---|---|
| `Anthropic` | Direct Anthropic API |
| `AWS Bedrock` | Amazon Bedrock |
| `Google` | Google Vertex AI |
| `Azure` | Azure OpenAI |
| `OpenAI` | Direct OpenAI API |
| `Together` | Together AI |
| `Fireworks` | Fireworks AI |
| `Lepton` | Lepton AI |
| `DeepInfra` | DeepInfra |
| `Perplexity` | Perplexity AI |
| `Cohere` | Cohere |
| `Groq` | Groq |
| `Mistral` | Mistral AI |
| `Hyperbolic` | Hyperbolic |
| `NovitaAI` | Novita AI |

## Routing Examples

### Force Specific Provider (No Fallbacks)

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "provider": {
    "order": ["Anthropic"],
    "allow_fallbacks": false
  }
}
```

### Prefer Low-Latency Providers

```json
{
  "model": "meta-llama/llama-3.3-70b-instruct",
  "provider": {
    "sort": "latency"
  }
}
```

### Privacy-First (No Data Training)

```json
{
  "model": "openai/gpt-4o",
  "provider": {
    "data_collection": "deny"
  }
}
```

### Require All Parameters Supported

```json
{
  "model": "anthropic/claude-opus-4-8",
  "provider": {
    "require_parameters": true
  },
  "logprobs": true,
  "top_logprobs": 3
}
```

### Prefer Price, Exclude Provider

```json
{
  "model": "meta-llama/llama-3.3-70b-instruct",
  "provider": {
    "sort": "price",
    "ignore": ["Together"]
  }
}
```

## Model Routing with `models` Array

Send requests to a list of models, trying each in order:

```json
{
  "models": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o",
    "meta-llama/llama-3.3-70b-instruct"
  ],
  "messages": [{"role": "user", "content": "Hello"}]
}
```

The first model that successfully responds is used. Unlike `fallbacks`, `models` targets different models (not different providers for the same model).

## Fallback Models

Configure up to 3 fallback models (triggered if primary model fails):

```json
{
  "model": "anthropic/claude-opus-4-8",
  "fallbacks": [
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-4o"
  ],
  "messages": [...]
}
```

- Max 3 fallback entries
- Fallbacks are tried in order if the primary model fails with a non-client-error
- Rate limit errors trigger fallback to next in list

## Auto Router

Use `openrouter/auto` to let OpenRouter select the best model:

```json
{
  "model": "openrouter/auto",
  "messages": [{"role": "user", "content": "Explain quantum entanglement"}]
}
```

OpenRouter analyzes the prompt and routes to the model most likely to give the best response.

## Checking Which Provider Was Used

The response includes which provider actually handled the request:

```json
{
  "id": "gen-1234567890",
  "model": "anthropic/claude-sonnet-4-6",
  "provider": "Anthropic",
  ...
}
```

## Bring Your Own Key (BYOK)

Route requests through your own API keys with OpenRouter acting as an orchestration layer:

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "provider": {
    "order": ["Anthropic"],
    "allow_fallbacks": false
  }
}
```

Then set your Anthropic API key in the OpenRouter dashboard under API Keys → Provider Keys.

BYOK pricing: 5% routing fee on top of provider pass-through costs (no standard OpenRouter markup).
