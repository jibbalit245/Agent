# Ollama OpenAI Compatibility Blog Post

Source: https://ollama.com/blog/openai-compatibility
Note: The Ollama blog page returned HTTP 403 during crawl. Content below is sourced from the official Ollama OpenAI compatibility documentation at https://raw.githubusercontent.com/ollama/ollama/main/docs/api/openai-compatibility.mdx

See also: /home/user/Agent/knowledge/tools/ollama-openai-compat.md for the full technical reference.

## Overview

Ollama provides an OpenAI-compatible API, allowing you to use existing OpenAI SDKs and tools with local models running via Ollama.

The compatibility endpoint is available at:
```
http://localhost:11434/v1
```

## Key Announcement Points

- Ollama supports the OpenAI Chat Completions API format
- Existing code using OpenAI SDK can be pointed at Ollama with minimal changes
- All Ollama models are available through the compatible endpoint
- Supports streaming, tool/function calling, and structured outputs

## Using OpenAI Python SDK with Ollama

```python
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # required but ignored
)

response = client.chat.completions.create(
    model="llama3",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

## Using OpenAI Node.js SDK with Ollama

```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
    baseURL: 'http://localhost:11434/v1',
    apiKey: 'ollama', // required but unused
});

const completion = await openai.chat.completions.create({
    model: 'llama3',
    messages: [{ role: 'user', content: 'Hello!' }],
});

console.log(completion.choices[0].message.content);
```

## Migration from OpenAI

To migrate existing OpenAI code to use Ollama:

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3`
3. Change `base_url` to `http://localhost:11434/v1`
4. Change `api_key` to any non-empty string (e.g., `'ollama'`)
5. Change `model` to the Ollama model name (e.g., `'llama3'` instead of `'gpt-4'`)

## Supported Endpoints

| Endpoint | Status |
|----------|--------|
| `/v1/chat/completions` | Supported |
| `/v1/completions` | Supported |
| `/v1/embeddings` | Supported |
| `/v1/models` | Supported |
| `/v1/models/{model}` | Supported |

## Supported Parameters

Most OpenAI parameters are supported:
- `model`
- `messages`
- `stream`
- `temperature`
- `top_p`
- `max_tokens`
- `tools` (function calling)
- `tool_choice`
- `format` (json mode)
- `seed`
- `stop`

## Not Supported

- Assistants API
- Batch API
- Fine-tuning API
- Files API
- Moderation API

## Integration with LiteLLM

LiteLLM also supports routing through Ollama's OpenAI-compatible endpoint:

```python
import litellm

response = litellm.completion(
    model="ollama/llama3",
    messages=[{"role": "user", "content": "Hello"}],
    api_base="http://localhost:11434"
)
```

For full technical documentation, see the OpenAI compatibility reference file.
