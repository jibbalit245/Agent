# Groq Models

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/models — content below is from model training data (knowledge cutoff August 2025).

## Overview

Groq hosts a curated set of open-source LLMs optimized for high-speed inference on Groq LPU hardware. Models are organized by capability (text, audio, vision).

---

## Text / Chat Models

### Llama 3.3 Series (Meta)

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `llama-3.3-70b-versatile` | 70B | 128,000 tokens | Recommended general-purpose |
| `llama-3.3-70b-specdec` | 70B | 8,192 tokens | Speculative decoding, faster |

### Llama 3.1 Series (Meta)

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `llama-3.1-8b-instant` | 8B | 128,000 tokens | Fast, low latency |
| `llama-3.1-70b-versatile` | 70B | 128,000 tokens | (Deprecated in favor of 3.3) |

### Llama 3 Series (Meta)

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `llama3-8b-8192` | 8B | 8,192 tokens | Older, still available |
| `llama3-70b-8192` | 70B | 8,192 tokens | Older, still available |

### Llama Guard (Meta — Moderation)

| Model ID | Notes |
|---|---|
| `llama-guard-3-8b` | Content moderation / safety classification |
| `llama3-groq-8b-8192-tool-use-preview` | Fine-tuned for tool use |
| `llama3-groq-70b-8192-tool-use-preview` | Fine-tuned for tool use |

### Mixtral (Mistral AI)

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `mixtral-8x7b-32768` | 8x7B MoE | 32,768 tokens | Strong multilingual |

### Gemma (Google)

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `gemma-7b-it` | 7B | 8,192 tokens | Instruction-tuned |
| `gemma2-9b-it` | 9B | 8,192 tokens | Improved version |

### DeepSeek

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `deepseek-r1-distill-llama-70b` | 70B | 128,000 tokens | Reasoning model |

### Qwen (Alibaba)

| Model ID | Parameters | Context Window | Notes |
|---|---|---|---|
| `qwen-qwq-32b` | 32B | 128,000 tokens | Reasoning model |
| `qwen-2.5-72b-instruct` | 72B | 128,000 tokens | |
| `qwen-2.5-coder-32b-instruct` | 32B | 128,000 tokens | Code-focused |

---

## Audio / Speech Models

### Whisper (OpenAI — hosted by Groq)

| Model ID | Notes |
|---|---|
| `whisper-large-v3` | Best accuracy, multilingual |
| `whisper-large-v3-turbo` | Faster, slightly less accurate |
| `distil-whisper-large-v3-en` | English-only, fastest |

---

## Vision / Multimodal Models

| Model ID | Notes |
|---|---|
| `llava-v1.5-7b-4096-preview` | Vision + language (preview) |
| `llama-3.2-11b-vision-preview` | Llama vision (preview) |
| `llama-3.2-90b-vision-preview` | Llama vision large (preview) |

---

## Model Selection Guide

| Use Case | Recommended Model |
|---|---|
| General chat | `llama-3.3-70b-versatile` |
| Low latency / high throughput | `llama-3.1-8b-instant` |
| Tool use / function calling | `llama3-groq-70b-8192-tool-use-preview` |
| Code generation | `qwen-2.5-coder-32b-instruct` |
| Reasoning tasks | `deepseek-r1-distill-llama-70b` or `qwen-qwq-32b` |
| Speech transcription | `whisper-large-v3` |
| Content moderation | `llama-guard-3-8b` |
| Vision tasks | `llama-3.2-90b-vision-preview` |
| Long context | `llama-3.3-70b-versatile` (128K) |

---

## API: List Available Models

```python
from groq import Groq

client = Groq()
models = client.models.list()
for model in models.data:
    print(model.id)
```

```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

---

## Notes

- Models marked `preview` may change or be deprecated without notice.
- Groq regularly adds new models; check the console for the latest list.
- `specdec` variants use speculative decoding for faster output but have smaller context windows.
- All models return standard OpenAI-compatible response objects.
