# Groq Text Chat

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/text-chat — content below is from model training data (knowledge cutoff August 2025).

## Overview

The chat completions endpoint is Groq's primary interface for text generation. It follows the OpenAI Chat Completions API format.

**Endpoint:** `POST https://api.groq.com/openai/v1/chat/completions`

---

## Message Roles

| Role | Description |
|---|---|
| `system` | Sets the assistant's behavior and persona |
| `user` | Input from the human |
| `assistant` | The model's previous responses |
| `tool` | Results from tool/function calls |

---

## Basic Chat Completion

```python
from groq import Groq

client = Groq()

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that answers concisely."
        },
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(response.choices[0].message.content)
# Output: "Paris"
```

---

## Multi-Turn Conversation

```python
from groq import Groq

client = Groq()

messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

def chat(user_message):
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )
    
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

print(chat("My name is Alice."))
print(chat("What's my name?"))  # Should remember "Alice"
```

---

## System Prompts

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": """You are an expert Python programmer.
            - Always provide working code examples
            - Explain your code with comments
            - Suggest best practices"""
        },
        {
            "role": "user",
            "content": "How do I read a CSV file?"
        }
    ],
)
```

---

## All Request Parameters

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",      # Required: model ID
    messages=[...],                          # Required: message array
    temperature=0.7,                         # 0.0-2.0, default 1.0
    max_tokens=1024,                         # Max output tokens
    top_p=0.9,                              # Nucleus sampling (0.0-1.0)
    frequency_penalty=0.0,                   # Penalize repeated tokens (-2.0 to 2.0)
    presence_penalty=0.0,                    # Penalize new topics (-2.0 to 2.0)
    stop=["\n", "User:"],                    # Stop sequences
    stream=False,                            # Enable streaming
    n=1,                                     # Number of completions
    seed=42,                                 # Reproducibility (beta)
    response_format={"type": "json_object"}, # Force JSON output
    user="user-123",                         # End-user identifier
    logprobs=True,                           # Return log probabilities
    top_logprobs=5,                          # Top N logprobs (requires logprobs=True)
)
```

---

## JSON Mode

Force the model to output valid JSON:

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a data extractor. Always respond with valid JSON."
        },
        {
            "role": "user",
            "content": "Extract: name='Alice', age=30, city='NYC'"
        }
    ],
    response_format={"type": "json_object"},
)

import json
data = json.loads(response.choices[0].message.content)
print(data)  # {"name": "Alice", "age": 30, "city": "NYC"}
```

---

## Streaming

```python
from groq import Groq

client = Groq()

with client.chat.completions.stream(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a short poem about AI"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Or using the create method with stream=True:
stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a short poem about AI"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
```

---

## Async Usage

```python
import asyncio
from groq import AsyncGroq

client = AsyncGroq()

async def main():
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

---

## Async Streaming

```python
import asyncio
from groq import AsyncGroq

client = AsyncGroq()

async def main():
    stream = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True,
    )
    
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)

asyncio.run(main())
```

---

## Token Counting / Usage

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)

usage = response.usage
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")
```

---

## Finish Reasons

| Reason | Meaning |
|---|---|
| `stop` | Model stopped naturally (end of response or stop sequence) |
| `length` | Hit `max_tokens` limit |
| `tool_calls` | Model wants to call a function/tool |
| `content_filter` | Content was filtered |

---

## Vision / Image Input

For vision-capable models (`llama-3.2-90b-vision-preview`):

```python
response = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ],
)
```

### Base64 Image

```python
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ],
)
```

---

## Error Handling

```python
from groq import Groq, AuthenticationError, RateLimitError, APIError

client = Groq()

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello"}],
    )
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```
