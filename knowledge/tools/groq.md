# Groq  
> Source: https://console.groq.com/docs/quickstart  
> Fetched: 2026-06-20

## What Is Groq?

Groq is a cloud inference platform built on **LPU (Language Processing Unit)** hardware — custom silicon designed specifically for LLM inference. Key differentiator: **extremely fast inference** (5-14x more tokens per second than GPU-based inference).

- Ultra-low latency inference
- OpenAI-compatible API
- Free tier with no credit card required
- Access to open-source models (Llama, Mixtral, Gemma, etc.)

## Setup

### Get API Key

1. Sign up at [console.groq.com](https://console.groq.com)
2. Navigate to API Keys
3. Create a new key

### Environment Variable

```bash
export GROQ_API_KEY="gsk_..."
```

### Install

```bash
# Official Groq SDK
pip install groq

# Or use OpenAI SDK (Groq is OpenAI-compatible)
pip install openai
```

## Python Usage — Groq SDK

```python
from groq import Groq

client = Groq()  # reads GROQ_API_KEY from env

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing briefly."}
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=1024,
)

print(chat_completion.choices[0].message.content)
```

## Python Usage — OpenAI SDK (Compatible)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-groq-api-key",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## API Base URL

```
https://api.groq.com/openai/v1
```

## Streaming

```python
from groq import Groq

client = Groq()

stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

## Available Models (mid-2026)

| Model | Context Window | Notes |
|-------|---------------|-------|
| `llama-3.3-70b-versatile` | 128K | Best overall on free tier |
| `llama-3.1-8b-instant` | 128K | Fastest, smallest |
| `llama-3.1-70b-versatile` | 128K | Previous gen 70B |
| `llama3-groq-70b-8192-tool-use-preview` | 8K | Tool/function calling |
| `llama3-groq-8b-8192-tool-use-preview` | 8K | Tool use, fast |
| `mixtral-8x7b-32768` | 32K | Mistral MoE model |
| `gemma-7b-it` | 8K | Google Gemma |
| `gemma2-9b-it` | 8K | Google Gemma 2 |
| `llama-4-maverick` | 128K+ | Llama 4 (may have limits) |
| `openai/gpt-oss-120b` | - | OpenAI OSS model |

Check [console.groq.com/docs/models](https://console.groq.com/docs/models) for current availability.

## Rate Limits (Free Tier, mid-2026)

**Default limits (most models):**
- 30 RPM (requests per minute)
- 6,000 TPM (tokens per minute)
- 1,000 RPD (requests per day)

**Model-specific variations:**
- `llama-3.3-70b-versatile`: 30 RPM / 12K TPM / 1K RPD
- `llama-4-maverick`: 15 RPM / 3,000 TPM / 500 RPD (half quota)
- `gemma2-9b-it`: 30 RPM / 15,000 TPM (higher TPM)

**Paid plans** offer significantly higher limits — check [console.groq.com/settings/limits](https://console.groq.com/settings/limits).

## Function/Tool Calling

```python
from groq import Groq
import json

client = Groq()

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. 'San Francisco, CA'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="llama3-groq-70b-8192-tool-use-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto",
)

tool_call = response.choices[0].message.tool_calls[0]
print(f"Function: {tool_call.function.name}")
print(f"Args: {tool_call.function.arguments}")
```

## JSON Mode

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "List 3 fruits in JSON format with keys: name, color"}],
    response_format={"type": "json_object"},
)
print(json.loads(response.choices[0].message.content))
```

## Pricing

- **Free tier**: All supported models available, no credit card required
- **Paid plans**: Higher rate limits, higher throughput
- Per-token pricing applies on paid tiers — Groq is generally very competitive
- **Batch API + prompt caching**: Can reduce costs to ~25% of on-demand pricing

Check [groq.com/pricing](https://groq.com/pricing) for current rates.

## Speed Comparison

Groq LPU hardware achieves:
- 500-800 tokens/second for 7B-8B models
- 250-400 tokens/second for 70B models

Compared to typical GPU inference (50-150 tokens/second), Groq is 5-14x faster. Ideal for:
- Real-time chat applications
- Interactive coding assistants
- Low-latency agent loops
- Time-sensitive batch processing

## Audio (Whisper)

Groq also provides fast Whisper transcription:

```python
with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=audio_file,
    )
print(transcription.text)
```

## Using with LiteLLM

```python
from litellm import completion
import os

os.environ["GROQ_API_KEY"] = "gsk_..."

response = completion(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## References

- [Groq Quickstart](https://console.groq.com/docs/quickstart)
- [Groq Models](https://console.groq.com/docs/models)
- [OpenAI Compatibility](https://console.groq.com/docs/openai)
- [Rate Limits](https://console.groq.com/docs/rate-limits)
- [Groq GitHub Examples](https://github.com/groq/groq-python)
