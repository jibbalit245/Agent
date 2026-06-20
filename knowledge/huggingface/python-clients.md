# HuggingFace Python Clients: InferenceClient and AsyncInferenceClient
> Sources: https://github.com/huggingface/huggingface_hub/blob/main/docs/source/en/guides/inference.md, https://huggingface.co/docs/huggingface_hub/package_reference/inference_client, https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/consuming_tgi, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

The `huggingface_hub` Python library provides two main clients for running inference:

- **`InferenceClient`** — synchronous, blocking calls
- **`AsyncInferenceClient`** — async version using `asyncio` + `aiohttp`

Both support:
- HuggingFace Inference Providers router (`router.huggingface.co/v1`)
- Legacy Serverless Inference API (`api-inference.huggingface.co`)
- Self-hosted TGI, vLLM, or any OpenAI-compatible server
- HuggingFace Inference Endpoints

```bash
pip install huggingface_hub
```

---

## InferenceClient

### Initialization Options

```python
from huggingface_hub import InferenceClient
import os

# Uses HF_TOKEN environment variable automatically
client = InferenceClient()

# Explicit token
client = InferenceClient(token="hf_xxxxxxxxxxxxxxxx")
# Also accepted as:
client = InferenceClient(api_key="hf_xxxxxxxxxxxxxxxx")

# With provider (routes through router.huggingface.co)
client = InferenceClient(
    provider="featherless-ai",
    api_key=os.environ["HF_TOKEN"],
)

# With default model (used if model not specified per-call)
client = InferenceClient(
    model="meta-llama/Llama-3.1-8B-Instruct",
    provider="featherless-ai",
)

# Against a specific Inference Endpoint
client = InferenceClient(
    model="https://your-endpoint.us-east-1.aws.endpoints.huggingface.cloud",
    token="hf_xxxxxxxxxxxxxxxx",
)

# Against a local/self-hosted server (TGI, vLLM)
client = InferenceClient(base_url="http://localhost:8080")

# With timeout (default is None = wait indefinitely)
client = InferenceClient(timeout=30)  # 30 seconds

# Bill to an organization
client = InferenceClient(
    provider="featherless-ai",
    api_key=os.environ["HF_TOKEN"],
    bill_to="my-org",  # Or use headers: {"X-HF-Bill-To": "my-org"}
)
```

---

## chat_completion

Primary method for conversational LLMs. Follows OpenAI Chat Completions spec.

```python
# Basic call
response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)
print(response.choices[0].message.content)
print(response.usage.total_tokens)

# With parameters
response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Write a haiku"}],
    max_tokens=100,
    temperature=0.7,       # 0.0–2.0 (higher = more random)
    top_p=0.9,             # Nucleus sampling
    top_k=50,              # Top-k sampling
    repetition_penalty=1.1,
    seed=42,               # For reproducibility
)

# Streaming
for chunk in client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Count to 10"}],
    stream=True,
    max_tokens=200,
):
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

# With stop sequences
response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "List 3 fruits"}],
    stop=["4.", "four"],
    max_tokens=100,
)

# Function/tool calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City and country"}
                },
                "required": ["location"],
            },
        }
    }
]

response = client.chat_completion(
    model="Qwen/Qwen2.5-72B-Instruct",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto",
)
tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.function.name)      # "get_weather"
print(tool_call.function.arguments) # '{"location": "Paris, France"}'

# Structured output (JSON schema)
json_schema = {
    "name": "person",
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    },
    "strict": True,
}

response = client.chat_completion(
    model="Qwen/Qwen3-32B",
    messages=[{"role": "user", "content": "Create a fictional person profile"}],
    response_format={"type": "json_schema", "json_schema": json_schema},
)
```

### OpenAI-compatible syntax (alternative)

```python
# InferenceClient also supports openai-style .chat.completions.create()
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100,
)
```

---

## text_generation

Lower-level text completion. Returns plain string (not chat format).

