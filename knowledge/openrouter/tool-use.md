# OpenRouter Tool Use / Function Calling
> Source: https://openrouter.ai/docs/tool-calling
> Fetched: 2026-06-20
---

## Overview

OpenRouter supports tool use / function calling in OpenAI format. Works with any model that supports tools.

## Tool Definition Format

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a location. Call this when the user asks about weather.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name, e.g., 'San Francisco, CA'"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "Temperature unit"
            }
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

## Tool Choice

| Value | Behavior |
|---|---|
| `"auto"` (default) | Model decides when to use tools |
| `"none"` | Never use tools |
| `"required"` | Must call at least one tool |
| `{"type": "function", "function": {"name": "..."}}` | Must call this specific tool |

## Complete Python Example

```python
from openai import OpenAI
import json

client = OpenAI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
)

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
            },
            "required": ["location"]
        }
    }
}]

def get_weather(location: str) -> str:
    # In production, call a real weather API
    return f"72°F and sunny in {location}"

messages = [{"role": "user", "content": "What's the weather in Paris?"}]

# First call — model may call a tool
response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",
    messages=messages,
    tools=tools,
)

# Loop until end_turn
while response.choices[0].finish_reason == "tool_calls":
    assistant_message = response.choices[0].message
    messages.append(assistant_message)
    
    # Execute all tool calls
    tool_messages = []
    for tool_call in assistant_message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)
        
        tool_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })
    
    messages.extend(tool_messages)
    
    # Continue the conversation
    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4-6",
        messages=messages,
        tools=tools,
    )

print(response.choices[0].message.content)
```

## Tool Call Response Format

When the model calls a tool, `finish_reason` is `"tool_calls"`:

```json
{
  "id": "gen-abc123",
  "object": "chat.completion",
  "choices": [{
    "finish_reason": "tool_calls",
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_xyz789",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"Paris\"}"
        }
      }]
    }
  }]
}
```

## Tool Result Format

Return tool results as `role: "tool"` messages:

```json
{
  "role": "tool",
  "tool_call_id": "call_xyz789",
  "content": "72°F and sunny in Paris"
}
```

## Parallel Tool Calls

By default, models may call multiple tools simultaneously:

```json
{
  "choices": [{
    "message": {
      "tool_calls": [
        {"id": "call_1", "function": {"name": "get_weather", "arguments": "{\"location\":\"Paris\"}"}},
        {"id": "call_2", "function": {"name": "get_weather", "arguments": "{\"location\":\"London\"}"}}
      ]
    }
  }]
}
```

Disable parallel tool calls:
```json
{
  "parallel_tool_calls": false
}
```

## Strict Mode (Structured Tool Inputs)

For models that support it, enable strict schema validation:

```json
{
  "tools": [{
    "type": "function",
    "function": {
      "name": "create_event",
      "strict": true,
      "parameters": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "date": {"type": "string", "format": "date"}
        },
        "required": ["name", "date"],
        "additionalProperties": false
      }
    }
  }]
}
```

## Models Supporting Tool Use

| Model | Tool Support | Parallel Tools | Strict Mode |
|---|---|---|---|
| `anthropic/claude-sonnet-4-6` | Yes | Yes | No |
| `anthropic/claude-opus-4-8` | Yes | Yes | No |
| `anthropic/claude-haiku-4-5` | Yes | Yes | No |
| `openai/gpt-4o` | Yes | Yes | Yes |
| `openai/gpt-4o-mini` | Yes | Yes | Yes |
| `openai/o3-mini` | Yes | No | Yes |
| `google/gemini-2.5-pro` | Yes | Yes | No |
| `meta-llama/llama-3.3-70b-instruct` | Yes (varies by provider) | Yes | No |

Check `tools: true` in the `/api/v1/models` response to confirm tool support.

## TypeScript Example

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: "sk-or-v1-...",
  baseURL: "https://openrouter.ai/api/v1",
});

const tools: OpenAI.ChatCompletionTool[] = [{
  type: "function",
  function: {
    name: "get_weather",
    description: "Get current weather",
    parameters: {
      type: "object",
      properties: {
        location: { type: "string" }
      },
      required: ["location"]
    }
  }
}];

const messages: OpenAI.ChatCompletionMessageParam[] = [
  { role: "user", content: "What's the weather in Tokyo?" }
];

let response = await client.chat.completions.create({
  model: "anthropic/claude-sonnet-4-6",
  messages,
  tools,
});

while (response.choices[0].finish_reason === "tool_calls") {
  const assistantMsg = response.choices[0].message;
  messages.push(assistantMsg);

  const toolResults: OpenAI.ChatCompletionToolMessageParam[] = 
    assistantMsg.tool_calls!.map(call => ({
      role: "tool" as const,
      tool_call_id: call.id,
      content: `72°F in ${JSON.parse(call.function.arguments).location}`,
    }));

  messages.push(...toolResults);

  response = await client.chat.completions.create({
    model: "anthropic/claude-sonnet-4-6",
    messages,
    tools,
  });
}

console.log(response.choices[0].message.content);
```
