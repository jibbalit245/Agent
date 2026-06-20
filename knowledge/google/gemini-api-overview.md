# Google Gemini API Overview

> Source: Fetched from GitHub google-gemini/cookbook and related repositories (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## What is the Gemini API?

The Gemini API provides access to Google's state-of-the-art generative AI models, including the Gemini family of language models, Imagen image generation models, Veo video generation models, and Lyria music generation models.

## Getting Started

### 1. Get an API Key

Create your API key at [Google AI Studio](https://aistudio.google.com/app/apikey) with a single click. Treat API keys with the same care as passwords — avoid committing them to version control.

### 2. Install the SDK

```bash
pip install google-genai
```

Or with uv:
```bash
uv pip install google-genai
```

### 3. Initialize the Client

```python
from google import genai

client = genai.Client(api_key='YOUR_GEMINI_API_KEY')
```

Or use environment variables:
```bash
export GEMINI_API_KEY='your-api-key'
# OR
export GOOGLE_API_KEY='your-api-key'
```

Then:
```python
client = genai.Client()  # Automatically detects GEMINI_API_KEY or GOOGLE_API_KEY
```

### 4. Make Your First Request

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the meaning of life?'
)
print(response.text)
```

## Core Capabilities

| Feature | Description |
|---------|-------------|
| **Text Generation** | Generate text from text prompts |
| **Multimodal Input** | Accept text, images, audio, video, and PDF inputs |
| **Chat / Multi-turn** | Stateful multi-turn conversations |
| **Function Calling** | Define tools the model can invoke |
| **Structured Output** | Force JSON or enum outputs with schemas |
| **System Instructions** | Set model behavior and persona |
| **Streaming** | Real-time streaming of responses |
| **Embeddings** | Convert text/multimodal content to vectors |
| **Context Caching** | Cache prompt prefixes to reduce costs |
| **Code Execution** | Generate and run Python code in-context |
| **Grounding** | Ground responses with Google Search, Maps, YouTube, URLs |
| **Image Generation** | Generate images with Imagen 4 |
| **Video Generation** | Generate videos with Veo 3.1 |
| **Batch API** | Process large volumes of requests asynchronously (50% discount) |
| **Thinking / Reasoning** | Extended reasoning mode for complex tasks |
| **Long Context** | Up to 2M token context windows |

## Available Model Families

### Gemini Models (Text / Multimodal)
- **Gemini 2.5 Flash** — Fast and cost-effective, 1M context window
- **Gemini 2.5 Pro** — Most capable, 2M context window
- **Gemini 2.0 Flash** — Previous generation fast model
- **Gemma 3** — Open-weight models (1B, 4B, 12B, 27B)

### Image Generation
- **Imagen 4.0** — State-of-the-art image generation (Standard, Ultra, Fast)

### Video Generation
- **Veo 3.1** — High-quality video generation

### Music / Audio
- **Lyria 3** — Music generation
- **Lyria RealTime** — Real-time music and podcast generation

### Embeddings
- **gemini-embedding-2** — Multimodal embeddings (text, images, video, audio, PDF)
- **gemini-embedding-001** — Text-only embeddings

## Official SDKs

- **Python**: `google-genai` (v2.9.0+, requires Python 3.10+)
- **Go**
- **Node.js**
- **Java**
- **C#**

## REST API Base URL

```
https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=YOUR_API_KEY
```

Example curl:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[{
          "text": "Please give me Python code to sort a list."
        }]
      }]
    }'
```

## Service Tiers

| Tier | Cost | Latency | Use Case |
|------|------|---------|----------|
| Standard | Full price | Seconds-minutes | General workflows |
| Flex | 50% discount | 1-15 min target | Background tasks, best-effort |
| Priority | +75-100% | Milliseconds | Production, user-facing |
| Batch | 50% discount | Up to 24 hours | Massive datasets |
| Caching | 90% discount | Faster first-token | Recurring queries with same prefix |

## Free Tier

- Available for `gemini-flash` models
- Rate limit: 15 requests per minute
- Not available in EEA, UK, CH without billing activation

## Key Links

- API Key: https://aistudio.google.com/app/apikey
- Cookbook: https://github.com/google-gemini/cookbook
- Python SDK: https://github.com/googleapis/python-genai
- Documentation: https://ai.google.dev/gemini-api/docs
- Pricing: https://ai.google.dev/pricing
