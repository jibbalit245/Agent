# Anthropic Claude Tool Use Guide
> Source: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
> Fetched: 2026-06-20

## Overview

Tool use (function calling) lets Claude call functions you define. Claude decides when to call a tool based on the user's request and tool descriptions, returns a structured call, and your application executes it and returns the result.

**Flow**: User message → Claude decides to call tool → `tool_use` block in response → You execute tool → Send `tool_result` → Claude continues

## Defining Tools

Tools are passed as an array in the `tools` parameter:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a given location. Returns temperature and conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. 'San Francisco, CA'"
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
]
```

### Tool Definition Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, alphanumeric + underscores |
| `description` | Yes | When and how to use the tool — critical for accuracy |
| `input_schema` | Yes | JSON Schema object defining expected parameters |

## Making a Tool Use Request

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ]
)

print(response.stop_reason)   # "tool_use"
print(response.content)       # List of content blocks
```

## Handling a tool_use Response

When Claude wants to call a tool, `stop_reason` is `"tool_use"` and content contains a `tool_use` block:

```python
# Example response content
[
    {
        "type": "text",
        "text": "I'll check the weather for you."
    },
    {
        "type": "tool_use",
        "id": "toolu_01A09q90qw90lq917835lq9",
        "name": "get_weather",
        "input": {
            "location": "San Francisco, CA",
            "unit": "fahrenheit"
        }
    }
]
```

## Sending a tool_result

After executing the tool, send results back as a `tool_result` content block:

```python
# Execute the tool
tool_use_block = next(b for b in response.content if b.type == "tool_use")
weather_result = get_weather(tool_use_block.input["location"])

# Continue the conversation
follow_up = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in San Francisco?"},
        {"role": "assistant", "content": response.content},  # include ALL content blocks
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,  # must match
                    "content": str(weather_result)       # string or content blocks
                }
            ]
        }
    ]
)
```

## tool_choice Parameter

Controls whether and how Claude uses tools:

```python
# Auto (default) — Claude decides whether to use a tool
tool_choice={"type": "auto"}

# Any — Claude must use at least one tool
tool_choice={"type": "any"}

# Specific tool — Claude must use this exact tool
tool_choice={"type": "tool", "name": "get_weather"}

# None — Claude cannot use tools
tool_choice={"type": "none"}
```

## Parallel Tool Calls

Claude can call multiple tools in a single response. Tool calls within one assistant turn are unordered and can be run concurrently:

```python
# Response may contain multiple tool_use blocks
response_content = [
    {"type": "tool_use", "id": "toolu_001", "name": "get_weather", "input": {...}},
    {"type": "tool_use", "id": "toolu_002", "name": "get_time",    "input": {...}},
]

# Run in parallel
import asyncio

async def run_tools(tool_blocks):
    tasks = [execute_tool(b) for b in tool_blocks]
    return await asyncio.gather(*tasks)

# Or sequentially — Claude doesn't assume ordering
results = [execute_tool(b) for b in tool_blocks]

# Return ALL tool results in a single user message
tool_results = [
    {
        "type": "tool_result",
        "tool_use_id": "toolu_001",
        "content": "72°F, sunny"
    },
    {
        "type": "tool_result",
        "tool_use_id": "toolu_002",
        "content": "2:30 PM PST"
    }
]
```

### Disabling Parallel Tool Use

```python
# Force Claude to use at most one tool per turn
tool_choice={
    "type": "auto",
    "disable_parallel_tool_use": True
}
```

## Error Handling in Tool Results

```python
{
    "type": "tool_result",
    "tool_use_id": "toolu_001",
    "content": "Error: Location not found",
    "is_error": True   # optional flag to signal failure
}
```

## Complete Agentic Loop Example

```python
def run_agent(user_message, tools, max_iterations=10):
    messages = [{"role": "user", "content": user_message}]
    
    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason == "end_turn":
            # Final text response
            return next(b.text for b in response.content if b.type == "text")
        
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            
            messages.append({"role": "user", "content": tool_results})
    
    raise Exception("Max iterations reached")
```

## Server-Side Tools (Anthropic-Provided)

Anthropic provides built-in server tools that execute on Anthropic's infrastructure:

```python
# Web search tool
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search"
    }
]

# Code execution tool
tools = [
    {
        "type": "code_execution_20250825",
        "name": "code_execution"
    }
]
```

## Best Practices

- **Descriptions matter most**: Write clear, specific tool descriptions. Claude decides when to call tools based on them.
- **Input schema**: Use `required` array to indicate mandatory params. Optional params get defaults.
- **Token efficiency**: Claude 4 models have built-in token-efficient tool use — tool definitions cost fewer tokens than earlier models.
- **Tool result content**: Can be a string or an array of content blocks (text, image).
- **Always include all blocks**: When continuing after a `tool_use`, include the complete `response.content` (all blocks, not just text) as the assistant message.
