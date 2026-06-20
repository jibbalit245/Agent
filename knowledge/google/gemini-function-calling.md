# Google Gemini API: Function Calling

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Function calling enables developers to describe functions and pass those descriptions to a language model in requests. The model response includes matching function names and arguments, allowing developers to use functions as tools in generative AI applications.

## Setup

```python
%pip install -qU 'google-genai>=1.0.0'
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
MODEL_ID = "gemini-2.5-flash"
```

## Basic Function Calling (Automatic)

The SDK can automatically convert Python functions to tool declarations using type hints and docstrings:

```python
def get_current_weather(location: str) -> str:
    """Returns the current weather.
    
    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'

response = client.models.generate_content(
    model=MODEL_ID,
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)

print(response.text)
```

## Supported Parameter Types

The SDK converts Python type annotations to API-compatible formats:
- `int`, `float`, `bool`, `str`
- `list['AllowedTypes']`
- `dict`

## Chat with Automatic Function Execution

```python
def add(a: float, b: float):
    """returns a + b."""
    return a + b

def subtract(a: float, b: float):
    """returns a - b."""
    return a - b

def multiply(a: float, b: float):
    """returns a * b."""
    return a * b

def divide(a: float, b: float):
    """returns a / b."""
    if b == 0:
        return "Cannot divide by zero."
    return a / b

operation_tools = [add, subtract, multiply, divide]

chat = client.chats.create(
    model=MODEL_ID,
    config={
        "tools": operation_tools,
        "automatic_function_calling": {"disable": False}
    }
)

response = chat.send_message(
    "I have 57 cats, each owns 44 mittens, how many mittens is that?"
)
print(response.text)  # Model calls multiply(57, 44) automatically
```

## Disable Automatic Function Calling

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    ),
)

# Manually access function call
function_calls = response.function_calls
print(function_calls[0].name)  # "get_current_weather"
print(function_calls[0].args)  # {"location": "Boston, MA"}
```

## Manual Function Declaration

```python
function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters_json_schema={
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The city and state, e.g. San Francisco, CA',
            }
        },
        'required': ['location'],
    },
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model=MODEL_ID,
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.function_calls[0])
```

## Processing Function Call Results Manually

```python
user_prompt_content = types.Content(
    role='user',
    parts=[types.Part.from_text(text='What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content

try:
    function_result = get_current_weather(**function_call_part.function_call.args)
    function_response = {'result': function_result}
except Exception as e:
    function_response = {'error': str(e)}

function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(
    role='tool',
    parts=[function_response_part]
)

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        user_prompt_content,
        function_call_content,
        function_response_content,
    ],
    config=types.GenerateContentConfig(tools=[tool]),
)

print(response.text)
```

## Parallel Function Calls

The Gemini API can invoke multiple independent functions in a single turn:

```python
def power_disco_ball(power: bool) -> bool:
    """Powers the spinning disco ball."""
    print(f"Disco ball is {'spinning!' if power else 'stopped.'}")
    return True

def start_music(energetic: bool, loud: bool, bpm: int) -> str:
    """Play music matching specified parameters."""
    print(f"Starting music! {energetic=} {loud=}, {bpm=}")
    return "Never gonna give you up."

def dim_lights(brightness: float) -> bool:
    """Dim the lights. 0.0 is off, 1.0 is full brightness."""
    print(f"Lights are now set to {brightness:.0%}")
    return True

house_fns = [power_disco_ball, start_music, dim_lights]

chat = client.chats.create(
    model=MODEL_ID,
    config={
        "tools": house_fns,
        "tool_config": {
            "function_calling_config": {"mode": "any"}
        }
    }
)

response = chat.send_message("Turn this place into a party!")
# Model may call all three functions in a single turn
```

## Function Calling Modes

### AUTO Mode (Default)

Model decides whether to respond with text or call functions:

```python
tool_config = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(mode="auto")
)
```

### NONE Mode

Prohibits function calls; model responds with text only:

```python
tool_config = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(mode="none")
)
```

### ANY Mode

Forces model to call at least one function:

```python
tool_config = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(mode="any")
)
```

### Restricting to Specific Functions

```python
tool_config = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(
        mode="any",
        allowed_function_names=["get_current_weather", "get_forecast"]
    )
)
```

## Key Configuration Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `mode` | Function calling behavior | `"auto"`, `"any"`, `"none"` |
| `allowed_function_names` | Restrict to specific functions | List of function names |
| `maximum_remote_calls` | Max auto-execution calls | Integer (default: 10) |
| `disable` | Disable automatic execution | Boolean |

## Limiting Automatic Function Calls

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents="Make this place PURPLE!",
    config={
        "tools": light_controls,
        "tool_config": {
            "function_calling_config": {"mode": "any"}
        },
        "automatic_function_calling": {
            "maximum_remote_calls": 1  # Allow only 1 auto call
        }
    }
)
```

**Note**: When using ANY mode with automatic execution, set `maximum_remote_calls` to x+1 to allow x calls.

## Compositional Function Calling

The model can chain function calls across multiple turns:

```python
def find_movies(description: str, location: str):
    """Find movie titles currently playing based on description."""
    return ["Barbie", "Oppenheimer"]

def find_theaters(location: str, movie: str):
    """Find theaters showing movies in a location."""
    return ["Googleplex 16", "Android Theatre"]

def get_showtimes(location: str, movie: str, theater: str, date: str):
    """Find start times for movies at specific theaters."""
    return ["10:00", "11:00"]

theater_functions = [find_movies, find_theaters, get_showtimes]

chat = client.chats.create(
    model=MODEL_ID,
    config={"tools": theater_functions}
)

response = chat.send_message("""
Find comedy movies in Mountain View, CA on 01/01/2025.
First find movie titles, then theaters, then showtimes.
""")
```

## Model Context Protocol (MCP) Support (Experimental)

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

client = genai.Client()

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@philschmid/weather-mcp"],
    env=None,
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents="What is the weather in London today?",
                config=genai.types.GenerateContentConfig(tools=[session]),
            )
            print(response.text)

asyncio.run(run())
```

## Explicit Schema Generation

```python
set_color_declaration = types.FunctionDeclaration.from_callable(
    callable=set_light_color,
    client=client
)

import json
print(json.dumps(set_color_declaration.to_json_dict(), indent=4))
```

## API Response Structure

```python
part = response.candidates[0].content.parts[0]

# FunctionCall Object
if part.function_call:
    print(part.function_call.name)  # Function name
    print(part.function_call.args)  # Dict of arguments
    print(part.function_call.id)    # Optional call identifier

# FunctionResponse Object
if part.function_response:
    print(part.function_response.name)     # Function name
    print(part.function_response.response) # Result dict
```

## Important Notes

- Docstrings and type hints are essential for automatic function schema generation
- Parameter docstrings enhance the generated schema
- The API is stateless; manually replying requires sending full conversation history
- Maximum automatic function calls defaults to 10
