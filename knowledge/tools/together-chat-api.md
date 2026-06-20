# Together AI Chat API

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/docs/chat-overview — content below is from model training data (knowledge cutoff August 2025).

## Overview

Together AI's chat completions API is OpenAI-compatible and supports multi-turn conversations, streaming, function calling, vision, and JSON mode.

**Endpoint:** `POST https://api.together.xyz/v1/chat/completions`

---

## Basic Chat Completion

### Python (Together SDK)

```python
from together import Together

client = Together(api_key="your_api_key")

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is quantum computing?"},
    ],
)

print(response.choices[0].message.content)
```

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="your_together_api_key",
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[
        {"role": "user", "content": "What is quantum computing?"},
    ],
)

print(response.choices[0].message.content)
```

### JavaScript

```javascript
import Together from "together-ai";

const client = new Together();

const response = await client.chat.completions.create({
  model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  messages: [{ role: "user", content: "What is quantum computing?" }],
});

console.log(response.choices[0].message.content);
```

---

## All Parameters

```python
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",  # Required
    messages=[...],                                      # Required
    max_tokens=1024,                # Max tokens to generate
    temperature=0.7,                # 0.0–2.0 (default 0.7 for Together)
    top_p=0.7,                      # Nucleus sampling
    top_k=50,                       # Top-k sampling
    repetition_penalty=1.0,         # 1.0 = no penalty
    stop=["</s>", "[INST]"],        # Stop sequences
    stream=False,                   # Enable streaming
    n=1,                            # Number of completions (usually 1)
    logprobs=1,                     # Number of logprob tokens
    echo=False,                     # Echo prompt in response
    safety_model=None,              # Optional safety classifier
    response_format={"type": "text"}, # "text" or "json_object"
    tools=None,                     # Tool/function definitions
    tool_choice="auto",             # Tool selection
    seed=None,                      # Random seed
)
```

**Parameter Reference:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | string | required | Model ID |
| `messages` | array | required | Conversation messages |
| `max_tokens` | integer | 512 | Maximum output tokens |
| `temperature` | float | 0.7 | Randomness (0.0–2.0) |
| `top_p` | float | 0.7 | Nucleus sampling |
| `top_k` | integer | 50 | Top-k sampling |
| `repetition_penalty` | float | 1.0 | Penalize repetition |
| `stop` | string/array | null | Stop sequences |
| `stream` | boolean | false | Stream tokens |
| `n` | integer | 1 | Number of completions |
| `logprobs` | integer | null | Number of logprob tokens |
| `echo` | boolean | false | Include prompt in output |
| `safety_model` | string | null | Safety classifier model |
| `response_format` | object | `{"type":"text"}` | Output format |
| `tools` | array | null | Function definitions |
| `tool_choice` | string/object | "auto" | How to use tools |
| `seed` | integer | null | Random seed |

---

## Streaming

### Python Streaming

```python
stream = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Write a poem about the ocean."}],
    stream=True,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()
```

### JavaScript Streaming

```javascript
const stream = await client.chat.completions.create({
  model: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  messages: [{ role: "user", content: "Write a poem about the ocean." }],
  stream: true,
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || "");
}
```

---

## JSON Mode

```python
import json

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[
        {
            "role": "system",
            "content": "Respond with valid JSON only."
        },
        {
            "role": "user",
            "content": "List 3 programming languages with their year of creation."
        }
    ],
    response_format={"type": "json_object"},
)

data = json.loads(response.choices[0].message.content)
print(data)
```

---

## Multi-Turn Conversation

```python
from together import Together

client = Together()

def chat_session():
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."}
    ]
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=messages,
            max_tokens=1024,
        )
        
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        
        print(f"Assistant: {assistant_message}\n")

chat_session()
```

---

## Vision / Image Input

For vision-capable models:

```python
response = client.chat.completions.create(
    model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What do you see in this image?"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image.jpg"}
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
    b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                }
            ]
        }
    ],
)
```

---

## Function Calling / Tool Use

```python
import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

messages = [{"role": "user", "content": "What's the weather like in Boston?"}]

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

message = response.choices[0].message

if message.tool_calls:
    messages.append(message)
    
    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        # Execute function...
        result = {"temperature": 72, "condition": "sunny"}
        
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })
    
    final = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=messages,
        tools=tools,
    )
    print(final.choices[0].message.content)
```

---

## Safety Models

Together AI offers optional content moderation:

```python
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "..."}],
    safety_model="Meta-Llama/Llama-Guard-7b",
)
```

Available safety models:
- `Meta-Llama/Llama-Guard-7b`
- `meta-llama/Meta-Llama-Guard-2-8B`

---

## Response Object

```json
{
  "id": "8857c763d9864571a4b3b9a8",
  "object": "chat.completion",
  "created": 1719000000,
  "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "eos",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 10,
    "total_tokens": 38
  }
}
```

---

## Async Usage

```python
import asyncio
from together import AsyncTogether

client = AsyncTogether()

async def main():
    response = await client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

---

## Error Handling

```python
from together import Together
from together.error import TogetherException, RateLimitError, AuthenticationError

client = Together()

try:
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[{"role": "user", "content": "Hello"}],
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except TogetherException as e:
    print(f"API error: {e}")
```
