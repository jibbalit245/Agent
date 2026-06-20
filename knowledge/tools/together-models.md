# Together AI Inference Models

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/docs/inference-models — content below is from model training data (knowledge cutoff August 2025).

## Overview

Together AI hosts 100+ open-source models across text, code, vision, and image generation categories. All models are available via serverless inference; some are available for dedicated deployment.

---

## Text / Chat Models

### Meta Llama 3.x

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 70B | 131,072 | Recommended, fast |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` | 70B | 131,072 | Free tier version |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` | 8B | 131,072 | Fast, affordable |
| `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` | 70B | 131,072 | High quality |
| `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo` | 405B | 131,072 | Largest Llama |
| `meta-llama/Llama-3.2-3B-Instruct-Turbo` | 3B | 131,072 | Smallest, cheapest |
| `meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo` | 11B | 131,072 | Vision model |
| `meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo` | 90B | 131,072 | Large vision model |
| `meta-llama/Meta-Llama-3-8B-Instruct-Turbo` | 8B | 8,192 | Older version |
| `meta-llama/Meta-Llama-3-70B-Instruct-Turbo` | 70B | 8,192 | Older version |
| `meta-llama/Llama-3-8b-chat-hf` | 8B | 8,192 | HuggingFace format |
| `meta-llama/Llama-3-70b-chat-hf` | 70B | 8,192 | HuggingFace format |

### Mistral / Mixtral

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | 8x7B MoE | 32,768 | Classic MoE |
| `mistralai/Mixtral-8x22B-Instruct-v0.1` | 8x22B MoE | 65,536 | Large MoE |
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | 32,768 | Efficient |
| `mistralai/Mistral-7B-Instruct-v0.1` | 7B | 4,096 | Original |

### Qwen (Alibaba)

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `Qwen/Qwen2.5-72B-Instruct-Turbo` | 72B | 131,072 | High quality |
| `Qwen/Qwen2.5-7B-Instruct-Turbo` | 7B | 131,072 | Fast |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | 32B | 131,072 | Code specialist |
| `Qwen/Qwen2-72B-Instruct` | 72B | 131,072 | |
| `Qwen/QwQ-32B-Preview` | 32B | 32,768 | Reasoning model |

### DeepSeek

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `deepseek-ai/DeepSeek-R1` | 671B | 131,072 | Reasoning, MoE |
| `deepseek-ai/DeepSeek-R1-Distill-Llama-70B` | 70B | 131,072 | Distilled reasoning |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | 14B | 131,072 | Smaller reasoning |
| `deepseek-ai/DeepSeek-V3` | 671B | 131,072 | General MoE |
| `deepseek-ai/deepseek-llm-67b-chat` | 67B | 4,096 | Older |

### Google Gemma

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `google/gemma-2-9b-it` | 9B | 8,192 | |
| `google/gemma-2-27b-it` | 27B | 8,192 | |

### Microsoft Phi

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `microsoft/phi-2` | 2.7B | 2,048 | Small, efficient |
| `microsoft/WizardLM-2-8x22B` | 8x22B | 65,536 | Instruction following |

### NovaSky / Berkeley

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `NovaSky-AI/Sky-T1-32B-Preview` | 32B | 32,768 | Reasoning model |

---

## Embedding Models

| Model ID | Dimensions | Max Tokens | Notes |
|---|---|---|---|
| `togethercomputer/m2-bert-80M-2k-retrieval` | 768 | 2,048 | Fast retrieval |
| `togethercomputer/m2-bert-80M-8k-retrieval` | 768 | 8,192 | Longer context |
| `togethercomputer/m2-bert-80M-32k-retrieval` | 768 | 32,768 | Long context |
| `BAAI/bge-large-en-v1.5` | 1,024 | 512 | High quality |
| `BAAI/bge-base-en-v1.5` | 768 | 512 | Balanced |
| `WhereIsAI/UAE-Large-V1` | 1,024 | 512 | |
| `sentence-transformers/msmarco-bert-base-dot-v5` | 768 | 512 | MS MARCO |

---

## Image Generation Models

| Model ID | Notes |
|---|---|
| `black-forest-labs/FLUX.1-schnell` | Fast, free tier |
| `black-forest-labs/FLUX.1-schnell-Free` | Free |
| `black-forest-labs/FLUX.1-dev` | High quality |
| `black-forest-labs/FLUX.1.1-pro` | Best FLUX quality |
| `stabilityai/stable-diffusion-xl-base-1.0` | SDXL |
| `runwayml/stable-diffusion-v1-5` | Classic SD |

---

## Code Models

| Model ID | Parameters | Context | Notes |
|---|---|---|---|
| `Qwen/Qwen2.5-Coder-32B-Instruct` | 32B | 131,072 | Best code model |
| `codellama/CodeLlama-70b-Instruct-hf` | 70B | 16,384 | Code Llama |
| `codellama/CodeLlama-34b-Instruct-hf` | 34B | 16,384 | |
| `codellama/CodeLlama-13b-Instruct-hf` | 13B | 16,384 | |
| `codellama/CodeLlama-7b-Instruct-hf` | 7B | 16,384 | |

---

## Model Selection Guide

| Use Case | Recommended Model |
|---|---|
| General chat (best quality) | `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| General chat (lowest cost) | `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` |
| Largest/highest capability | `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo` |
| Reasoning / math | `deepseek-ai/DeepSeek-R1` or `Qwen/QwQ-32B-Preview` |
| Code generation | `Qwen/Qwen2.5-Coder-32B-Instruct` |
| Vision/images | `meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo` |
| Embeddings | `BAAI/bge-large-en-v1.5` |
| Image generation | `black-forest-labs/FLUX.1-dev` |
| Free usage | `*-Free` variants |

---

## API: List Models

```python
from together import Together

client = Together()
models = client.models.list()
for model in models:
    print(model.id, model.type)
```

```bash
curl https://api.together.xyz/v1/models \
  -H "Authorization: Bearer $TOGETHER_API_KEY"
```
