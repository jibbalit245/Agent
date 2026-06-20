# HuggingFace Python Client (huggingface_hub)
> Source: https://huggingface.co/docs/huggingface_hub/en/guides/inference
> Fetched: 2026-06-20

## Overview

The `huggingface_hub` Python library provides the `InferenceClient` and `AsyncInferenceClient` classes for running inference against:
- The HuggingFace Inference Providers router (`router.huggingface.co/v1`)
- The legacy Serverless Inference API (`api-inference.huggingface.co`)
- Self-hosted Inference Endpoints
- Third-party OpenAI-compatible servers (TGI, vLLM, etc.)

## Installation

```bash
pip install huggingface_hub
```

## InferenceClient

The synchronous client. Designed for straightforward, blocking calls.

### Basic Initialization

```python
from huggingface_hub import InferenceClient

# Uses HF_TOKEN env var automatically if set
client = InferenceClient()

# Explicit token
client = InferenceClient(token="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# With provider selection (routes via router.huggingface.co)
client = InferenceClient(
    provider="featherless-ai",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)

# With explicit model (sets default model for all calls)
client = InferenceClient(
    model="meta-llama/Llama-3.1-8B-Instruct",
    provider="featherless-ai",
)

# Against a custom endpoint (self-hosted TGI, vLLM, etc.)
client = InferenceClient(base_url="http://localhost:8080")
```

### chat_completion

The primary method for conversational LLMs. Follows the OpenAI Chat Completions API.

```python
from huggingface_hub import InferenceClient

client = InferenceClient(provider="featherless-ai")

# Basic usage
response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
)
print(response.choices[0].message.content)

# With parameters
response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Write a haiku about coding."}],
    max_tokens=100,
    temperature=0.7,
    top_p=0.9,
    stream=False,
)

# Streaming
for chunk in client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Count from 1 to 10."}],
    stream=True,
):
    print(chunk.choices[0].delta.content, end="", flush=True)
```

### text_generation

Lower-level text completion (not chat format). Useful for base models or custom prompting.

```python
# Basic text generation
result = client.text_generation(
    prompt="The capital of France is",
    model="gpt2",
    max_new_tokens=50,
)
print(result)  # Returns a string

# With detailed output
result = client.text_generation(
    prompt="Once upon a time",
    model="gpt2",
    max_new_tokens=100,
    temperature=0.8,
    details=True,  # Returns TextGenerationOutput with token details
)
print(result.generated_text)
print(result.details.finish_reason)

# Streaming
for token in client.text_generation(
    prompt="The quick brown fox",
    model="gpt2",
    max_new_tokens=50,
    stream=True,
):
    print(token, end="", flush=True)
```

### Other Key Methods

```python
# Text classification / sentiment analysis
result = client.text_classification(
    text="I love this product!",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)
# Returns list of ClassificationOutput: [{"label": "POSITIVE", "score": 0.99}]

# Feature extraction / embeddings
embeddings = client.feature_extraction(
    text="What is machine learning?",
    model="sentence-transformers/all-MiniLM-L6-v2",
)
# Returns numpy array of shape (embedding_dim,) or (n_tokens, embedding_dim)

# Sentence similarity
scores = client.sentence_similarity(
    sentence="Machine learning is awesome",
    other_sentences=["AI is great", "I like pizza"],
    model="sentence-transformers/all-MiniLM-L6-v2",
)

# Token classification / NER
result = client.token_classification(
    text="My name is Sarah and I live in London.",
    model="dslim/bert-base-NER",
)

# Translation
result = client.translation(
    text="Hello, world!",
    model="Helsinki-NLP/opus-mt-en-fr",
)

# Summarization
result = client.summarization(
    text="Long article text here...",
    model="facebook/bart-large-cnn",
)

# Image classification
result = client.image_classification(
    image="path/to/image.jpg",  # or URL, or PIL Image, or bytes
    model="google/vit-base-patch16-224",
)

# Text to image (Stable Diffusion, FLUX, etc.)
image = client.text_to_image(
    prompt="A beautiful sunset over the ocean",
    model="black-forest-labs/FLUX.1-schnell",
)
image.save("sunset.png")  # Returns PIL Image

# Automatic speech recognition
result = client.automatic_speech_recognition(
    audio="path/to/audio.wav",
    model="openai/whisper-large-v3",
)
print(result.text)
```

## AsyncInferenceClient

Async version using `asyncio` and `httpx`. **Same API as InferenceClient** but all methods are coroutines.

```python
import asyncio
from huggingface_hub import AsyncInferenceClient

client = AsyncInferenceClient(
    provider="featherless-ai",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)

async def main():
    # Basic chat completion
    response = await client.chat_completion(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

    # Async streaming
    async for chunk in await client.chat_completion(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": "Count to 5."}],
        stream=True,
    ):
        print(chunk.choices[0].delta.content, end="", flush=True)

asyncio.run(main())
```

### Parallel Requests with AsyncInferenceClient

```python
import asyncio
from huggingface_hub import AsyncInferenceClient

client = AsyncInferenceClient(provider="featherless-ai")

async def process_batch(prompts: list[str]) -> list[str]:
    tasks = [
        client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": p}],
        )
        for p in prompts
    ]
    responses = await asyncio.gather(*tasks)
    return [r.choices[0].message.content for r in responses]

results = asyncio.run(process_batch([
    "What is Python?",
    "Explain async/await",
    "What is machine learning?",
]))
```

## Provider Selection

```python
from huggingface_hub import InferenceClient

# Specify a provider
client = InferenceClient(provider="together")

# No provider = automatic (fastest available)
client = InferenceClient()

# Available providers (pass as string to 'provider' parameter):
# "featherless-ai", "together", "cerebras", "groq", "deepinfra",
# "fireworks-ai", "nebius", "novita", "sambanova", "replicate", etc.
```

## Using with OpenAI Client (Alternative)

You can also use the standard OpenAI Python SDK pointed at the HF router:

```python
from openai import OpenAI, AsyncOpenAI

# Synchronous
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct:featherless-ai",
    messages=[{"role": "user", "content": "Hello!"}],
)

# Async
async_client = AsyncOpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
```

## Model Downloads with snapshot_download

```python
from huggingface_hub import snapshot_download, hf_hub_download

# Download a single file
path = hf_hub_download(
    repo_id="meta-llama/Llama-3.1-8B",
    filename="config.json",
    token="hf_xxxxxxxx",
)

# Download entire model
local_dir = snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B",
    token="hf_xxxxxxxx",
    local_dir="./models/llama",
)
```

## InferenceClient vs OpenAI Client Comparison

| Feature | InferenceClient | OpenAI Client (via HF router) |
|---------|-----------------|-------------------------------|
| Provider param | `provider="featherless-ai"` | `:featherless-ai` in model name |
| Model format | `model="..."` (no :provider suffix) | `model="...:provider"` |
| Auto-login | Uses HF_TOKEN automatically | Must pass as `api_key` |
| Non-chat tasks | Yes (image, audio, NLP) | Chat/completions only |
| Streaming | Yes | Yes |
| Async | AsyncInferenceClient | AsyncOpenAI |

## References

- [Run Inference on Servers Guide](https://huggingface.co/docs/huggingface_hub/en/guides/inference)
- [InferenceClient API Reference](https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client)
- [Inference Providers Chat Completion](https://huggingface.co/docs/inference-providers/en/tasks/chat-completion)
- [Text Generation Inference (TGI) Client](https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/consuming_tgi)
