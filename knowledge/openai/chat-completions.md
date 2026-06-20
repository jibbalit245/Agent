# OpenAI Chat Completions API
> Source: https://platform.openai.com/docs/api-reference/chat
> Fetched: 2026-06-20

## Endpoint

```
POST https://api.openai.com/v1/chat/completions
```

## Request Format

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model ID (e.g., `gpt-4o`, `gpt-4.1`, `o3`) |
| `messages` | array | List of message objects comprising the conversation |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | 1.0 | Sampling temperature 0–2. Higher = more random |
| `top_p` | float | 1.0 | Nucleus sampling; alternative to temperature |
| `max_tokens` | int | model max | Maximum tokens to generate in the response |
| `max_completion_tokens` | int | — | Total token budget including reasoning tokens (o-series) |
| `stream` | bool | false | Enable server-sent events streaming |
| `tools` | array | — | List of tool definitions for function calling |
| `tool_choice` | string/obj | `"auto"` | Controls tool use: `"auto"`, `"none"`, `"required"`, or specific tool |
| `response_format` | object | — | `{"type": "json_object"}` or structured output schema |
| `n` | int | 1 | Number of completion choices to generate |
| `stop` | string/array | — | Up to 4 sequences where the API stops generating |
| `presence_penalty` | float | 0 | -2.0 to 2.0, penalizes new topics |
| `frequency_penalty` | float | 0 | -2.0 to 2.0, penalizes repetition |
| `user` | string | — | Unique end-user ID for abuse monitoring |
| `seed` | int | — | For deterministic outputs (best-effort) |
| `logprobs` | bool | false | Return log probabilities of tokens |

## Message Roles

### System Message
Sets behavior/persona for the assistant. Some models use `"developer"` role instead of `"system"`.

```python
{"role": "system", "content": "You are a helpful assistant that speaks like a pirate."}
```

### User Message
Input from the human user.

```python
{"role": "user", "content": "What is 2 + 2?"}
```

### Assistant Message
Prior assistant output (used in multi-turn conversations).

```python
{"role": "assistant", "content": "2 + 2 equals 4."}
```

### Tool Message
Result returned from a tool call.

```python
{"role": "tool", "content": "72°F", "tool_call_id": "call_abc123"}
```

## Basic Python Example

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum entanglement in one sentence."}
    ],
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)
# Usage info:
print(f"Tokens used: {response.usage.total_tokens}")
```

## Response Format

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1720000000,
  "model": "gpt-4o-2024-11-20",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum entanglement is when..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 45,
    "total_tokens": 70,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```

**`finish_reason` values**: `"stop"` (natural end), `"length"` (hit max_tokens), `"tool_calls"` (model wants to call a tool), `"content_filter"` (safety filter triggered)

## Streaming

Set `stream=True` to receive server-sent events (SSE). Each chunk has a `delta` field instead of `message`.

```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Count to 5."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

Stream chunk format:
```json
{
  "object": "chat.completion.chunk",
  "choices": [{"delta": {"content": "1, "}, "finish_reason": null}]
}
```

Final chunk has `finish_reason` set and content delta is `null`.

## Tool Use (Function Calling)

Define tools in the request, then handle `tool_calls` in the response.

### Step 1 — Define tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. 'San Francisco, CA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
            "strict": True  # enforce exact schema adherence
        }
    }
]
```

### Step 2 — Call with tools

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message
if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(tool_call.function.name)       # "get_weather"
    print(tool_call.function.arguments)  # '{"location": "Paris"}'
```

### Step 3 — Return tool result

```python
import json

args = json.loads(tool_call.function.arguments)
result = get_weather(args["location"])  # your actual function

messages = [
    {"role": "user", "content": "What's the weather in Paris?"},
    message,  # assistant message with tool_calls
    {
        "role": "tool",
        "content": str(result),
        "tool_call_id": tool_call.id
    }
]

final_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools
)
print(final_response.choices[0].message.content)
```

**`tool_choice` options**:
- `"auto"` — model decides whether to call tools (default)
- `"none"` — no tools
- `"required"` — must call at least one tool
- `{"type": "function", "function": {"name": "get_weather"}}` — force specific tool

## JSON Mode

Force the model to output valid JSON. Always instruct the model to produce JSON in the system prompt too.

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Respond only with valid JSON."},
        {"role": "user", "content": "Give me 3 fruits with colors."}
    ],
    response_format={"type": "json_object"}
)
```

## Structured Outputs (Preferred over JSON Mode)

Structured Outputs guarantee the response matches a specific JSON schema. Preferred over raw JSON mode.

```python
from pydantic import BaseModel

class Fruit(BaseModel):
    name: str
    color: str

class FruitList(BaseModel):
    fruits: list[Fruit]

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": "List 3 fruits with their colors."}],
    response_format=FruitList
)

data = response.choices[0].message.parsed
print(data.fruits)
```

## Vision (Image Input)

Pass images as `image_url` content blocks in user messages.

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/photo.jpg",
                        # or base64: "data:image/jpeg;base64,/9j/4AAQ..."
                        "detail": "auto"  # "low", "high", or "auto"
                    }
                }
            ]
        }
    ]
)
```

**Detail levels**:
- `"low"` — 85 tokens, low-res 512x512 view (good for classification)
- `"high"` — additional 170 tokens per 512x512 tile (good for reading text in images)
- `"auto"` — model chooses based on image size

## Multi-Turn Conversation

Maintain history manually by appending messages:

```python
history = [{"role": "system", "content": "You are a helpful assistant."}]

def chat(user_input):
    history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="gpt-4o", messages=history)
    assistant_msg = response.choices[0].message
    history.append({"role": "assistant", "content": assistant_msg.content})
    return assistant_msg.content
```

## Responses API (New Alternative)

OpenAI now offers a **Responses API** as an evolution of Chat Completions. It offers built-in state management, built-in tools (web search, code interpreter, file search), and a simpler multi-turn interface. For new projects, consider using the Responses API. Migration guide: https://developers.openai.com/api/docs/guides/migrate-to-responses

## Sources
- [Chat Completions Overview | OpenAI API Reference](https://developers.openai.com/api/reference/chat-completions/overview)
- [Function calling | OpenAI API](https://developers.openai.com/api/docs/guides/function-calling)
- [Streaming API responses | OpenAI API](https://developers.openai.com/api/docs/guides/streaming-responses)
- [Structured model outputs | OpenAI API](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Migrate to the Responses API | OpenAI API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
