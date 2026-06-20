# OpenAI Function Calling (Tool Use)
> Source: https://platform.openai.com/docs/guides/function-calling
> Fetched: 2026-06-20

## Overview

Function calling (also called "tool use") allows models to call functions you define. The model:
1. Decides when to call a tool based on the conversation
2. Returns the function name and arguments as structured JSON
3. Receives the function result and generates a final response

**Use cases**: Fetching real-time data, taking actions, returning structured data, integrating with external APIs.

---

## Basic Structure

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "function_name",
            "description": "What this function does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "What this parameter is"
                    }
                },
                "required": ["param1"],
                "additionalProperties": False  # required for strict mode
            },
            "strict": True  # enforce exact schema adherence
        }
    }
]
```

---

## Complete Example

### Step 1: Define Tools

```python
from openai import OpenAI
import json

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city. Call this when the user asks about weather.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name and country code, e.g. 'San Francisco, US'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]
```

### Step 2: Call API with Tools

```python
messages = [{"role": "user", "content": "What's the weather like in Tokyo and London today?"}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"  # model decides when to call tools
)

message = response.choices[0].message
print(f"Finish reason: {response.choices[0].finish_reason}")
# "tool_calls" means the model wants to call functions
```

### Step 3: Execute Functions and Return Results

```python
import json

def get_weather(location, unit="celsius"):
    # Your real implementation here
    return {"temperature": 22, "condition": "sunny", "unit": unit}

def search_web(query):
    return {"results": [{"title": "Example", "snippet": "..."}]}

# Add assistant message with tool calls
messages.append(message)

# Handle tool calls
if message.tool_calls:
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute the function
        if function_name == "get_weather":
            result = get_weather(**arguments)
        elif function_name == "search_web":
            result = search_web(**arguments)
        else:
            result = {"error": "Unknown function"}
        
        # Add tool result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

# Get final response
final_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools
)

print(final_response.choices[0].message.content)
```

---

## tool_choice Options

| Value | Behavior |
|-------|---------|
| `"auto"` | Model decides whether to call tools (default) |
| `"none"` | Model never calls tools |
| `"required"` | Model must call at least one tool |
| `{"type": "function", "function": {"name": "get_weather"}}` | Force specific tool |

```python
# Force a specific tool
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)
```

---

## Parallel Function Calling

Models can call multiple functions in a single response:

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Compare weather in Tokyo, London, and New York"}],
    tools=tools
)

message = response.choices[0].message
# message.tool_calls may contain multiple calls:
# - get_weather(Tokyo)
# - get_weather(London)
# - get_weather(New York)

if message.tool_calls:
    results = []
    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)
        results.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
    
    messages.append(message)
    messages.extend(results)
    
    # Final response synthesizes all results
    final = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )
    print(final.choices[0].message.content)
```

---

## Strict Mode

`"strict": True` guarantees the model's arguments exactly match your schema.

### Strict Mode Requirements

1. `additionalProperties` must be `False` for all objects
2. All properties must be in `required`
3. Optional fields are represented as nullable types:

```python
# Without strict: optional "unit" can be omitted
# With strict: make optional fields nullable
"parameters": {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "City name"
        },
        "unit": {
            "type": ["string", "null"],  # nullable = optional
            "enum": ["celsius", "fahrenheit", None],
            "description": "Temperature unit (null for default)"
        }
    },
    "required": ["location", "unit"],  # all properties must be required
    "additionalProperties": False       # must be False in strict mode
}
```

**When to use strict mode**: Always for production use. Ensures reliable argument structure.

---

## JSON Schema Types for Parameters

### Basic Types

```python
# String
{"type": "string", "description": "A text value"}

# Number
{"type": "number", "description": "A numeric value"}
{"type": "integer", "description": "A whole number"}

# Boolean
{"type": "boolean", "description": "True or false"}

# Null (for optional fields in strict mode)
{"type": ["string", "null"]}

# Enum (restricted values)
{"type": "string", "enum": ["option1", "option2", "option3"]}
```

