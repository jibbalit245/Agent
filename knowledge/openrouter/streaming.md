# OpenRouter Streaming
> Source: https://openrouter.ai/docs/streaming
> Fetched: 2026-06-20
---

## Overview

OpenRouter supports Server-Sent Events (SSE) streaming, fully compatible with OpenAI's streaming format. Set `"stream": true` in your request body.

## Basic Streaming Request

```python
import anthropic

client = anthropic.Anthropic(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://yourapp.com",
        "X-Title": "My App",
    }
)

with client.messages.stream(
    model="anthropic/claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a short story."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## OpenAI SDK Streaming

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
)

stream = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Write a short story."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Raw HTTP SSE

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer sk-or-v1-..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-sonnet-4-6",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

## SSE Event Format

Each event is a line prefixed with `data: `:

```
data: {"id":"gen-xyz","object":"chat.completion.chunk","created":1719849600,"model":"anthropic/claude-sonnet-4-6","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}

data: {"id":"gen-xyz","object":"chat.completion.chunk","created":1719849600,"model":"anthropic/claude-sonnet-4-6","choices":[{"index":0,"delta":{"content":" there"},"finish_reason":null}]}

data: {"id":"gen-xyz","object":"chat.completion.chunk","created":1719849600,"model":"anthropic/claude-sonnet-4-6","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

## Stream Termination

The stream ends with `data: [DONE]`. Always handle this sentinel value to avoid JSON parse errors.

```python
import json
import requests

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-or-v1-...",
        "Content-Type": "application/json",
    },
    json={
        "model": "anthropic/claude-sonnet-4-6",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
    },
    stream=True,
)

for line in response.iter_lines():
    if line:
        line = line.decode("utf-8")
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            delta = chunk["choices"][0]["delta"]
            if "content" in delta and delta["content"]:
                print(delta["content"], end="", flush=True)
```

## Streaming with Tool Calls

Tool calls are also streamed in chunks:

```json
{
  "choices": [{
    "delta": {
      "tool_calls": [{
        "index": 0,
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"loca"
        }
      }]
    }
  }]
}
```

Accumulate `arguments` across chunks before parsing the complete JSON.

## TypeScript / Node.js Streaming

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: "sk-or-v1-...",
  baseURL: "https://openrouter.ai/api/v1",
  defaultHeaders: {
    "HTTP-Referer": "https://yourapp.com",
    "X-Title": "My App",
  },
});

const stream = await client.chat.completions.create({
  model: "anthropic/claude-sonnet-4-6",
  messages: [{ role: "user", content: "Write a short story." }],
  stream: true,
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || "");
}
```

## Fetch API Streaming (Browser)

```javascript
const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": "Bearer sk-or-v1-...",
    "Content-Type": "application/json",
    "HTTP-Referer": window.location.href,
    "X-Title": document.title,
  },
  body: JSON.stringify({
    model: "anthropic/claude-sonnet-4-6",
    messages: [{ role: "user", content: "Hello" }],
    stream: true,
  }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split("\n");
  
  for (const line of lines) {
    if (line.startsWith("data: ") && line !== "data: [DONE]") {
      const data = JSON.parse(line.slice(6));
      const content = data.choices[0]?.delta?.content;
      if (content) process(content);
    }
  }
}
```

## Streaming Usage Statistics

The final chunk (before `[DONE]`) includes usage statistics when `stream_options.include_usage` is set:

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "stream": true,
  "stream_options": {"include_usage": true}
}
```

Final chunk:
```json
{
  "choices": [{"finish_reason": "stop", "delta": {}}],
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 123,
    "total_tokens": 168
  }
}
```
