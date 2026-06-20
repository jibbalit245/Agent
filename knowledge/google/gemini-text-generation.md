# Google Gemini API: Text Generation

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

The Gemini API's `generate_content` method handles text, multimodal, and multi-turn requests through a single versatile endpoint.

## Setup

```python
%pip install -U -q 'google-genai>=1.51.0'
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
```

## Basic Text Generation

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me python code to sort a list'
)

print(response.text)
```

## Configuration Parameters

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Tell me about quantum computing',
    config=types.GenerateContentConfig(
        system_instruction='You are a physics professor.',
        temperature=0.7,         # Randomness: 0.0 (deterministic) to 1.0 (creative)
        top_p=0.95,              # Nucleus sampling threshold
        top_k=20,                # Top-k sampling
        max_output_tokens=1024,  # Max tokens in response
        candidate_count=1,       # Number of response candidates
        seed=42,                 # For reproducibility
        stop_sequences=['END'],  # Stop generation at these strings
        presence_penalty=0.0,    # Penalize tokens already present
        frequency_penalty=0.0,   # Penalize frequent tokens
    )
)
```

## Streaming Responses

### Synchronous Streaming

```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Asynchronous Streaming

```python
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Write a cute story about cats.'
):
    if chunk.text:
        print(chunk.text, end='')
```

## Asynchronous Non-Streaming

```python
response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
)
print(response.text)
```

## Response Structure

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Hello'
)

# Access text
print(response.text)

# Access candidates
print(response.candidates)

# Access usage metadata
print(response.usage_metadata.prompt_token_count)
print(response.usage_metadata.candidates_token_count)
print(response.usage_metadata.thoughts_token_count)   # For thinking models
print(response.usage_metadata.cached_content_token_count)
print(response.usage_metadata.total_token_count)

# Check finish reason
print(response.candidates[0].finish_reason)
# FinishReason.STOP = completed normally
# FinishReason.SAFETY = blocked by safety filters
# FinishReason.MAX_TOKENS = reached max output tokens
```

## Safety Ratings

```python
print(response.candidates[0].safety_ratings)
# Returns list of safety ratings for each harm category
```

Safety categories:
- `HARM_CATEGORY_SEXUALLY_EXPLICIT`
- `HARM_CATEGORY_HATE_SPEECH`
- `HARM_CATEGORY_HARASSMENT`
- `HARM_CATEGORY_DANGEROUS_CONTENT`

## Safety Settings

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]
    )
)
```

Threshold levels: `BLOCK_LOW_AND_ABOVE`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_ONLY_HIGH`, `BLOCK_NONE`

## Thinking / Reasoning Control

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Solve this complex math problem: ...',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=8192,     # Token budget for reasoning
            include_thoughts=True,    # Include thought summaries in response
        )
    )
)

# Access thoughts
for part in response.candidates[0].content.parts:
    if hasattr(part, 'thought') and part.thought:
        print("Thought:", part.text)
    else:
        print("Answer:", part.text)
```

## Multimodal Input

```python
from PIL import Image

img = Image.open('image.jpg')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[img, 'Describe this image in detail']
)
print(response.text)
```

## Token Counting

```python
response = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents='What is the highest mountain in Africa?',
)
print("Prompt tokens:", response.total_tokens)
```

## Content Types for `contents` Parameter

The SDK automatically converts various input types:

| Input | Converts To |
|-------|-------------|
| `"string"` | `[UserContent(parts=[Part.from_text(...)])]` |
| `["str1", "str2"]` | Single UserContent with multiple parts |
| `types.Content(...)` | `[types.Content(...)]` |
| `types.Part.from_uri(...)` | `[UserContent(parts=[...])]` |
| `types.Part.from_function_call(...)` | `[ModelContent(parts=[...])]` |

## Available Models for Text Generation

- `gemini-2.5-flash` — Recommended starting point
- `gemini-2.5-pro` — Most capable
- `gemini-2.5-flash-lite` — Lightweight
- `gemini-2.0-flash` — Previous generation

## Rate Limits (Free Tier)

- 15 requests per minute (gemini-flash models)
- Not available in EEA, UK, CH without billing
