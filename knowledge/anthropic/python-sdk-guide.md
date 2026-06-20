# Claude API — Python SDK Guide
> Source: https://platform.claude.com/docs/en/api/sdks/python.md
> Fetched: 2026-06-20
---

## Installation

```bash
pip install anthropic
```

## Client Initialization

```python
import anthropic

# Default — resolves credentials from the environment:
# ANTHROPIC_API_KEY, or ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile.
client = anthropic.Anthropic()

# Explicit API key
client = anthropic.Anthropic(api_key="your-api-key")

# Async client
async_client = anthropic.AsyncAnthropic()
```

## Client Configuration

### Per-request overrides

```python
client.with_options(timeout=5.0, max_retries=5).messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Timeouts

Default request timeout is 10 minutes.

```python
import httpx
client = anthropic.Anthropic(timeout=20.0)
client = anthropic.Anthropic(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)
```

### Retries

The SDK auto-retries connection errors, 408, 409, 429, and ≥500 with exponential backoff (default 2 retries).

### Async performance (aiohttp backend)

```python
from anthropic import AsyncAnthropic, DefaultAioHttpClient

async with AsyncAnthropic(http_client=DefaultAioHttpClient()) as client:
    ...
```

## Basic Message Request

```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
for block in response.content:
    if block.type == "text":
        print(block.text)
```

## System Prompts

```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    system="You are a helpful coding assistant. Always provide examples in Python.",
    messages=[{"role": "user", "content": "How do I read a JSON file?"}]
)
```

## Vision (Images)

### Base64

```python
import base64

with open("image.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data
                }
            },
            {"type": "text", "text": "What's in this image?"}
        ]
    }]
)
```

### URL

```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "https://example.com/image.png"
                }
            },
            {"type": "text", "text": "Describe this image"}
        ]
    }]
)
```

## Extended Thinking / Adaptive Thinking

```python
# Fable 5 / Opus 4.8 / 4.7 / 4.6: adaptive thinking (recommended)
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high"},  # low | medium | high | max
    messages=[{"role": "user", "content": "Solve this step by step..."}]
)

for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Response: {block.text}")
```

## Streaming

```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    final_message = stream.get_final_message()
    print(f"\n\nTokens used: {final_message.usage.output_tokens}")
```

### Async Streaming

```python
async with async_client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    async for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Stream Event Types

| Event Type | Description |
| --- | --- |
| `message_start` | Contains message metadata |
| `content_block_start` | New content block beginning |
| `content_block_delta` | Incremental content update |
| `content_block_stop` | Content block complete |
| `message_delta` | Contains `stop_reason`, usage |
| `message_stop` | Message complete |

## Prompt Caching

```python
# Automatic caching (simplest)
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    cache_control={"type": "ephemeral"},
    system=large_document_text,
    messages=[{"role": "user", "content": "Summarize the key points"}]
)

# Verify cache hits
print(response.usage.cache_creation_input_tokens)  # tokens written to cache
print(response.usage.cache_read_input_tokens)      # tokens served from cache
print(response.usage.input_tokens)                 # uncached tokens
```

## Structured Outputs

### JSON Outputs (Pydantic — Recommended)

```python
from pydantic import BaseModel
from typing import List

class ContactInfo(BaseModel):
    name: str
    email: str
    plan: str
    interests: List[str]

response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Extract: Jane Doe (jane@co.com)..."}],
    output_format=ContactInfo,
)
contact = response.parsed_output  # validated ContactInfo instance
```

### Raw Schema

```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Extract info..."}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["name", "email"],
                "additionalProperties": False
            }
        }
    }
)
```

## Error Handling

```python
import anthropic

try:
    response = client.messages.create(...)
except anthropic.BadRequestError as e:
    print(f"Bad request: {e.message}")
except anthropic.AuthenticationError:
    print("Invalid API key")
except anthropic.PermissionDeniedError:
    print("API key lacks required permissions")
except anthropic.NotFoundError:
    print("Invalid model or endpoint")
except anthropic.RateLimitError as e:
    retry_after = int(e.response.headers.get("retry-after", "60"))
    print(f"Rate limited. Retry after {retry_after}s.")
except anthropic.APIStatusError as e:
    if e.status_code >= 500:
        print(f"Server error ({e.status_code}). Retry later.")
    else:
        print(f"API error: {e.message}")
except anthropic.APIConnectionError:
    print("Network error. Check internet connection.")
```