```python
# Basic
result = client.text_generation(
    prompt="The capital of France is",
    model="gpt2",
    max_new_tokens=50,
)
print(result)  # Plain string

# With details
result = client.text_generation(
    prompt="Once upon a time",
    model="gpt2",
    max_new_tokens=100,
    temperature=0.8,
    details=True,  # Returns TextGenerationOutput object
)
print(result.generated_text)
print(result.details.finish_reason)   # "length" | "eos_token" | "stop_sequence"
print(result.details.tokens)          # List of token details with logprobs

# Streaming (4 modes by details + stream params)
# Stream=True, Details=False (most common)
for token in client.text_generation(
    prompt="The quick brown fox",
    model="gpt2",
    max_new_tokens=50,
    stream=True,
):
    print(token, end="")  # token is a plain string

# Stream=True, Details=True
for chunk in client.text_generation(
    prompt="Hello",
    model="gpt2",
    max_new_tokens=20,
    stream=True,
    details=True,
):
    print(chunk.token.text, end="")
    if chunk.details:  # Only set on last token
        print(f"\nFinish reason: {chunk.details.finish_reason}")
```

---

## feature_extraction (Embeddings)

```python
import numpy as np

# Single text
embedding = client.feature_extraction(
    text="What is machine learning?",
    model="sentence-transformers/all-MiniLM-L6-v2",
)
print(type(embedding))  # numpy.ndarray
print(embedding.shape)  # (384,) for all-MiniLM-L6-v2

# Multiple texts (via list)
# Note: Some models support batching, some don't
embedding = client.feature_extraction(
    text=["Hello world", "Goodbye world"],
    model="sentence-transformers/all-MiniLM-L6-v2",
)
# Shape: (2, 384)

# Normalize embeddings (for cosine similarity)
embedding = embedding / np.linalg.norm(embedding, axis=-1, keepdims=True)

# Cosine similarity between two embeddings
emb1 = client.feature_extraction("cat", model="sentence-transformers/all-MiniLM-L6-v2")
emb2 = client.feature_extraction("dog", model="sentence-transformers/all-MiniLM-L6-v2")
similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
print(f"Similarity: {similarity:.3f}")
```

---

## Other Key Methods

```python
# Text classification / sentiment analysis
result = client.text_classification(
    text="I love this product!",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)
# Returns: [ClassificationOutput(label="POSITIVE", score=0.998)]
print(result[0].label, result[0].score)

# Token classification (NER)
result = client.token_classification(
    text="My name is Sarah and I live in London.",
    model="dslim/bert-base-NER",
)
for entity in result:
    print(f"{entity.word}: {entity.entity_group} ({entity.score:.3f})")

# Fill mask
result = client.fill_mask(
    text="Paris is the [MASK] of France.",
    model="bert-base-uncased",
)
for pred in result:
    print(f"{pred.token_str}: {pred.score:.3f}")

# Translation
result = client.translation(
    text="Hello, how are you?",
    model="Helsinki-NLP/opus-mt-en-fr",
)
print(result.translation_text)

# Summarization
result = client.summarization(
    text="Long article text here...",
    model="facebook/bart-large-cnn",
    parameters={"max_length": 130, "min_length": 30},
)
print(result.summary_text)

# Question answering
result = client.question_answering(
    question="What is the capital of France?",
    context="France is a country in Western Europe. Paris is the capital city.",
    model="deepset/roberta-base-squad2",
)
print(result.answer, result.score)

# Zero-shot classification
result = client.zero_shot_classification(
    text="I love programming",
    labels=["sports", "technology", "cooking"],
    model="facebook/bart-large-mnli",
)
for label, score in zip(result.labels, result.scores):
    print(f"{label}: {score:.3f}")

# Image classification
result = client.image_classification(
    image="https://example.com/dog.jpg",  # URL, local path, bytes, or PIL Image
    model="google/vit-base-patch16-224",
)
print(result[0].label, result[0].score)

# Text to image
image = client.text_to_image(
    prompt="A serene mountain lake at sunset",
    model="black-forest-labs/FLUX.1-schnell",
    guidance_scale=7.5,
    num_inference_steps=20,
)
image.save("output.png")  # Returns PIL Image

# Automatic speech recognition
result = client.automatic_speech_recognition(
    audio="path/to/audio.wav",  # local path, URL, or bytes
    model="openai/whisper-large-v3",
)
print(result.text)

# Sentence similarity
scores = client.sentence_similarity(
    sentence="Machine learning is awesome",
    other_sentences=["AI is great", "I like pizza"],
    model="sentence-transformers/all-MiniLM-L6-v2",
)
print(scores)  # [0.89, 0.12]

# Object detection
result = client.object_detection(
    image="path/to/image.jpg",
    model="facebook/detr-resnet-50",
)
for detection in result:
    print(f"{detection.label}: {detection.score:.3f} at {detection.box}")
```

---

## AsyncInferenceClient

Identical API to `InferenceClient` but all methods are coroutines (must `await`).

