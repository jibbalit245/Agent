# Mistral AI Function Calling

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/capabilities/function_calling/ — content below is from model training data (knowledge cutoff August 2025).

## Overview

Mistral models support function calling (tool use), allowing models to request execution of external functions and receive their results. Compatible with the OpenAI tool-calling format.

**Supported models:** `mistral-large-latest`, `mistral-small-latest`, `open-mistral-nemo`, `open-mixtral-8x22b`

---

## Basic Function Calling

### Step 1: Define Tools

```python
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
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### Step 2: First API Call

```python
from mistralai import Mistral
import json

client = Mistral(api_key="your_api_key")

messages = [
    {"role": "user", "content": "What's the weather like in Paris?"}
]

response = client.chat.complete(
    model="mistral-large-latest",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

message = response.choices[0].message
print(f"Finish reason: {response.choices[0].finish_reason}")  # "tool_calls"
```

### Step 3: Process Tool Call

```python
if response.choices[0].finish_reason == "tool_calls":
    tool_calls = message.tool_calls
    
    # Add assistant message to history
    messages.append(message)
    
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"Calling: {function_name}({function_args})")
        
        # Execute the function
        if function_name == "get_current_weather":
            result = {
                "location": function_args["location"],
                "temperature": 18,
                "unit": function_args.get("unit", "celsius"),
                "condition": "partly cloudy",
            }
        
        # Add tool result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result),
        })
```

### Step 4: Get Final Response

```python
final_response = client.chat.complete(
    model="mistral-large-latest",
    messages=messages,
    tools=tools,
)

print(final_response.choices[0].message.content)
# "The weather in Paris is currently 18°C and partly cloudy."
```

---

## Complete Working Example

```python
from mistralai import Mistral
import json

client = Mistral(api_key="your_api_key")

# Define available functions
def get_current_weather(location: str, unit: str = "celsius") -> dict:
    # Real implementation would call a weather API
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 65,
    }

def search_database(query: str, limit: int = 5) -> dict:
    return {
        "query": query,
        "results": [f"Result {i}: {query} related content" for i in range(limit)],
        "total": limit,
    }

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search the database for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5}
                },
                "required": ["query"]
            }
        }
    }
]

# Function registry
available_functions = {
    "get_current_weather": get_current_weather,
    "search_database": search_database,
}

def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        
        if finish_reason == "stop":
            return message.content
        
        if finish_reason == "tool_calls":
            messages.append(message)
            
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                fn = available_functions.get(fn_name)
                result = fn(**fn_args) if fn else {"error": f"Unknown: {fn_name}"}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(result),
                })
        else:
            return message.content or ""

# Test it
print(run_agent("What's the weather in London and Paris?"))
```

---

## Tool Choice Options

```python
# Let model decide (default)
tool_choice="auto"

# Disable all tools
tool_choice="none"

# Force model to always use a tool
tool_choice="any"  # Mistral-specific: forces tool use

# Force a specific tool
tool_choice={
    "type": "function",
    "function": {"name": "get_current_weather"}
}
```

**Note:** Mistral uses `"any"` instead of `"required"` to force tool use (OpenAI uses `"required"`).

---

## Parallel Tool Calls

Mistral supports calling multiple tools in a single response:

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[{
        "role": "user",
        "content": "What's the weather in London and what's the stock price of AAPL?"
    }],
    tools=tools,
)

# message.tool_calls may contain multiple tool calls
for tc in response.choices[0].message.tool_calls:
    print(f"Tool: {tc.function.name}, Args: {tc.function.arguments}")
```

---

## Streaming with Tool Calls

```python
with client.chat.stream(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
) as stream:
    for event in stream:
        delta = event.data.choices[0].delta
        
        if delta.content:
            print(delta.content, end="")
        
        if delta.tool_calls:
            for tc in delta.tool_calls:
                if tc.function:
                    print(f"\nTool call: {tc.function.name}")
```

---

## JSON Schema Best Practices

```python
{
    "type": "function",
    "function": {
        "name": "create_calendar_event",
        "description": """Create a new calendar event.
        Use this when the user wants to schedule a meeting or appointment.
        Returns the created event ID.""",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Event title/name"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO 8601 format (e.g., 2024-01-15T14:00:00Z)"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO 8601 format"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee email addresses"
                },
                "description": {
                    "type": "string",
                    "description": "Optional event description"
                }
            },
            "required": ["title", "start_time", "end_time"]
        }
    }
}
```

---

## Mistral vs OpenAI Tool Format Differences

| Feature | Mistral | OpenAI |
|---|---|---|
| Tool definition format | Same | Same |
| `tool_choice="any"` | Force any tool | Use `"required"` |
| Tool result role | `"tool"` | `"tool"` |
| `name` field in tool message | Required | Optional |
| Parallel tool calls | Yes | Yes |

```python
# Mistral tool result message (name is required)
{
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": function_name,      # Required in Mistral!
    "content": json.dumps(result),
}

# OpenAI tool result message (name optional)
{
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(result),
}
```

---

## Error Handling in Tool Use

```python
def safe_call_tool(tool_call, available_functions):
    fn_name = tool_call.function.name
    
    try:
        fn_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse arguments"})
    
    fn = available_functions.get(fn_name)
    if not fn:
        return json.dumps({"error": f"Function '{fn_name}' not found"})
    
    try:
        result = fn(**fn_args)
        return json.dumps(result)
    except TypeError as e:
        return json.dumps({"error": f"Invalid arguments: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Function failed: {str(e)}"})
```
