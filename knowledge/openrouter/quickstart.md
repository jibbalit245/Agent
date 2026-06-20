# OpenRouter Quickstart
> Source: https://openrouter.ai/docs/quick-start
> Fetched: 2026-06-20

## What is OpenRouter?

OpenRouter is a unified API gateway that provides access to 315+ AI models from dozens of providers (Anthropic, OpenAI, Google, Meta, Mistral, DeepSeek, Qwen, and more) through a single endpoint. It is fully OpenAI-compatible — change the base URL and API key in existing code and everything else works unchanged.

Key features:
- **One API key** for all major model providers
- **Automatic fallback** routing if a provider is down or rate-limited
- **Free tier** with 28+ free models (no credit card required)
- **Pass-through pricing** — OpenRouter charges 5.5% on credit purchases and passes through provider token prices exactly
- **Leaderboards and analytics** for your app usage

## Getting an API Key

1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Navigate to **Keys** in your dashboard
4. Click **Create Key**
5. Copy the key — it starts with `sk-or-v1-...`

Set as environment variable:
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

## Base URL

```
https://openrouter.ai/api/v1
```

## Authentication

```
Authorization: Bearer sk-or-v1-...
```

## Required vs Optional Headers

```http
Authorization: Bearer sk-or-v1-...     # REQUIRED
HTTP-Referer: https://yourapp.com       # Optional — identifies your app (used for analytics/leaderboards)
X-Title: My App Name                    # Optional — your app name (used for analytics/leaderboards)
Content-Type: application/json          # Required for POST requests
```

The `HTTP-Referer` and `X-Title` headers are optional but recommended — they allow your app to appear on OpenRouter's leaderboards and help with support.

## Quickstart Code Examples

### Python (requests)
```python
import os
import requests

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "HTTP-Referer": "https://myapp.example.com",
        "X-Title": "My App",
        "Content-Type": "application/json"
    },
    json={
        "model": "anthropic/claude-sonnet-4-6",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
print(response.json()["choices"][0]["message"]["content"])
```

### Python (OpenAI SDK)
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://myapp.example.com",
        "X-Title": "My App"
    }
)

response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Node.js (OpenAI SDK)
```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: "https://openrouter.ai/api/v1",
  defaultHeaders: {
    "HTTP-Referer": "https://myapp.example.com",
    "X-Title": "My App"
  }
});

const response = await client.chat.completions.create({
  model: "anthropic/claude-sonnet-4-6",
  messages: [{ role: "user", content: "Hello!" }]
});
console.log(response.choices[0].message.content);
```

### Using Free Models (no credits needed)
```python
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={
        "model": "deepseek/deepseek-r1:free",   # :free suffix for free tier
        "messages": [{"role": "user", "content": "Hello!"}]
    }
)
```

## Model ID Format

All model IDs follow the pattern: `{provider}/{model-name}`

Free tier models append `:free`: `{provider}/{model-name}:free`

Examples:
- `anthropic/claude-sonnet-4-6`
- `openai/gpt-4o`
- `google/gemini-flash-1.5`
- `meta-llama/llama-3.3-70b-instruct`
- `deepseek/deepseek-r1:free`

## OpenAI SDK Compatibility

OpenRouter is a drop-in replacement for the OpenAI API. Any code using the OpenAI SDK works by changing:
1. `base_url` → `https://openrouter.ai/api/v1`
2. `api_key` → your OpenRouter key
3. `model` → use OpenRouter model IDs (`anthropic/claude-sonnet-4-6` instead of `claude-sonnet-4-6`)
