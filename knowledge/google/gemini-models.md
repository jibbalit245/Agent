# Google Gemini API: Models Reference

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Listing Models

```python
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)

for model in client.models.list():
    print(model.name)
```

## Available Gemini Models

### Gemini 2.5 Series

| Model | Input Tokens | Output Tokens | Key Features |
|-------|-------------|---------------|--------------|
| `gemini-2.5-pro` | 2,000,000 (2M) | Variable | Most capable, deepest reasoning |
| `gemini-2.5-flash` | 1,048,576 (1M) | 65,536 | Fast + capable, thinking budget 0-24,576 |
| `gemini-2.5-flash-lite` | 1,048,576 (1M) | Variable | Lightweight, thinking budget 0-24,576 |

### Gemini 2.0 Series

| Model | Key Features |
|-------|-------------|
| `gemini-2.0-flash` | Previous generation fast |
| `gemini-2.0-flash-exp` | Experimental 2.0 flash |
| `gemini-2.0-pro-exp` | Experimental 2.0 pro |
| `gemini-2.0-flash-thinking-exp` | Thinking variant |

### Gemma (Open-Weight) Series

| Model | Parameters |
|-------|-----------|
| `gemma-3-1b-it` | 1B |
| `gemma-3-4b-it` | 4B |
| `gemma-3-12b-it` | 12B |
| `gemma-3-27b-it` | 27B |

### Latest Aliases

- `gemini-flash-latest` — Always points to latest flash model
- `gemini-pro-latest` — Always points to latest pro model

### Specialized Models

| Model | Purpose |
|-------|---------|
| `learnlm-2.0-flash-experimental` | Educational/learning tasks |
| `gemini-robotics-er-1.5-preview` | Robotics spatial understanding |

## Embedding Models

Query models supporting `embedContent` action:

```python
for model in client.models.list():
    if "embedContent" in model.supported_actions:
        print(model.name)
```

| Model | Capability |
|-------|-----------|
| `gemini-embedding-2` | Multimodal (text, images, video, audio, PDFs) — 3,072 dimensions |
| `gemini-embedding-001` | Text-only — legacy |
| `text-embedding-004` | Text-only |
| `gemini-embedding-exp-03-07` | Experimental |
| `embedding-001` | Legacy |

## Image Generation Models

| Model | Description |
|-------|-------------|
| `imagen-4.0-generate-001` | Standard — best balance of quality/cost |
| `imagen-4.0-ultra-generate-001` | Highest quality, 1 image per request |
| `imagen-4.0-fast-generate-001` | Faster, lower cost |
| `imagen-3.0-generate-002` | Previous generation |

## Video Generation Models

| Model | Description |
|-------|-------------|
| `veo-3.0-generate-001` | Standard Veo 3 |
| `veo-3.0-fast-generate-001` | Fast Veo 3 |
| `veo-3.1-generate-preview` | Latest preview |

## Supported Actions

Models support various capabilities:

| Action | Description |
|--------|-------------|
| `generateContent` | Primary prompting method |
| `countTokens` | Token calculation |
| `createCachedContent` | Prompt caching |
| `batchGenerateContent` | Batch processing |
| `embedContent` | Embedding generation |
| `generateImages` | Image generation (Imagen) |
| `generateVideos` | Video generation (Veo) |

## Get Model Details

```python
for model in client.models.list():
    if model.name == "models/gemini-2.5-flash":
        print(model)
```

Example output for Gemini 2.5 Flash:
```
Model: Gemini 2.5 Flash
- Input Token Limit: 1,048,576
- Output Token Limit: 65,536
- Supported Actions: generateContent, countTokens, 
                      createCachedContent, batchGenerateContent
```

## Thinking Model Configuration

All Gemini 2.5+ models are thinking models by default:

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=4096  # 0 disables thinking (not available on Pro)
        )
    )
)
```

Thinking token budgets:
- **Gemini 2.5 Flash / Flash-Lite**: 0 to 24,576 tokens
- **Gemini 2.5 Pro**: 128 to 32,768 tokens

## Token Counting Equivalency

- 1 token ≈ 4 characters
- 100 tokens ≈ 60-80 English words
