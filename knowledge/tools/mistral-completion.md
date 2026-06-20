# Mistral AI Chat Completions

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/capabilities/completion/ — content below is from model training data (knowledge cutoff August 2025).

## Overview

Mistral's chat completions API supports multi-turn conversations, streaming, JSON mode, vision, and function calling. It's OpenAI-compatible for easy migration.

**Endpoint:** `POST https://api.mistral.ai/v1/chat/completions`

---

## Basic Usage

### Python (Mistral SDK)

```python
from mistralai import Mistral

client = Mistral(api_key="your_api_key")

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "user", "content": "What is the best French cheese?"}
    ],
)

print(response.choices[0].message.content)
```

### Python (OpenAI SDK — Compatible)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.mistral.ai/v1",
    api_key="your_mistral_api_key",
)

response = client.chat.completions.create(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### cURL

```bash
curl -X POST https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [
      {"role": "user", "content": "What is the best French cheese?"}
    ]
  }'
```

---

## Parameters

```python
response = client.chat.complete(
    model="mistral-large-latest",      # Required
    messages=[...],                    # Required
    temperature=0.7,                   # 0.0–1.0 (Mistral range is 0-1, not 0-2!)
    top_p=1.0,                         # Nucleus sampling
    max_tokens=None,                   # None = model default
    stream=False,                      # Streaming
    safe_prompt=False,                 # Prepend safety system prompt
    random_seed=None,                  # Integer for reproducibility
    response_format={"type": "text"},  # "text" or "json_object"
    tools=None,                        # Tool definitions
    tool_choice="auto",                # Tool selection
)
```

---

## System Prompts

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {
            "role": "system",
            "content": """You are an expert French chef.
            Always recommend traditional French cuisine.
            Be enthusiastic about food."""
        },
        {
            "role": "user",
            "content": "What should I cook for dinner?"
        }
    ],
)
```

---

## Multi-Turn Conversation

```python
from mistralai import Mistral

client = Mistral()

messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

def chat(user_message: str) -> str:
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=messages,
    )
    
    assistant_msg = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_msg})
    
    return assistant_msg

print(chat("My name is Marie."))
print(chat("What's my name?"))
```

---

## Streaming

### Python Streaming

```python
stream = client.chat.stream(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Tell me a story"}],
)

for event in stream:
    content = event.data.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()
```

### Async Streaming

```python
import asyncio
from mistralai import AsyncMistral

async def main():
    client = AsyncMistral(api_key="your_key")
    
    async with client.chat.stream(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Tell me a story"}],
    ) as stream:
        async for event in stream:
            content = event.data.choices[0].delta.content
            if content:
                print(content, end="", flush=True)

asyncio.run(main())
```

---

## JSON Mode

```python
import json

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {
            "role": "user",
            "content": """Extract the following information as JSON:
            Name: Alice Johnson
            Age: 32
            Occupation: Software Engineer
            City: Paris"""
        }
    ],
    response_format={"type": "json_object"},
)

data = json.loads(response.choices[0].message.content)
print(data)
# {"name": "Alice Johnson", "age": 32, "occupation": "Software Engineer", "city": "Paris"}
```

---

## Safe Prompt

The `safe_prompt` parameter prepends a safety system prompt:

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "..."}],
    safe_prompt=True,  # Adds safety guardrails
)
```

---

## Vision / Image Input

Using Pixtral models:

```python
response = client.chat.complete(
    model="pixtral-large-latest",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": "https://example.com/image.jpg"
                }
            ]
        }
    ],
)
print(response.choices[0].message.content)
```

### Base64 Image

```python
import base64

with open("image.png", "rb") as f:
    b64_image = base64.b64encode(f.read()).decode()

response = client.chat.complete(
    model="pixtral-large-latest",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image."},
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{b64_image}"
                }
            ]
        }
    ],
)
```

---

## Async Usage

```python
import asyncio
from mistralai import AsyncMistral

async def main():
    client = AsyncMistral(api_key="your_key")
    
    response = await client.chat.complete_async(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

---

## Response Object

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Hello!"}],
)

# Access response
print(response.id)              # Completion ID
print(response.model)           # Model used
print(response.created)         # Unix timestamp
print(response.choices[0].message.role)     # "assistant"
print(response.choices[0].message.content)  # Text content
print(response.choices[0].finish_reason)    # "stop" | "length" | "tool_calls"
print(response.usage.prompt_tokens)
print(response.usage.completion_tokens)
print(response.usage.total_tokens)
```

---

## Reproducibility

```python
# Use random_seed for deterministic outputs
response1 = client.chat.complete(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Pick a number between 1 and 10"}],
    random_seed=42,
    temperature=0.0,
)

response2 = client.chat.complete(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Pick a number between 1 and 10"}],
    random_seed=42,
    temperature=0.0,
)

# response1 and response2 should be identical
```

---

## Error Handling

```python
from mistralai import Mistral
from mistralai.models import SDKError

client = Mistral()

try:
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hello"}],
    )
except SDKError as e:
    print(f"Error: {e.status_code} - {e.message}")
```

---

## Fill-in-Middle (Codestral)

For code completion with prefix and suffix context:

```python
# Requires Codestral API key and different base URL
from mistralai import Mistral

client = Mistral(
    api_key="your_codestral_api_key",
    server_url="https://codestral.mistral.ai"
)

response = client.fim.complete(
    model="codestral-latest",
    prompt="def fibonacci(n):\n    if n <= 1:\n        return n\n    ",
    suffix="\n\nprint(fibonacci(10))",
)
print(response.choices[0].message.content)
# Returns: "return fibonacci(n-1) + fibonacci(n-2)"
```
