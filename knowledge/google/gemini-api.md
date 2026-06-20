# Gemini API (Google AI Studio)  
> Source: https://ai.google.dev/gemini-api/docs/quickstart  
> Fetched: 2026-06-20

## Overview

The Gemini API (via Google AI Studio) is the simpler, developer-friendly path to using Google's Gemini models. It uses a single API key (`GEMINI_API_KEY`) rather than OAuth or service accounts. Google AI Studio provides a free tier for experimentation.

## Authentication: GEMINI_API_KEY vs OAuth

- **Google AI Studio / Gemini API**: Uses a simple API key (`GEMINI_API_KEY`). Get one at [aistudio.google.com](https://aistudio.google.com). API keys start with the prefix `AIza`.
- **Vertex AI**: Uses OAuth/service accounts (Application Default Credentials). More complex but needed for enterprise/production.

The Gemini API and Vertex AI both access the same underlying Gemini models, but through different auth mechanisms and endpoints.

## Installation

```bash
pip install google-genai
```

## Basic Usage

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

# Single turn
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works"
)
print(response.text)
```

## Environment Variable Setup

```bash
export GEMINI_API_KEY="AIza..."
```

```python
import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

## Chat (Multi-turn)

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
chat = client.chats.create(model="gemini-2.0-flash")

response = chat.send_message("Hello world!")
print(response.text)

response = chat.send_message("Explain to me how AI works")
print(response.text)

# View history
for message in chat.get_history():
    print(f'role - {message.role}: {message.parts[0].text}')
```

## Model IDs

Current models (as of mid-2026):

| Model ID | Context Window | Notes |
|----------|---------------|-------|
| `gemini-2.5-flash` | 1M tokens | Fast, cost-effective; recommended default |
| `gemini-2.5-pro` | 2M tokens | Most capable, largest context |
| `gemini-2.0-flash` | 1M tokens | Previous gen (note: gemini-2.0-flash-001 discontinued June 2026) |
| `gemini-1.5-pro` | 2M tokens | Older, supports context caching |
| `gemini-1.5-flash` | 1M tokens | Older fast variant |

Note: Models like `gemini-3.5-flash` (launched Google I/O 2026) and `gemini-3.1-pro` (2M context) are the latest generation. Always check the [models page](https://ai.google.dev/gemini-api/docs/models) for current availability.

## Listing Available Models Programmatically

```python
client = genai.Client(api_key="GEMINI_API_KEY")
for model in client.models.list():
    print(model.name, model.input_token_limit)
```

## Multimodal Support

Gemini models are natively multimodal — they accept text, images, audio, video, and documents in a single prompt.

```python
import PIL.Image
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
image = PIL.Image.open("photo.jpg")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["Describe this image:", image]
)
print(response.text)
```

## Key Differences: Gemini API vs Vertex AI

| Feature | Gemini API (AI Studio) | Vertex AI |
|---------|----------------------|-----------|
| Auth | API key | OAuth / service account |
| Free tier | Yes (rate-limited) | No (pay-per-use only) |
| Setup complexity | Simple | Complex (requires GCP project) |
| Enterprise features | Limited | Full (IAM, VPC, audit logs) |
| Model access | Most Gemini models | All Gemini + Model Garden |
| Best for | Dev/prototyping | Production / enterprise |

## Free Tier Limits (as of 2026)

- Free tier limited to Flash and Flash-Lite models (Pro models are paid-only as of April 2026)
- ~250,000 tokens per minute (TPM) across free tier
- ~10 requests per minute (RPM) for Flash models
- ~1,500 requests per day (RPD)
- Note: Google reduced free tier quotas significantly in December 2025 (~50-80%)

## References

- [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)
- [Available Models](https://ai.google.dev/gemini-api/docs/models)
- [Google Gen AI Python SDK](https://googleapis.github.io/python-genai/)
- [Google AI Studio](https://aistudio.google.com)
