# Google Gemini API: System Instructions

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

System instructions allow you to steer the behavior of the model by providing context separate from user prompts. This enables product-level behavior specifications without relying solely on end-user prompts.

**Important caveat**: System instructions can help guide the model but do not fully prevent jailbreaks or leaks. Exercise caution with sensitive information in system instructions.

## Setup

```python
%pip install -U -q "google-genai>=1.0.0"
```

```python
from google.colab import userdata
from google import genai
from google.genai import types

client = genai.Client(api_key=userdata.get("GOOGLE_API_KEY"))
```

## Available Models

- `gemini-2.5-flash`
- `gemini-2.5-pro`
- `gemini-2.5-flash-preview`
- `gemini-2.5-flash-lite`

## Basic Single-Turn Implementation

```python
system_prompt = "You are a cat. Your name is Neko."
prompt = "Good morning! How are you?"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)
```

## Using Dictionary Config

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What can you do?',
    config={
        'system_instruction': 'You are a helpful coding assistant specializing in Python.',
        'temperature': 0.3,
    }
)
```

## Multi-Turn Chat with System Instructions

```python
chat = client.chats.create(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        system_instruction="You are a pirate captain. Always speak like a pirate."
    )
)

response = chat.send_message("Good day fine chatbot")
print(response.text)  # Will respond in pirate speak

response = chat.send_message("How's your boat doing?")
print(response.text)  # Continues in pirate persona
```

## Code Generation Use Case

```python
system_prompt = """
You are a coding expert specializing in front end interfaces. Return 
HTML with inline CSS only. No explanations needed.
"""

prompt = "A flexbox with large rainbow text logo left, links right."

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)
```

## API Parameter Structure

| Parameter | Type | Purpose |
|-----------|------|---------|
| `model` | string | Specifies which Gemini model to use |
| `contents` | string or list | User prompt/message |
| `system_instruction` | string | Behavior guidance for the model |
| `config` | GenerateContentConfig | Configuration object containing all settings |

## GenerateContentConfig Parameters

```python
config = types.GenerateContentConfig(
    system_instruction="You are a helpful assistant.",
    temperature=0.7,
    top_p=0.95,
    top_k=20,
    max_output_tokens=1024,
    candidate_count=1,
    seed=42,
    stop_sequences=['END'],
    presence_penalty=0.0,
    frequency_penalty=0.0,
    response_mime_type='text/plain',  # or 'application/json'
    safety_settings=[...],
    tools=[...],
    tool_config=...,
    cached_content=...,
    thinking_config=...,
)
```

## Common System Instruction Patterns

### Persona Assignment
```
You are a helpful customer service agent for Acme Corp. Be friendly and concise.
```

### Output Format Control
```
You are a JSON API. Always respond with valid JSON. No explanations or markdown.
```

### Language / Style Control
```
Always respond in formal academic English. Use citations where appropriate.
```

### Domain Specialization
```
You are an expert at analyzing transcripts. Focus on key quotes and themes.
```

### Limitation Setting
```
You only answer questions about cooking. For all other topics, politely decline.
```

## Documentation

- Full documentation: https://ai.google.dev/docs/system_instructions
