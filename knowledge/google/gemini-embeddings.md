# Google Gemini API: Embeddings

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

The Gemini API provides state-of-the-art text and multimodal embeddings that convert content into numerical vectors representing semantic meaning. "Embeddings are numerical representations that capture the relationships between different inputs."

## Setup

```python
%pip install -q -U "google-genai>=1.73.0"
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
```

## Embedding Models

| Model | Capability | Dimensions | Use Case |
|-------|-----------|-----------|----------|
| `gemini-embedding-2` | Multimodal | 3,072 | Text, images, video, audio, PDFs |
| `gemini-embedding-001` | Text-only | Variable | Legacy text embeddings |
| `text-embedding-004` | Text-only | Variable | Text embeddings |

## Basic Text Embedding

```python
text = ["Hello world"]
result = client.models.embed_content(model='gemini-embedding-2', contents=text)
[embedding] = result.embeddings
print(f"Dimensions: {len(embedding.values)}")  # 3072
print(f"First few values: {embedding.values[:5]}")
```

## Batch Text Embedding

```python
from google.genai import types

response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['why is the sky blue?', 'What is your age?', 'Tell me a story'],
    config=types.EmbedContentConfig(output_dimensionality=512),  # Truncate dimensions
)

for i, embedding in enumerate(response.embeddings):
    print(f"Text {i}: {len(embedding.values)} dimensions")
```

## Multimodal Embeddings (gemini-embedding-2)

### Input Specifications

| Content Type | Limit |
|-------------|-------|
| Text | Up to 8,192 tokens |
| Images | Max 6 per request (PNG, JPEG) |
| PDF | Max 6 pages |
| Audio | Up to 80 seconds (MP3, WAV) |
| Video | Up to 128 seconds (MP4, MOV) |
| Overall | 8,192 tokens across all inputs |

### Image Embedding

```python
with open('image.png', 'rb') as f:
    image_bytes = f.read()

result = client.models.embed_content(
    model='gemini-embedding-2',
    contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/png',
        ),
    ]
)

print(f"Image embedding dimensions: {len(result.embeddings[0].values)}")
```

### Cross-Modal Embedding (Text + Image)

```python
# Aggregated approach - single embedding for all inputs
result = client.models.embed_content(
    model='gemini-embedding-2',
    contents=[
        "A jetpack for personal travel",
        types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
    ]
)
# Returns ONE combined embedding
print(f"Combined embedding: {len(result.embeddings[0].values)} dimensions")
```

## Aggregation Strategies

### Multiple parts (aggregated) — Single embedding

Adding multiple inputs directly to `contents` produces ONE combined embedding:

```python
result = client.models.embed_content(
    model='gemini-embedding-2',
    contents=[text_part, image_part, audio_part]
)
# result.embeddings has length 1
```

### Multiple Content objects (separate) — Multiple embeddings

Wrapping each input in a `Content` object returns INDIVIDUAL embeddings:

```python
result = client.models.embed_content(
    model='gemini-embedding-2',
    contents=[
        types.Content(parts=[text_part]),
        types.Content(parts=[image_part]),
    ]
)
# result.embeddings has length 2
```

## Task Type Optimization

Specify task type to optimize embedding quality:

```python
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['Your document text here'],
    config=types.EmbedContentConfig(
        task_type='RETRIEVAL_DOCUMENT',  # or RETRIEVAL_QUERY, SEMANTIC_SIMILARITY, etc.
        output_dimensionality=768,
    )
)
```

Task types:
- `RETRIEVAL_QUERY` — For query embeddings in search
- `RETRIEVAL_DOCUMENT` — For document embeddings in search
- `SEMANTIC_SIMILARITY` — For comparing sentence pairs
- `CLASSIFICATION` — For text classification
- `CLUSTERING` — For grouping similar texts

## Dimensionality Truncation

Reduce embedding size for storage efficiency:

```python
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['Your text'],
    config=types.EmbedContentConfig(output_dimensionality=256),  # Down from 3072
)
```

## Similarity Calculation

```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Get embeddings
result1 = client.models.embed_content(model='gemini-embedding-001', contents=['cat'])
result2 = client.models.embed_content(model='gemini-embedding-001', contents=['kitten'])
result3 = client.models.embed_content(model='gemini-embedding-001', contents=['car'])

emb1 = result1.embeddings[0].values
emb2 = result2.embeddings[0].values
emb3 = result3.embeddings[0].values

print(f"cat vs kitten: {cosine_similarity(emb1, emb2):.4f}")   # High similarity
print(f"cat vs car: {cosine_similarity(emb1, emb3):.4f}")      # Low similarity
```

## Async Embedding

```python
response = await client.aio.models.embed_content(
    model='gemini-embedding-001',
    contents='why is the sky blue?',
)
print(response)
```

## Batch Embeddings via Batch API

For large-scale embedding generation:

```python
from google.genai import types

batch_job = client.batches.create_embeddings(
    model='gemini-embedding-001',
    src=types.EmbeddingsBatchJobSource(file_name=uploaded_file.name)
)

# Monitor progress
import time
while batch_job.state.name not in ('JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED'):
    time.sleep(30)
    batch_job = client.batches.get(name=batch_job.name)
```

## Key Features

- **Unified embedding space**: Maps text, images, video, audio, and PDFs into compatible representations
- **Multilingual support**: Operates across 100+ languages
- **Default dimensionality**: 3,072 dimensions (for gemini-embedding-2)
- **Cross-modal capabilities**: Enable search, classification, and clustering across media types
- **50% Batch API discount**: Available for bulk embedding generation
