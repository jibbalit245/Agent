# Together AI Serverless Models

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/docs/serverless-models — content below is from model training data (knowledge cutoff August 2025).

## Overview

Serverless inference on Together AI allows you to run any supported model without provisioning dedicated GPU resources. You pay only for what you use, billed per token (input and output separately).

---

## How Serverless Works

- **No setup required:** Just call the API with the model ID
- **Auto-scaling:** Together AI handles load balancing
- **Cold starts:** First request may have slightly higher latency
- **Pay per token:** No idle costs
- **Rate limits:** Shared capacity across all users

---

## Serverless vs. Dedicated

| Feature | Serverless | Dedicated |
|---|---|---|
| Setup | None | Configure endpoint |
| Pricing | Per token | Per hour (GPU) |
| Latency | Variable | Consistent |
| Throughput | Shared | Reserved |
| Availability | Always on | While running |
| Cold starts | Possible | None |
| Best for | Variable load | Production/consistent load |

---

## Available Serverless Models

Most models on Together AI are available serverlessly. Key categories:

### Chat / Instruction Models (Serverless)

```
meta-llama/Llama-3.3-70B-Instruct-Turbo
meta-llama/Llama-3.3-70B-Instruct-Turbo-Free    # Free tier
meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
mistralai/Mixtral-8x7B-Instruct-v0.1
mistralai/Mixtral-8x22B-Instruct-v0.1
Qwen/Qwen2.5-72B-Instruct-Turbo
deepseek-ai/DeepSeek-R1
deepseek-ai/DeepSeek-V3
```

### Free Tier Models

Together AI offers several models with free access (with rate limits):

```
meta-llama/Llama-3.3-70B-Instruct-Turbo-Free
meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo-Free
black-forest-labs/FLUX.1-schnell-Free
```

---

## Using Serverless Models

```python
from together import Together

client = Together(api_key="your_api_key")

# Just call any model - it runs serverlessly by default
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=512,
)
```

---

## Turbo Models

Many models have a `-Turbo` suffix indicating an optimized serverless deployment:
- Uses speculative decoding or other speed optimizations
- Typically 2-4x faster than base inference
- Same model weights, optimized serving infrastructure

```python
# Turbo variants - faster, same quality
"meta-llama/Llama-3.3-70B-Instruct-Turbo"   # vs Meta-Llama-3.3-70B-Instruct
"meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
"Qwen/Qwen2.5-72B-Instruct-Turbo"
```

---

## Serverless Rate Limits

Together AI serverless rate limits vary by:
- Account tier (free vs. paid)
- Model size
- Current platform load

Typical limits for paid accounts:
- 60 RPM (requests per minute)
- 600,000 TPM (tokens per minute)

Free tier limits are lower (approximately 10 RPM).

### Handling Rate Limits

```python
import time
from together import Together
from together.error import RateLimitError

client = Together()

def complete_with_retry(messages, model, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
```

---

## Concurrent Requests

For high throughput, run multiple requests concurrently:

```python
import asyncio
from together import AsyncTogether

client = AsyncTogether()

async def batch_completions(prompts: list[str], model: str) -> list[str]:
    tasks = [
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": p}],
        )
        for p in prompts
    ]
    
    responses = await asyncio.gather(*tasks)
    return [r.choices[0].message.content for r in responses]

prompts = ["What is AI?", "What is ML?", "What is DL?"]
results = asyncio.run(batch_completions(prompts, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"))
```

---

## Model Availability Check

```python
from together import Together

client = Together()

# List all available models
models = client.models.list()
serverless_chat_models = [
    m for m in models 
    if m.type == "chat" and not m.id.startswith("custom/")
]

for model in serverless_chat_models:
    print(f"{model.id}: {model.context_length} tokens")
```

---

## Latency Optimization Tips

1. **Use Turbo variants** for lower latency
2. **Use smaller models** (8B vs 70B) when quality allows
3. **Stream responses** for better perceived latency
4. **Use `max_tokens` wisely** — set it to what you actually need
5. **Warm up requests** — first request may be slower due to model loading

```python
# Latency-optimized example
response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",  # Small + Turbo
    messages=[{"role": "user", "content": "Quick question: what is 2+2?"}],
    max_tokens=10,   # Only generate what you need
    temperature=0,   # Deterministic (faster)
    stream=True,     # Start receiving tokens immediately
)
```

---

## Image Generation (Serverless)

```python
response = client.images.generate(
    model="black-forest-labs/FLUX.1-schnell",
    prompt="A sunset over the mountains",
    n=1,
    width=1024,
    height=1024,
    steps=4,  # schnell only needs 4 steps
)

image_url = response.data[0].url
```