```python
import asyncio
from huggingface_hub import AsyncInferenceClient

client = AsyncInferenceClient(
    provider="featherless-ai",
    api_key="hf_xxxxxxxxxxxxxxxx",
)

async def main():
    # Basic chat completion
    response = await client.chat_completion(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": "Hello!"}],
        max_tokens=100,
    )
    print(response.choices[0].message.content)

    # Async streaming
    async for chunk in await client.chat_completion(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": "Count to 5"}],
        stream=True,
    ):
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)

    # Text generation
    async for token in await client.text_generation(
        prompt="The Hugging Face Hub is",
        model="gpt2",
        max_new_tokens=50,
        stream=True,
    ):
        print(token, end="")

    # Feature extraction
    embedding = await client.feature_extraction(
        text="What is machine learning?",
        model="sentence-transformers/all-MiniLM-L6-v2",
    )
    print(embedding.shape)

asyncio.run(main())
```

### Parallel Requests (the key async advantage)

```python
import asyncio
from huggingface_hub import AsyncInferenceClient

client = AsyncInferenceClient(provider="featherless-ai")

async def process_batch(prompts: list[str]) -> list[str]:
    tasks = [
        client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        for prompt in prompts
    ]
    
    # Run all requests in parallel
    responses = await asyncio.gather(*tasks)
    return [r.choices[0].message.content for r in responses]

# Process 10 prompts simultaneously
prompts = [f"Question {i}: What is AI?" for i in range(10)]
results = asyncio.run(process_batch(prompts))
```

---

## Error Handling

```python
from huggingface_hub import InferenceClient
from huggingface_hub.errors import InferenceTimeoutError
import time

client = InferenceClient(timeout=30)

# Timeout handling
try:
    result = client.text_generation("Hello", model="gpt2", max_new_tokens=100)
except InferenceTimeoutError:
    print("Request timed out after 30s")

# Rate limit retry
import httpx

def query_with_retry(client, **kwargs):
    for attempt in range(5):
        try:
            return client.chat_completion(**kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("retry-after", 60))
                print(f"Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after)
            elif e.response.status_code == 503:
                wait_time = e.response.json().get("estimated_time", 20)
                print(f"Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise RuntimeError("Max retries exceeded")
```

---

## InferenceClient vs OpenAI Client Comparison

| Feature | `InferenceClient` | OpenAI Python SDK (via HF router) |
|---------|------------------|-----------------------------------|
| Provider param | `provider="featherless-ai"` | `:featherless-ai` in model name |
| Model format | `model="meta-llama/..."` | `model="meta-llama/...:provider"` |
| Auto-uses HF_TOKEN | Yes | Must pass as `api_key` |
| Non-chat tasks | Yes (28+ tasks) | Chat/completions only |
| Streaming | Yes | Yes |
| Async version | `AsyncInferenceClient` | `AsyncOpenAI` |
| Local server | `base_url="http://localhost:8080"` | `base_url="http://localhost:8080/v1"` |

---

## Supported Providers (via `provider=` parameter)

```python
# All valid provider values (as of 2025-2026):
providers = [
    "featherless-ai",   # 6,700+ models, largest LLM catalog
    "together",         # Wide LLM support
    "cerebras",         # Fast inference, structured outputs
    "groq",             # Ultra-fast LPU inference
    "deepinfra",        # Wide model support
    "fireworks-ai",     # Fast LLM inference
    "nebius",           # Wide support, function calling
    "novita",           # General purpose
    "sambanova",        # Ultra-fast inference
    "replicate",        # LLMs + image/video
    "fal-ai",           # Image/video generation
    "hyperbolic",       # General purpose
    "cohere",           # Command models
    "black-forest-labs", # FLUX image models
    "hf-inference",     # HF's own CPU inference
    "ovhcloud",         # European cloud
    "nscale",           # General purpose
    "nvidia",           # NVIDIA NIM
    "scaleway",         # European cloud
    "wavespeed",        # Video generation
    "publicai",         # Public AI
    "clarifai",         # General purpose
    "zai-org",          # General purpose
]
```

---

## References

- [InferenceClient API Reference](https://huggingface.co/docs/huggingface_hub/package_reference/inference_client)
- [Run Inference on Servers Guide](https://huggingface.co/docs/huggingface_hub/en/guides/inference)
- [Inference Providers Documentation](https://huggingface.co/docs/inference-providers/en/index)
- [GitHub: inference.md guide](https://github.com/huggingface/huggingface_hub/blob/main/docs/source/en/guides/inference.md)
