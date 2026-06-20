# OpenAI Responses API
> Source: https://developers.openai.com/api/reference/responses/overview
> Fetched: 2026-06-20

## Overview

The **Responses API** is OpenAI's most advanced interface for generating model responses. It is the recommended API for new projects, especially agentic applications. It offers:

- **Stateful conversations** — pass `previous_response_id` to link responses, avoiding manual history management
- **Built-in tools** — web search, file search, code interpreter, computer use, image generation
- **Better performance** — 40–80% improved cache utilization vs. Chat Completions
- **Simpler agentic loops** — model can call multiple tools in a single API request

---

## Endpoint

```
POST https://api.openai.com/v1/responses
```

---

## Basic Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o",
    input="Tell me a joke about programming."
)

print(response.output_text)
```

---

## Core Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID |
| `input` | string or array | Yes | User message (string) or array of message objects |
| `instructions` | string | No | System-level instructions (replaces system message) |
| `previous_response_id` | string | No | ID of a prior response to continue the conversation |
| `tools` | array | No | Built-in tools or function definitions |
| `tool_choice` | string/object | No | `"auto"`, `"none"`, `"required"`, or specific tool |
| `store` | bool | No | Whether to store the response for multi-turn (`true` by default) |
| `stream` | bool | No | Enable streaming output |
| `temperature` | float | No | Sampling temperature 0–2 |
| `top_p` | float | No | Nucleus sampling |
| `max_output_tokens` | int | No | Maximum response tokens |
| `reasoning` | object | No | For o-series models: `{"effort": "low"|"medium"|"high"}` |
| `text` | object | No | Text output configuration |
| `metadata` | object | No | Custom key-value pairs |

---

## Multi-Turn Conversations (Stateful)

The Responses API handles conversation state. You can either:

### Option 1: Chain via previous_response_id (Simple)

```python
# First turn
response1 = client.responses.create(
    model="gpt-4o",
    input="My name is Alice."
)

# Second turn — links to first response
response2 = client.responses.create(
    model="gpt-4o",
    input="What's my name?",
    previous_response_id=response1.id
)

print(response2.output_text)  # "Your name is Alice."
```

### Option 2: Conversation object (Persistent threads)

```python
# Create a persistent conversation
conversation = client.conversations.create(
    model="gpt-4o",
    system="You are a helpful assistant."
)

# Add messages to it
response = client.conversations.responses.create(
    conversation_id=conversation.id,
    input="What's the capital of France?"
)
```

---

## Built-in Tools

The Responses API supports tools that the model can invoke automatically within a single API call.

### Web Search

```python
response = client.responses.create(
    model="gpt-4o",
    input="What's the latest news about AI?",
    tools=[{"type": "web_search_preview"}]
)
```

### File Search (RAG)

```python
response = client.responses.create(
    model="gpt-4o",
    input="What does the document say about Q3 revenue?",
    tools=[{
        "type": "file_search",
        "vector_store_ids": ["vs_abc123"]
    }]
)
```

### Code Interpreter

```python
response = client.responses.create(
    model="gpt-4o",
    input="Calculate the compound interest for $10,000 at 5% for 10 years.",
    tools=[{"type": "code_interpreter"}]
)
```

### Computer Use

```python
response = client.responses.create(
    model="computer-use-preview",  # specialized model
    input="Open a browser and search for OpenAI",
    tools=[{
        "type": "computer_use_preview",
        "display_width": 1280,
        "display_height": 800,
        "environment": "browser"
    }]
)
```

### Image Generation

```python
response = client.responses.create(
    model="gpt-4o",
    input="Create an image of a sunset over mountains.",
    tools=[{"type": "image_generation"}]
)
```

### Remote MCP Servers

```python
response = client.responses.create(
    model="gpt-4o",
    input="Run the tests using the test framework.",
    tools=[{
        "type": "mcp",
        "server_url": "https://my-mcp-server.example.com",
        "server_label": "my-tools"
    }]
)
```

### Custom Function Tools (Same as Chat Completions)

```python
response = client.responses.create(
    model="gpt-4o",
    input="What's the weather in Tokyo?",
    tools=[{
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        },
        "strict": True
    }]
)
```

---

## Handling Tool Results

When the model calls a tool, you submit results back:

```python
import json

response = client.responses.create(
    model="gpt-4o",
    input="What's the weather in Tokyo?",
    tools=[...],
    tool_choice="auto"
)

# Check if model wants to call a tool
if response.status == "requires_action" or any(
    item.type == "function_call" for item in response.output
):
    tool_call = next(
        item for item in response.output if item.type == "function_call"
    )
    
    args = json.loads(tool_call.arguments)
    result = get_weather(args["location"])  # your function
    
    # Continue with tool result
    final_response = client.responses.create(
        model="gpt-4o",
        previous_response_id=response.id,
        input=[{
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result)
        }]
    )
    
    print(final_response.output_text)
```

---

## Streaming

```python
with client.responses.stream(
    model="gpt-4o",
    input="Tell me a long story."
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    
    final_response = stream.get_final_response()
```

### Streaming Event Types

| Event | Description |
|-------|-------------|
| `response.created` | Response object created |
| `response.output_item.added` | New output item started |
| `response.output_text.delta` | Text token streamed |
| `response.output_text.done` | Text output complete |
| `response.function_call_arguments.delta` | Tool call arguments streaming |
| `response.function_call_arguments.done` | Tool call complete |
| `response.completed` | Response fully complete |
| `response.failed` | Response failed |

---

## Reasoning Models (o-series)

For o-series models, use the `reasoning` parameter instead of `temperature`:

```python
response = client.responses.create(
    model="o3",
    input="Solve this complex math proof...",
    reasoning={"effort": "high"}  # "low", "medium", "high"
)

# Access reasoning summary (if available)
for item in response.output:
    if item.type == "reasoning":
        print("Reasoning:", item.summary)
    elif item.type == "message":
        print("Answer:", item.content[0].text)
```

---

## Response Object

```json
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1720000000,
  "model": "gpt-4o-2024-11-20",
  "status": "completed",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The answer is..."
        }
      ]
    }
  ],
  "output_text": "The answer is...",
  "usage": {
    "input_tokens": 15,
    "output_tokens": 42,
    "total_tokens": 57,
    "input_tokens_details": {
      "cached_tokens": 0
    }
  }
}
```

---

## Responses API vs Chat Completions

| Feature | Responses API | Chat Completions |
|---------|--------------|-----------------|
| Stateful conversations | ✅ Built-in via previous_response_id | ❌ Manual history |
| Built-in web search | ✅ | ❌ |
| Built-in code interpreter | ✅ | ❌ |
| Built-in file search | ✅ | ❌ |
| Computer use | ✅ | ❌ |
| Cache performance | Better (40-80% improvement) | Standard |
| Custom function tools | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Vision | ✅ | ✅ |
| Maturity | Newer API | More established |

---

## Migration from Chat Completions

```python
# Chat Completions (old)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)

# Responses API (new)
response = client.responses.create(
    model="gpt-4o",
    instructions="You are helpful.",  # replaces system message
    input="Hello!"                     # replaces user message
)
print(response.output_text)
```

---

## Sources
- [Responses Overview | OpenAI API Reference](https://developers.openai.com/api/reference/responses/overview)
- [Conversation state | OpenAI API](https://developers.openai.com/api/docs/guides/conversation-state)
- [Migrate to the Responses API | OpenAI API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [OpenAI Responses API explained | eesel AI](https://www.eesel.ai/blog/openai-responses-api-reference)
