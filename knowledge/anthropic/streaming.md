# Streaming
> Source: https://platform.claude.com/docs/en/api/streaming.md
> Fetched: 2026-06-20
---

## Overview

Claude supports Server-Sent Events (SSE) streaming for the Messages API. Streaming delivers tokens as they are generated, reducing time-to-first-token and avoiding request timeouts for long outputs.

**When to stream:**
- `max_tokens > ~16000` (required — non-streaming times out on long outputs)
- Any response where time-to-first-token matters
- Displaying output progressively in a UI

## Basic Streaming (Python)

### Using the SDK Stream Context Manager

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=64000,
    messages=[{"role": "user", "content": "Write a detailed story about space exploration."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Get final message with usage stats after streaming
final_message = stream.get_final_message()
print(f"\n\nInput tokens: {final_message.usage.input_tokens}")
print(f"Output tokens: {final_message.usage.output_tokens}")
```

### Async Streaming

```python
import asyncio
import anthropic

async def stream_response():
    async_client = anthropic.AsyncAnthropic()
    
    async with async_client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=64000,
        messages=[{"role": "user", "content": "Explain quantum mechanics."}]
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
    
    final = await stream.get_final_message()
    print(f"\nTotal tokens: {final.usage.input_tokens + final.usage.output_tokens}")

asyncio.run(stream_response())
```

## Raw SSE Events

For fine-grained event handling, use `stream_raw_events()`:

```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
) as stream:
    for event in stream:
        print(f"Event type: {event.type}")
        if hasattr(event, 'delta'):
            if hasattr(event.delta, 'text'):
                print(f"Text delta: {event.delta.text}")
```

## SSE Event Types

| Event Type | Description |
|---|---|
| `message_start` | Message metadata (model, usage placeholders) |
| `content_block_start` | New content block beginning (text, thinking, tool_use) |
| `content_block_delta` | Incremental content delta |
| `content_block_stop` | Content block complete |
| `message_delta` | Message-level updates: `stop_reason`, `stop_sequence`, usage |
| `message_stop` | Stream complete |

## SSE Wire Format

```
event: message_start
data: {"type":"message_start","message":{"id":"msg_01abc","type":"message","role":"assistant","content":[],"model":"claude-opus-4-8","stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":25,"output_tokens":1}}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: ping
data: {"type":"ping"}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"!"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":5}}

event: message_stop
data: {"type":"message_stop"}
```

## Streaming with Tools

Tool use blocks are also streamed:

```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=4096,
    tools=[{
        "name": "get_weather",
        "description": "Get weather data",
        "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
    }],
    messages=[{"role": "user", "content": "What's the weather in Paris?"}]
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if hasattr(event.content_block, 'type'):
                if event.content_block.type == "tool_use":
                    print(f"\nTool call: {event.content_block.name}")
        elif event.type == "content_block_delta":
            if hasattr(event.delta, 'text'):
                print(event.delta.text, end="", flush=True)
            elif hasattr(event.delta, 'partial_json'):
                print(event.delta.partial_json, end="", flush=True)

final = stream.get_final_message()
```

## Streaming with Thinking

```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[{"role": "user", "content": "Solve this step by step: ..."}]
) as stream:
    current_block_type = None
    
    for event in stream:
        if event.type == "content_block_start":
            current_block_type = getattr(event.content_block, 'type', None)
            if current_block_type == "thinking":
                print("\n[THINKING]", end="")
        elif event.type == "content_block_delta":
            if hasattr(event.delta, 'thinking'):
                print(event.delta.thinking, end="", flush=True)
            elif hasattr(event.delta, 'text'):
                if current_block_type == "thinking":
                    print("\n[RESPONSE]", end="")
                    current_block_type = "text"
                print(event.delta.text, end="", flush=True)
```

## Raw HTTP SSE (curl)

```bash
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-8",
    "max_tokens": 1024,
    "stream": true,
    "messages": [{"role": "user", "content": "Hello, Claude"}]
  }'
```

## Raw HTTP SSE (Python with requests)

```python
import json
import requests

def stream_completion(messages, model="claude-opus-4-8", max_tokens=1024):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "stream": True,
            "messages": messages,
        },
        stream=True,
    )
    response.raise_for_status()
    
    for line in response.iter_lines():
        if not line:
            continue
        line = line.decode("utf-8")
        
        if line.startswith("event:"):
            continue
        
        if line.startswith("data:"):
            data = line[5:].strip()
            if data:
                event = json.loads(data)
                if event["type"] == "content_block_delta":
                    delta = event["delta"]
                    if delta.get("type") == "text_delta":
                        yield delta["text"]
                elif event["type"] == "message_stop":
                    return

# Usage
for chunk in stream_completion([{"role": "user", "content": "Hello!"}]):
    print(chunk, end="", flush=True)
```

## TypeScript Streaming

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const stream = await client.messages.stream({
  model: "claude-opus-4-8",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Write a story about space." }],
});

for await (const text of stream.text_stream) {
  process.stdout.write(text);
}

const finalMessage = await stream.finalMessage();
console.log("\nTotal tokens:", finalMessage.usage.input_tokens + finalMessage.usage.output_tokens);
```

## Stop Reasons in Streaming

The `message_delta` event contains the final `stop_reason`:

```python
with client.messages.stream(...) as stream:
    for event in stream:
        if event.type == "message_delta":
            print(f"Stop reason: {event.delta.stop_reason}")
            # end_turn | max_tokens | stop_sequence | tool_use | pause_turn | refusal
```

## Performance Tips

- Use async streaming (`AsyncAnthropic`) in async frameworks (FastAPI, aiohttp)
- Use `aiohttp` backend for best async performance: `AsyncAnthropic(http_client=DefaultAioHttpClient())`
- Default timeout is 10 minutes — sufficient for most streaming requests
- Set `timeout=httpx.Timeout(600.0, connect=10.0)` for very long outputs
