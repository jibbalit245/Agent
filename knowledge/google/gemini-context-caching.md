# Google Gemini API: Context Caching

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Context caching allows you to cache frequently used prompt prefixes to reduce token costs when asking multiple questions about the same large context. Cached tokens cost significantly less than standard tokens.

## Key Concepts

- **Cache Reusability**: Same cached content applies across multiple queries without reprocessing
- **Model Specificity**: Caches are tied to a specific model (different tokenization between models)
- **TTL Management**: Configure time-to-live to balance cost and accessibility
- **Cost Savings**: Cached tokens are charged at a ~90% discount rate

## Setup

```python
%pip install -q -U "google-genai>=1.0.0"
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
```

## Supported Models

- `gemini-2.5-flash`
- `gemini-2.5-pro`
- `gemini-2.5-flash-lite`

## Creating a Cache

### Step 1: Upload a File

```python
# Download and upload a large document
import subprocess
subprocess.run(["wget", "-q", "https://storage.googleapis.com/generativeai-downloads/data/a11.txt"])

document = client.files.upload(file="a11.txt")
```

### Step 2: Create CachedContent

```python
apollo_cache = client.caches.create(
    model='gemini-2.5-flash',
    config={
        'contents': [document],
        'system_instruction': 'You are an expert at analyzing transcripts.',
        'ttl': '3600s',  # Default: 1 hour
        'display_name': 'Apollo 11 Transcript Cache',
    },
)

print(apollo_cache.name)  # caches/abc123
```

### Alternative: Using Python SDK types

```python
from google.genai import types

cached_content = client.caches.create(
    model='gemini-2.5-flash',
    config=types.CreateCachedContentConfig(
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_uri(
                        file_uri=file1.uri,
                        mime_type='application/pdf'
                    ),
                    types.Part.from_uri(
                        file_uri=file2.uri,
                        mime_type='application/pdf',
                    ),
                ],
            )
        ],
        system_instruction='What is the sum of the two pdfs?',
        display_name='test cache',
        ttl='3600s',
    ),
)
```

## Using a Cache for Content Generation

### Single Request

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Find a lighthearted moment from this transcript',
    config=types.GenerateContentConfig(
        cached_content=apollo_cache.name,
    )
)

print(response.text)
```

### Chat Interface

```python
chat = client.chats.create(
    model='gemini-2.5-flash',
    config={"cached_content": apollo_cache.name}
)

response = chat.send_message(message="What was the first thing said after landing?")
print(response.text)

response = chat.send_message(message="Who said it?")
print(response.text)
```

## Cache Management

### Get Cache Info

```python
cache_info = client.caches.get(name=apollo_cache.name)
print(cache_info.name)
print(cache_info.model)
print(cache_info.expire_time)
print(cache_info.usage_metadata.total_token_count)
```

### List Caches

```python
for cache in client.caches.list():
    print(cache.name, cache.display_name, cache.expire_time)
```

### Update Cache TTL

```python
client.caches.update(
    name=apollo_cache.name,
    config=types.UpdateCachedContentConfig(ttl="7200s")  # 2 hours
)
```

### Delete Cache

```python
client.caches.delete(name=apollo_cache.name)
```

## Token Usage Breakdown

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Summarize the document',
    config=types.GenerateContentConfig(
        cached_content=apollo_cache.name,
    )
)

print(response.usage_metadata)
```

Output fields:
- **`cached_content_token_count`**: Tokens served from cache (e.g., 322,698)
- **`prompt_token_count`**: Total input tokens (includes cache + new prompt)
- **`candidates_token_count`**: Output tokens generated
- **`thoughts_token_count`**: Internal reasoning tokens (thinking models)
- **`total_token_count`**: All tokens excluding cached content

### Example Token Breakdown

| Metric | Count |
|--------|-------|
| Cached tokens | 322,698 |
| New prompt tokens | 97 |
| Thinking tokens | 902 |
| Output tokens | 239 |
| **Total** | **323,936** |

## Pricing Benefits

Cached tokens cost significantly less than standard tokens. Only new prompt tokens consume standard quota; cached content is charged at a reduced rate (~90% discount). See https://ai.google.dev/pricing for current rates.

## Important Notes

- Default expiration: 1 hour (with recurring storage costs)
- Cannot transfer caches between different models
- Cache creation requires a minimum token count (typically 32k+ tokens for cost efficiency)
- Cache names are unique per project
