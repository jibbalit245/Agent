# Mistral AI Models

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/getting-started/models/models_overview/ — content below is from model training data (knowledge cutoff August 2025).

## Overview

Mistral AI offers two categories: proprietary models via their hosted API and open-weight models for self-hosting.

---

## Proprietary Models (La Plateforme)

### Mistral Large

The flagship model, best at complex reasoning, multilingual tasks, and instruction following.

| Property | Value |
|---|---|
| Model ID | `mistral-large-latest` (alias) |
| Current version | `mistral-large-2411` |
| Context window | 128,000 tokens |
| Languages | EN, FR, DE, ES, IT, PT, ZH, JA, KO, AR, HI |
| Function calling | Yes |
| Vision | No (use Pixtral for vision) |

### Mistral Small

Cost-effective model for simpler tasks.

| Property | Value |
|---|---|
| Model ID | `mistral-small-latest` |
| Current version | `mistral-small-2409` |
| Context window | 32,000 tokens |
| Languages | EN, FR, DE, ES, IT, and more |
| Function calling | Yes |

### Mistral Medium (Legacy)

Balanced model, still available but Mistral Small 2409 is the recommended alternative.

| Property | Value |
|---|---|
| Model ID | `mistral-medium-latest` |
| Context window | 32,000 tokens |

### Pixtral Large

Vision-capable version of Mistral Large.

| Property | Value |
|---|---|
| Model ID | `pixtral-large-latest` |
| Current version | `pixtral-large-2411` |
| Context window | 128,000 tokens |
| Vision | Yes (images, documents) |
| Function calling | Yes |

### Pixtral 12B

Smaller, efficient vision model.

| Property | Value |
|---|---|
| Model ID | `pixtral-12b-latest` |
| Current version | `pixtral-12b-2409` |
| Parameters | 12B |
| Context window | 128,000 tokens |
| Vision | Yes |

### Mistral Nemo

Compact model trained with Nvidia, good quality for size.

| Property | Value |
|---|---|
| Model ID | `open-mistral-nemo` |
| Parameters | 12B |
| Context window | 128,000 tokens |
| Function calling | Yes |
| License | Apache 2.0 |

---

## Code Models

### Codestral

State-of-the-art code model supporting 80+ programming languages.

| Property | Value |
|---|---|
| Model ID | `codestral-latest` |
| Current version | `codestral-2405` |
| Context window | 32,000 tokens |
| Languages | 80+ programming languages |
| Fill-in-middle | Yes |

**Special Codestral Base URL:**
```
https://codestral.mistral.ai/v1
```
(requires separate Codestral API key)

### Codestral Mamba

State-space model for code (experimental).

| Property | Value |
|---|---|
| Model ID | `open-codestral-mamba` |
| Architecture | Mamba (SSM) |
| Context | Long |

---

## Embedding Models

### Mistral Embed

Semantic embedding model for RAG and similarity tasks.

| Property | Value |
|---|---|
| Model ID | `mistral-embed` |
| Output dimensions | 1,024 |
| Max input tokens | 8,192 |
| Normalized | Yes |

---

## Moderation Models

### Mistral Moderation

For content safety classification.

| Property | Value |
|---|---|
| Model ID | `mistral-moderation-latest` |
| Current version | `mistral-moderation-2411` |

---

## Open-Weight Models (Self-Hosting)

### Mistral 7B

The original release; highly capable 7B model.

| Property | Value |
|---|---|
| Model ID (HuggingFace) | `mistralai/Mistral-7B-v0.1` |
| Instruct version | `mistralai/Mistral-7B-Instruct-v0.3` |
| Parameters | 7B |
| Context window | 32,768 tokens |
| License | Apache 2.0 |
| API ID | `open-mistral-7b` |

### Mixtral 8x7B

Sparse mixture-of-experts model.

| Property | Value |
|---|---|
| Model ID (HuggingFace) | `mistralai/Mixtral-8x7B-v0.1` |
| Instruct version | `mistralai/Mixtral-8x7B-Instruct-v0.1` |
| Active parameters | ~12B (of 47B total) |
| Context window | 32,768 tokens |
| License | Apache 2.0 |
| API ID | `open-mixtral-8x7b` |

### Mixtral 8x22B

Large sparse mixture-of-experts model.

| Property | Value |
|---|---|
| Model ID (HuggingFace) | `mistralai/Mixtral-8x22B-v0.1` |
| Instruct version | `mistralai/Mixtral-8x22B-Instruct-v0.1` |
| Active parameters | ~39B (of 141B total) |
| Context window | 65,536 tokens |
| License | Apache 2.0 |
| API ID | `open-mixtral-8x22b` |

---

## Model Aliases

Mistral provides dated versions and `latest` aliases:

| Alias | Resolves to |
|---|---|
| `mistral-large-latest` | `mistral-large-2411` |
| `mistral-small-latest` | `mistral-small-2409` |
| `pixtral-large-latest` | `pixtral-large-2411` |
| `codestral-latest` | `codestral-2405` |
| `mistral-moderation-latest` | `mistral-moderation-2411` |

**Best practice:** Use dated versions (e.g., `mistral-large-2411`) in production for stability.

---

## Model Selection Guide

| Use Case | Recommended Model |
|---|---|
| Complex reasoning / writing | `mistral-large-latest` |
| Cost-effective general use | `mistral-small-latest` |
| Code generation / completion | `codestral-latest` |
| Vision / image understanding | `pixtral-large-latest` |
| Text embeddings / RAG | `mistral-embed` |
| Multilingual (12B, cheap) | `open-mistral-nemo` |
| Self-hosting (7B) | `Mistral-7B-Instruct-v0.3` |
| Self-hosting (MoE) | `Mixtral-8x7B-Instruct-v0.1` |
| Content moderation | `mistral-moderation-latest` |

---

## API: List Models

```python
from mistralai import Mistral

client = Mistral(api_key="your_key")
models = client.models.list()
for model in models.data:
    print(model.id)
```

```bash
curl https://api.mistral.ai/v1/models \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```
