# Groq Tool Use / Function Calling

> **Fetch status:** HTTP 403 Forbidden from https://console.groq.com/docs/tool-use — content below is from model training data (knowledge cutoff August 2025).

## Overview

Groq supports OpenAI-compatible function/tool calling. Models can decide when to call a tool and return structured arguments. Your application executes the function and returns results to continue the conversation.

---

## Supported Models for Tool Use

| Model | Tool Use Support |
|---|---|
| `llama-3.3-70b-versatile` | Yes |
| `llama-3.1-8b-instant` | Yes |
| `llama3-groq-70b-8192-tool-use-preview` | Optimized |
| `llama3-groq-8b-8192-tool-use-preview` | Optimized |
| `mixtral-8x7b-32768` | Yes |
| `gemma2-9b-it` | Limited |

---

## Basic Tool Use Example

### Step 1: Define Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
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
    }
]
```

### Step 2: Initial Request

```python
from groq import Groq
import json

client = Groq()

messages = [
    {"role": "user", "content": "What's the weather like in San Francisco?"}
]

response = client.chat.completions.create(
    model="llama3-groq-70b-8192-tool-use-preview",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # "auto", "none", or {"type": "function", "function": {"name": "..."}}
)

response_message = response.choices[0].message
```

### Step 3: Handle Tool Call

```python
# Check if model wants to call a tool
if response_message.tool_calls:
    # Add assistant message to conversation
    messages.append(response_message)
    
    # Process each tool call
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Execute the function
        if function_name == "get_weather":
            result = get_weather(
                location=function_args["location"],
                unit=function_args.get("unit", "fahrenheit")
            )
        
        # Add tool result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
```

### Step 4: Get Final Response

```python
final_response = client.chat.completions.create(
    model="llama3-groq-70b-8192-tool-use-preview",
    messages=messages,
    tools=tools,
)

print(final_response.choices[0].message.content)
```

---

## Complete Working Example

```python
from groq import Groq
import json

client = Groq()

# Mock function implementations
def get_weather(location: str, unit: str = "fahrenheit") -> dict:
    # In production, call a real weather API
    return {
        "location": location,
        "temperature": 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 45,
    }

def get_stock_price(symbol: str) -> dict:
    return {
        "symbol": symbol,
        "price": 150.25,
        "change": "+2.5%",
    }

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
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
            "name": "get_stock_price",
            "description": "Get current stock price for a ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock ticker, e.g. AAPL"}
                },
                "required": ["symbol"]
            }
        }
    }
]

def run_conversation(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    
    # Function dispatch table
    available_functions = {
        "get_weather": get_weather,
        "get_stock_price": get_stock_price,
    }
    
    # Agentic loop
    while True:
        response = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # If no tool calls, we're done
        if not message.tool_calls:
            return message.content
        
        # Execute each tool call
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            
            fn = available_functions.get(fn_name)
            if fn:
                result = fn(**fn_args)
            else:
                result = {"error": f"Unknown function: {fn_name}"}
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

# Test
print(run_conversation("What's the weather in Paris and the stock price of TSLA?"))
```

---

## Tool Choice Options

```python
# Let the model decide (default)
tool_choice="auto"

# Disable tools (plain text response)
tool_choice="none"

# Force a specific function
tool_choice={
    "type": "function",
    "function": {"name": "get_weather"}
}
```

---

## Parallel Tool Calls

Some models can call multiple tools simultaneously:

```python
response = client.chat.completions.create(
    model="llama3-groq-70b-8192-tool-use-preview",
    messages=[{
        "role": "user",
        "content": "Get weather for NYC and London at the same time"
    }],
    tools=tools,
    parallel_tool_calls=True,  # Enable parallel calls
)

# response.choices[0].message.tool_calls may contain multiple items
for tool_call in response.choices[0].message.tool_calls:
    print(f"Tool: {tool_call.function.name}")
    print(f"Args: {tool_call.function.arguments}")
```

---

## Tool Schema Best Practices

```python
{
    "type": "function",
    "function": {
        "name": "search_database",          # snake_case, descriptive
        "description": """Search the product database.
        Use this when the user asks about products, prices, or inventory.
        Returns a list of matching products with details.""",  # Detailed description
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query text"
                },
                "category": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "food"],
                    "description": "Product category to filter by"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10
                }
            },
            "required": ["query"]           # List all truly required fields
        }
    }
}
```

---

## Streaming with Tool Calls

```python
stream = client.chat.completions.create(
    model="llama3-groq-70b-8192-tool-use-preview",
    messages=[{"role": "user", "content": "What's the weather?"}],
    tools=tools,
    stream=True,
)

tool_calls = []
for chunk in stream:
    delta = chunk.choices[0].delta
    
    if delta.tool_calls:
        for tc in delta.tool_calls:
            # Accumulate streaming tool call chunks
            if tc.index >= len(tool_calls):
                tool_calls.append({"id": "", "name": "", "arguments": ""})
            tool_calls[tc.index]["id"] = tc.id or tool_calls[tc.index]["id"]
            if tc.function:
                tool_calls[tc.index]["name"] += tc.function.name or ""
                tool_calls[tc.index]["arguments"] += tc.function.arguments or ""
```

---

## Error Handling in Tool Use

```python
# Always validate tool arguments before execution
import json
from jsonschema import validate, ValidationError

def safe_execute_tool(tool_call, available_functions, tool_schemas):
    fn_name = tool_call.function.name
    
    try:
        fn_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON arguments from model"}
    
    if fn_name not in available_functions:
        return {"error": f"Unknown function: {fn_name}"}
    
    try:
        result = available_functions[fn_name](**fn_args)
        return result
    except Exception as e:
        return {"error": str(e)}
```
