# Token Counting
> Source: https://platform.claude.com/docs/en/api/token-counting.md
> Fetched: 2026-06-20
---

## Overview

The token counting endpoint lets you count tokens before sending a request, so you can predict costs, check if a prompt fits the context window, and make routing decisions.

**Do not use `tiktoken`.** It's OpenAI's tokenizer and undercounts Claude tokens by ~15-20%.

## Endpoint

```
POST /v1/messages/count_tokens
```

Same request shape as `/v1/messages`, minus `max_tokens` and `stream`.

## Python Example

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=[{"role": "user", "content": "Hello, world!"}],
)
print(response.input_tokens)  # e.g. 14
```

## Count Tokens with System Prompt

```python
response = client.messages.count_tokens(
    model="claude-opus-4-8",
    system="You are a helpful coding assistant.",
    messages=[{"role": "user", "content": "How do I reverse a list in Python?"}],
)
print(response.input_tokens)
```

## Count Tokens with Tools

```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}]

response = client.messages.count_tokens(
    model="claude-opus-4-8",
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
)
print(response.input_tokens)
```

## Count Tokens for Multi-Turn Conversation

```python
messages = [
    {"role": "user", "content": "Tell me about photosynthesis."},
    {"role": "assistant", "content": "Photosynthesis is the process..."},
    {"role": "user", "content": "How does the light reaction work?"},
]

response = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=messages,
)
print(response.input_tokens)
```

## Count Tokens for Files / Images

```python
import base64

with open("document.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode()

response = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data}
            },
            {"type": "text", "text": "Summarize this document."}
        ]
    }],
)
print(response.input_tokens)
```

## TypeScript Example

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.messages.countTokens({
  model: "claude-opus-4-8",
  messages: [{ role: "user", content: "Hello, world!" }],
});
console.log(response.input_tokens);
```

## Pre-Request Check Pattern

```python
def fits_context(messages, system=None, model="claude-opus-4-8"):
    """Check if a conversation fits in the context window."""
    context_windows = {
        "claude-opus-4-8": 1_000_000,
        "claude-sonnet-4-6": 1_000_000,
        "claude-haiku-4-5": 200_000,
    }
    limit = context_windows.get(model, 200_000)
    
    token_response = client.messages.count_tokens(
        model=model,
        system=system,
        messages=messages,
    )
    
    return token_response.input_tokens < limit * 0.9  # 10% safety margin
```

## Pricing Estimation

```python
def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate cost in USD."""
    pricing = {
        "claude-opus-4-8": {"input": 5.00, "output": 25.00},
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
        "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
    }
    
    if model not in pricing:
        raise ValueError(f"Unknown model: {model}")
    
    input_cost = (input_tokens / 1_000_000) * pricing[model]["input"]
    output_cost = (output_tokens / 1_000_000) * pricing[model]["output"]
    return input_cost + output_cost

# Count tokens first
token_response = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=messages,
)
input_tokens = token_response.input_tokens
estimated_cost = estimate_cost(input_tokens, 2000, "claude-opus-4-8")
print(f"Estimated cost: ${estimated_cost:.4f}")
```

## Key Facts

- Token counts are exact, not estimates — the same tokenizer is used for counting and billing
- The endpoint returns only `input_tokens` (not output — output is unknown before generation)
- Token counts include overhead for message formatting, roles, and system prompt structure
- Tools add significant token overhead — count with tools included in your payload
- Cache control markers do not affect token counts (only billing)
- Context windows: 1M tokens for Opus 4.8, Opus 4.7, Opus 4.6, Sonnet 4.6; 200K for Haiku 4.5
