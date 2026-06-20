# Google Gemini API: Long Context

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Gemini models support very large context windows, enabling analysis of extensive documents, codebases, conversation histories, and multimedia files in a single prompt.

## Context Window Sizes

| Model | Input Context | Output Tokens |
|-------|-------------|---------------|
| `gemini-2.5-flash` | 1,048,576 (1M tokens) | 65,536 |
| `gemini-2.5-pro` | 2,000,000 (2M tokens) | Variable |
| `gemini-2.5-flash-lite` | 1,048,576 (1M tokens) | Variable |

## Token Approximations

- 1 token ≈ 4 characters
- 100 tokens ≈ 60-80 English words
- 1M tokens ≈ ~750,000 words ≈ ~1,500 page document

## Multimodal Token Rates

All input types consume tokens:
- **Images**: Fixed token count per image regardless of file size
- **Video**: Fixed tokens per second of video
- **Audio**: Fixed tokens per second of audio
- **PDF**: Tokens per page (text + screenshot)

## Counting Tokens for Long Inputs

Always count tokens before making long-context requests:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')

# Count tokens for a file
file_ref = client.files.upload(file='large_document.pdf')

token_count = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents=[file_ref, 'Your question']
).total_tokens

print(f"Total tokens: {token_count}")
```

## Long Document Analysis

```python
# Upload and analyze a large document
document = client.files.upload(file='annual_report.pdf')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        document,
        'Provide a comprehensive executive summary including all key metrics, risks, and strategic initiatives.'
    ]
)

print(response.text)
```

## Multi-Document Analysis

```python
doc1 = client.files.upload(file='paper1.pdf')
doc2 = client.files.upload(file='paper2.pdf')
doc3 = client.files.upload(file='paper3.pdf')

response = client.models.generate_content(
    model='gemini-2.5-pro',  # 2M context for very large collections
    contents=[
        doc1, doc2, doc3,
        'Compare and contrast the methodologies used in these three papers.'
    ]
)
```

## Video Analysis with Long Context

```python
import time

def upload_video(path):
    video = client.files.upload(file=path)
    while video.state == "PROCESSING":
        time.sleep(10)
        video = client.files.get(name=video.name)
    if video.state == "FAILED":
        raise ValueError(video.state)
    return video

video = upload_video('long_lecture.mp4')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        video,
        'Create a structured outline with timestamps for each major topic discussed.'
    ]
)
```

## Context Caching for Efficiency

For repeated queries on the same long document, use context caching to reduce costs:

```python
from google.genai import types

# Upload the document once
document = client.files.upload(file="large_codebase.txt")

# Create a cache
cache = client.caches.create(
    model='gemini-2.5-flash',
    config={
        'contents': [document],
        'system_instruction': 'You are a code review expert.',
        'ttl': '7200s',  # 2 hours
    },
)

# Reuse the cache for multiple queries (much cheaper)
questions = [
    'What are the main architectural patterns used?',
    'List all security vulnerabilities you can identify.',
    'What functions lack proper error handling?',
    'Suggest performance improvements.',
]

for question in questions:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            cached_content=cache.name,
        )
    )
    print(f"\nQ: {question}")
    print(f"A: {response.text}")
```

## YouTube Long Videos

Process long YouTube videos directly:

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=types.Content(
        parts=[
            types.Part(text="Create a chapter-by-chapter summary with timestamps."),
            types.Part(
                file_data=types.FileData(
                    file_uri='https://www.youtube.com/watch?v=LONG_VIDEO_ID'
                )
            ),
        ]
    ),
)
```

## Usage Metadata for Long Contexts

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[large_document, 'Summarize'],
)

meta = response.usage_metadata
print(f"Prompt tokens: {meta.prompt_token_count}")
print(f"Cached tokens: {meta.cached_content_token_count}")
print(f"Output tokens: {meta.candidates_token_count}")
print(f"Thinking tokens: {meta.thoughts_token_count}")
print(f"Total: {meta.total_token_count}")
```

## Tips for Long-Context Prompting

1. **Place instructions at the end**: "Document... [long context]... Now answer: ..."
2. **Be specific about output format**: Specify tables, bullet points, timestamps
3. **Use context caching** for repeated queries on the same document
4. **Count tokens first** to avoid exceeding limits and estimate costs
5. **Use Gemini 2.5 Pro** for the largest contexts (2M tokens)
6. **Stream responses** for long outputs to improve perceived latency
