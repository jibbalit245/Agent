# Mistral AI Overview

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/ — content below is from model training data (knowledge cutoff August 2025).

## What is Mistral AI?

Mistral AI is a French AI company offering:
- **La Plateforme (le Chat API):** Hosted API for Mistral's proprietary and open models
- **Open-source models:** Mistral 7B, Mixtral 8x7B, Mixtral 8x22B (Apache 2.0)
- **Proprietary frontier models:** Mistral Large, Mistral Medium, Mistral Small
- **Specialized models:** Codestral (code), Mistral Embed (embeddings), Pixtral (vision)
- **On-premise/self-hosting:** Models available for deployment on Azure, AWS, GCP, and private infrastructure

---

## API Base URL

```
https://api.mistral.ai/v1
```

---

## Authentication

```bash
export MISTRAL_API_KEY="your_api_key_here"
```

```
Authorization: Bearer your_api_key_here
```

---

## Core Capabilities

| Capability | Description |
|---|---|
| **Chat completions** | Multi-turn conversations with all models |
| **Function calling** | JSON-structured tool use |
| **JSON mode** | Structured output |
| **Embeddings** | Text embedding generation |
| **Vision** | Multimodal understanding (Pixtral) |
| **Code generation** | Specialized with Codestral |
| **Fine-tuning** | Fine-tune on your data |
| **Agents** | Agent framework via le Chat |

---

## Quick Start

### Install SDK

```bash
pip install mistralai
```

### Python Example

```python
from mistralai import Mistral

client = Mistral(api_key="your_api_key")

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "user", "content": "What is the best French cheese?"}
    ],
)

print(response.choices[0].message.content)
```

### OpenAI SDK Compatibility

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.mistral.ai/v1",
    api_key="your_mistral_api_key",
)

response = client.chat.completions.create(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### JavaScript

```javascript
import { Mistral } from "@mistralai/mistralai";

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const response = await client.chat.complete({
  model: "mistral-large-latest",
  messages: [{ role: "user", content: "What is the best French cheese?" }],
});

console.log(response.choices[0].message.content);
```

### cURL

```bash
curl -X POST https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Model Tiers

| Tier | Models | Use Case |
|---|---|---|
| **Premier** | Mistral Large, Mistral Medium | Highest quality, complex tasks |
| **Efficient** | Mistral Small, Mistral 7B Instruct | Balanced cost/performance |
| **Specialized** | Codestral, Pixtral, Mistral Embed | Domain-specific tasks |
| **Research** | Open-weight models | Self-hosting, research |

---

## Deployment Options

| Option | Description |
|---|---|
| **La Plateforme** | Hosted API at api.mistral.ai |
| **Azure AI** | Deploy via Azure marketplace |
| **AWS Bedrock** | Deploy via AWS Bedrock |
| **Google Cloud** | Deploy via Vertex AI |
| **Self-hosting** | Run open models on your own GPUs |
| **Mistral le Chat** | Consumer chat interface |

---

## Key Links

- Console: https://console.mistral.ai/
- Models: https://docs.mistral.ai/getting-started/models/
- API Playground: https://console.mistral.ai/playground/
- Pricing: https://mistral.ai/technology/#pricing
- Discord: https://discord.gg/mistralai
