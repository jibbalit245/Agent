# Google Gemini API: Chat (Multi-Turn Conversations)

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

The Gemini API supports multi-turn conversations through chat sessions, which automatically maintain conversation history across turns.

## Setup

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
```

## Basic Chat (Synchronous, Non-Streaming)

```python
chat = client.chats.create(model='gemini-2.5-flash')

response = chat.send_message('tell me a story')
print(response.text)

response = chat.send_message('summarize the story you told me in 1 sentence')
print(response.text)
```

## Chat with System Instructions

```python
chat = client.chats.create(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        system_instruction='You are a helpful assistant who always answers in rhyme.'
    )
)

response = chat.send_message('What is the capital of France?')
print(response.text)
```

## Chat with Tools

```python
def enable_lights():
    """Turn on the lighting system."""
    print("LIGHTBOT: Lights enabled.")

def set_light_color(rgb_hex: str):
    """Set the light color. Lights must be enabled for this to work."""
    print(f"LIGHTBOT: Lights set to {rgb_hex}.")

def stop_lights():
    """Stop flashing lights."""
    print("LIGHTBOT: Lights turned off.")

light_controls = [enable_lights, set_light_color, stop_lights]

chat = client.chats.create(
    model='gemini-2.5-flash',
    config={
        "tools": light_controls,
        "system_instruction": "You control a smart lighting system.",
    }
)

response = chat.send_message("It's awful dark in here...")
print(response.text)
```

## Synchronous Streaming Chat

```python
chat = client.chats.create(model='gemini-2.5-flash')

for chunk in chat.send_message_stream('tell me a story'):
    print(chunk.text, end='')
```

## Asynchronous Non-Streaming Chat

```python
chat = client.aio.chats.create(model='gemini-2.5-flash')

response = await chat.send_message('tell me a story')
print(response.text)

response = await chat.send_message('what was the moral of the story?')
print(response.text)
```

## Asynchronous Streaming Chat

```python
chat = client.aio.chats.create(model='gemini-2.5-flash')

async for chunk in await chat.send_message_stream('tell me a story'):
    print(chunk.text, end='')
```

## Chat History

The `Chat.history` property stores conversation chronologically. Each turn contains:

- **Role**: `"user"` or `"model"`
- **Parts**: List of content components:
  - Text messages
  - `FunctionCall` objects (model requests execution)
  - `FunctionResponse` objects (execution results)

```python
chat = client.chats.create(model='gemini-2.5-flash')
chat.send_message("My name is Alice")
chat.send_message("What is my name?")

# Access history
for message in chat.history:
    print(f"Role: {message.role}")
    for part in message.parts:
        print(f"  Text: {part.text}")
```

## Manual History Construction

For stateless API usage or resuming conversations:

```python
messages = [
    types.Content(
        role="user",
        parts=[types.Part(text="What theaters in Mountain View show Barbie?")]
    ),
    types.Content(
        role="model",
        parts=[types.Part(text="I found some theaters...")]
    ),
    types.Content(
        role="user",
        parts=[types.Part(text="What are the showtimes?")]
    ),
]

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=messages,
)
```

## Chat with Context Caching

```python
chat = client.chats.create(
    model='gemini-2.5-flash',
    config={"cached_content": apollo_cache.name}
)

response = chat.send_message(message="Find a lighthearted moment from this transcript")
print(response.text)
```

## Interactions API (Stateful, Server-Side)

An alternative to client-side chat, maintaining state on the server:

```python
# First turn
interaction1 = client.interactions.create(
    model='gemini-2.5-flash',
    input='Hi, my name is Amir.'
)
print(f"Model: {interaction1.outputs[-1].text}")

# Second turn - references previous interaction
interaction2 = client.interactions.create(
    model='gemini-2.5-flash',
    input='What is my name?',
    previous_interaction_id=interaction1.id
)
print(f"Model: {interaction2.outputs[-1].text}")
```

## Response Object

```python
response = chat.send_message('Hello')

# Text content
print(response.text)

# Token usage
print(response.usage_metadata.prompt_token_count)
print(response.usage_metadata.candidates_token_count)
print(response.usage_metadata.total_token_count)

# Finish reason
print(response.candidates[0].finish_reason)
```

## Available Models

- `gemini-2.5-flash` — Recommended for most chat use cases
- `gemini-2.5-pro` — Most capable, larger context
- `gemini-2.5-flash-lite` — Lightweight / cost-efficient