### Arrays

```python
{
    "type": "array",
    "items": {"type": "string"},
    "description": "List of city names"
}

# Array with min/max
{
    "type": "array",
    "items": {"type": "number"},
    "minItems": 1,
    "maxItems": 10
}
```

### Nested Objects

```python
{
    "type": "object",
    "properties": {
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "zip": {"type": "string"}
            },
            "required": ["street", "city", "zip"],
            "additionalProperties": False
        }
    },
    "required": ["address"],
    "additionalProperties": False
}
```

---

## Structured Data Extraction

Use function calling to extract structured data from unstructured text:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_contact_info",
            "description": "Extract contact information from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": ["string", "null"], "description": "Full name"},
                    "email": {"type": ["string", "null"], "description": "Email address"},
                    "phone": {"type": ["string", "null"], "description": "Phone number"},
                    "company": {"type": ["string", "null"], "description": "Company name"}
                },
                "required": ["name", "email", "phone", "company"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Hi, I'm John Smith from Acme Corp. Call me at 555-1234 or john@acme.com"
    }],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "extract_contact_info"}}
)

contact = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
print(contact)
# {"name": "John Smith", "email": "john@acme.com", "phone": "555-1234", "company": "Acme Corp"}
```

---

## vs. Structured Outputs

| Feature | Function Calling | Structured Outputs |
|---------|-----------------|-------------------|
| Mechanism | Tool definition | `response_format` with JSON schema |
| Use case | Actions + data extraction | Pure data extraction |
| Strict schema | Optional (`strict: True`) | Default strict |
| Multi-step | Yes (tools + results) | No |
| In output | `tool_calls` field | `message.content` or `message.parsed` |
| Best for | When model needs to decide to call | When you always want structured output |

### Structured Output (Alternative Approach)

```python
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str | None
    email: str | None
    phone: str | None
    company: str | None

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract: John Smith, john@acme.com, 555-1234"}],
    response_format=ContactInfo
)

contact = response.choices[0].message.parsed
print(contact.name, contact.email)
```

---

## Streaming with Tool Calls

```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    stream=True
)

tool_calls = []
for chunk in stream:
    delta = chunk.choices[0].delta
    
    if delta.tool_calls:
        for tc_chunk in delta.tool_calls:
            # Accumulate tool call chunks
            if len(tool_calls) <= tc_chunk.index:
                tool_calls.append({"id": "", "name": "", "arguments": ""})
            
            if tc_chunk.id:
                tool_calls[tc_chunk.index]["id"] = tc_chunk.id
            if tc_chunk.function.name:
                tool_calls[tc_chunk.index]["name"] = tc_chunk.function.name
            if tc_chunk.function.arguments:
                tool_calls[tc_chunk.index]["arguments"] += tc_chunk.function.arguments

# Process accumulated tool calls
for tc in tool_calls:
    args = json.loads(tc["arguments"])
    print(f"Call: {tc['name']}({args})")
```

---

## Best Practices

1. **Write clear descriptions**: The model decides when to call tools based on your description
2. **Use strict mode in production**: Prevents schema violations
3. **Handle all finish_reasons**: Check for `"tool_calls"` to know when to handle tool use
4. **Parallel calls**: Always handle multiple `tool_calls` in a single response
5. **Error handling**: Return error info in tool result if function fails
6. **Unique tool_call_id**: Each tool result must reference the correct `tool_call_id`
7. **Limit tools**: Having too many tools (>10-20) degrades model decision-making

---

## Sources
- [Function calling | OpenAI API](https://developers.openai.com/api/docs/guides/function-calling)
- [Function Calling in the OpenAI API | OpenAI Help Center](https://help.openai.com/en/articles/8555517-function-calling-in-the-openai-api)
- [Introducing Structured Outputs | OpenAI](https://openai.com/index/introducing-structured-outputs-in-the-api/)