## Stop Reasons

| Value | Meaning |
|-------|---------|
| `end_turn` | Claude finished its response naturally |
| `max_tokens` | Hit the `max_tokens` limit |
| `stop_sequence` | Hit a custom stop sequence |
| `tool_use` | Claude wants to call a tool |
| `pause_turn` | Model paused and can be resumed (agentic flows) |
| `refusal` | Claude refused for safety reasons |

```python
if response.stop_reason == "refusal" and response.stop_details:
    print(f"Category: {response.stop_details.category}")
    print(f"Explanation: {response.stop_details.explanation}")
```

## Refusal Fallbacks (Claude Fable 5)

```python
response = client.beta.messages.create(
    model="claude-fable-5",
    max_tokens=16000,
    betas=["server-side-fallback-2026-06-01"],
    fallbacks=[{"model": "claude-opus-4-8"}],
    messages=[{"role": "user", "content": "..."}],
)
```

## Multi-Turn Conversations

```python
class ConversationManager:
    def __init__(self, client, model, system=None):
        self.client = client
        self.model = model
        self.system = system
        self.messages = []

    def send(self, user_message, **kwargs):
        self.messages.append({"role": "user", "content": user_message})
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 16000),
            system=self.system,
            messages=self.messages,
        )
        assistant_message = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        self.messages.append({"role": "assistant", "content": assistant_message})
        return assistant_message
```

## Compaction (long conversations)

```python
response = client.beta.messages.create(
    betas=["compact-2026-01-12"],
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=messages,
    context_management={
        "edits": [{"type": "compact_20260112"}]
    }
)
# CRITICAL: Append full content — compaction blocks must be preserved
messages.append({"role": "assistant", "content": response.content})
```

## Token Counting

```python
resp = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=[{"role": "user", "content": open("CLAUDE.md").read()}],
)
print(resp.input_tokens)
```

**Do not use `tiktoken`.** It's OpenAI's tokenizer and undercounts Claude tokens by ~15-20%.

## Response Helpers

```python
message = client.messages.create(...)
print(message._request_id)       # req_018EeWyXxfu5pfWkrYcMdjWG
print(message.to_json())          # serialize the Pydantic model
print(message.to_dict())          # plain dict

# Access raw headers
raw = client.messages.with_raw_response.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(raw.headers.get("request-id"))
message = raw.parse()
```

## Message Batches API

```python
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

# Create batch (50% cheaper)
message_batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id="request-1",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-8",
                max_tokens=16000,
                messages=[{"role": "user", "content": "Summarize climate change impacts"}]
            )
        ),
    ]
)

# Poll for completion
import time
while True:
    batch = client.messages.batches.retrieve(message_batch.id)
    if batch.processing_status == "ended":
        break
    time.sleep(60)

# Retrieve results
for result in client.messages.batches.results(message_batch.id):
    if result.result.type == "succeeded":
        msg = result.result.message
        text = next((b.text for b in msg.content if b.type == "text"), "")
        print(f"[{result.custom_id}] {text[:100]}")
```

**Key Facts:**
- Up to 100,000 requests or 256 MB per batch
- Most batches complete within 1 hour; maximum 24 hours
- Results available for 29 days after creation
- 50% cost reduction on all token usage

## Files API (Beta)

```python
# Upload a file
uploaded = client.beta.files.upload(
    file=("report.pdf", open("report.pdf", "rb"), "application/pdf"),
)
print(f"File ID: {uploaded.id}")

# Use in messages
response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize the key findings."},
            {
                "type": "document",
                "source": {"type": "file", "file_id": uploaded.id},
                "citations": {"enabled": True}
            }
        ]
    }],
    betas=["files-api-2025-04-14"],
)

# Manage files
for f in client.beta.files.list():
    print(f"{f.id}: {f.filename} ({f.size_bytes} bytes)")
client.beta.files.delete(uploaded.id)
```

**Key Facts:**
- Maximum file size: 500 MB
- Total storage: 100 GB per organization
- Files persist until deleted
- Not available on Amazon Bedrock or Google Vertex AI
