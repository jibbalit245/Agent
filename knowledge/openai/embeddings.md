# OpenAI Embeddings API
> Source: https://platform.openai.com/docs/guides/embeddings
> Fetched: 2026-06-20

## Overview

Embeddings convert text into numerical vectors that capture semantic meaning. Similar texts produce similar vectors, enabling:
- **Semantic search** — find documents by meaning, not keywords
- **Clustering** — group similar content
- **Classification** — train classifiers on embedded features
- **Recommendation systems** — find related items
- **Anomaly detection** — detect outliers
- **RAG (Retrieval-Augmented Generation)** — find relevant context for LLM queries

---

## Endpoint

```
POST https://api.openai.com/v1/embeddings
```

---

## Models

### text-embedding-3-small (Recommended for most cases)

| Property | Value |
|----------|-------|
| Model ID | `text-embedding-3-small` |
| Dimensions | 1,536 (default); supports reduction |
| Context window | 8,191 tokens |
| Price | $0.02 / 1M tokens |
| Batch price | $0.01 / 1M tokens |
| Performance | Better than ada-002, optimized for cost |

### text-embedding-3-large (Best performance)

| Property | Value |
|----------|-------|
| Model ID | `text-embedding-3-large` |
| Dimensions | 3,072 (default); supports reduction |
| Context window | 8,191 tokens |
| Price | $0.13 / 1M tokens |
| Batch price | $0.065 / 1M tokens |
| Performance | Best for English and multilingual tasks |

### text-embedding-ada-002 (Legacy)

| Property | Value |
|----------|-------|
| Model ID | `text-embedding-ada-002` |
| Dimensions | 1,536 (fixed, no reduction) |
| Context window | 8,191 tokens |
| Price | $0.10 / 1M tokens |
| Note | Prefer text-embedding-3-small (cheaper, better) |

---

## Basic Usage

```python
from openai import OpenAI

client = OpenAI()

# Embed a single string
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Dimensions: {len(embedding)}")  # 1536
print(f"First 5 values: {embedding[:5]}")
```

---

## Parameters

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID |
| `input` | string or array | Yes | Text(s) to embed. Single string or list of strings/tokens |
| `dimensions` | int | No | Reduce output dimensions (Matryoshka embeddings) |
| `encoding_format` | string | No | `"float"` (default) or `"base64"` |
| `user` | string | No | End-user ID for monitoring |

### Notes on `input`

- Can be a single string, a list of strings, or a list of token arrays
- Maximum 2048 inputs per request
- Max 8,191 tokens per individual input
- Empty strings are not allowed
- Pricing is based on input tokens only (no output tokens for embeddings)

---

## Batch Embedding (Multiple texts)

```python
texts = [
    "Paris is the capital of France",
    "Python is a programming language",
    "The mitochondria is the powerhouse of the cell",
    "Machine learning transforms industries"
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

# Access embeddings
for i, embedding_obj in enumerate(response.data):
    print(f"Text {i}: {len(embedding_obj.embedding)} dimensions")

# Get all embeddings as a list
embeddings = [e.embedding for e in response.data]
```

---

## Dimension Reduction (Matryoshka Embeddings)

The text-embedding-3 models support the `dimensions` parameter to reduce vector size without separate model retraining. Shorter vectors are faster and cheaper to store/compare.

```python
# Full 1536-dim embedding (default)
full = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world"
)
print(len(full.data[0].embedding))  # 1536

# Reduced to 256 dimensions
small = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world",
    dimensions=256
)
print(len(small.data[0].embedding))  # 256
```

Supported reduced dimensions for `text-embedding-3-small`: 512, 256, 64
Supported reduced dimensions for `text-embedding-3-large`: 3072, 1536, 1024, 512, 256

---

## Response Format

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.0023064255, -0.009327292, ...]
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

---

## Semantic Search Example

```python
import numpy as np
from openai import OpenAI

client = OpenAI()

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Index documents
documents = [
    "Python is a high-level programming language",
    "Machine learning uses statistical methods",
    "The Eiffel Tower is in Paris, France",
    "Deep learning is a subset of machine learning"
]

# Embed all documents
doc_embeddings_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents
)
doc_embeddings = [e.embedding for e in doc_embeddings_response.data]

# Search
query = "AI and neural networks"
query_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)
query_embedding = query_response.data[0].embedding

# Rank by similarity
similarities = [
    (cosine_similarity(query_embedding, doc_emb), doc)
    for doc_emb, doc in zip(doc_embeddings, documents)
]
similarities.sort(reverse=True)

print("Results for:", query)
for score, doc in similarities:
    print(f"  {score:.3f}: {doc}")
```

---

## RAG (Retrieval-Augmented Generation) Pattern

```python
import json
from openai import OpenAI

client = OpenAI()

# 1. Index your knowledge base
def index_documents(docs: list[str]) -> list[dict]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=docs
    )
    return [
        {"text": doc, "embedding": resp.embedding}
        for doc, resp in zip(docs, response.data)
    ]

# 2. Find relevant docs for a query
def retrieve(query: str, index: list[dict], top_k: int = 3) -> list[str]:
    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    
    scores = []
    for item in index:
        score = np.dot(query_emb, item["embedding"])
        scores.append((score, item["text"]))
    
    scores.sort(reverse=True)
    return [text for _, text in scores[:top_k]]

# 3. Generate answer with context
def answer_with_rag(question: str, index: list[dict]) -> str:
    context_docs = retrieve(question, index)
    context = "\n\n".join(context_docs)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Answer based on this context:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content
```

---

## Using with Vector Databases

Common vector databases that work with OpenAI embeddings:

| Database | Notes |
|----------|-------|
| **Pinecone** | Managed cloud vector DB, easy setup |
| **Weaviate** | Open-source, supports hybrid search |
| **Qdrant** | Open-source, Rust-based, high performance |
| **Chroma** | Lightweight, good for prototyping |
| **pgvector** | PostgreSQL extension, SQL-compatible |
| **FAISS** | Facebook's library, CPU/GPU, in-memory |
| **Milvus** | Open-source, production-scale |
| **OpenAI Vector Stores** | Native via Assistants/Responses API |

---

## Handling Long Texts

The 8,191 token limit means very long documents must be chunked:

```python
import tiktoken

def chunk_text(text: str, max_tokens: int = 8000, model: str = "text-embedding-3-small") -> list[str]:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(enc.decode(chunk_tokens))
    
    return chunks

def embed_long_document(text: str) -> list[list[float]]:
    chunks = chunk_text(text)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    return [e.embedding for e in response.data]
```

---

## Best Practices

1. **Normalize embeddings**: Normalize vectors to unit length before computing cosine similarity (or use numpy's dot product directly after normalizing)
2. **Cache embeddings**: Embeddings are deterministic — cache them to avoid re-computing
3. **Chunk appropriately**: 256–512 tokens per chunk often works well for RAG
4. **Match query and document embedding**: Use the same model for indexing and querying
5. **Batch requests**: Batch up to 2048 inputs per API call to reduce overhead
6. **Reduce dimensions when possible**: For large-scale retrieval, 256-512 dimensions often performs nearly as well as 1536

---

## Sources
- [Embeddings | OpenAI API](https://platform.openai.com/docs/guides/embeddings)
- [text-embedding-3-large Model | OpenAI API](https://developers.openai.com/api/docs/models/text-embedding-3-large)
- [New embedding models and API updates | OpenAI](https://openai.com/index/new-embedding-models-and-api-updates/)
