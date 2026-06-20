# LiteLLM  
> Source: https://docs.litellm.ai/docs/  
> Fetched: 2026-06-20

## What Is LiteLLM?

LiteLLM is an open-source Python SDK and proxy server (AI Gateway) that provides:
- **Universal interface**: Call 100+ LLM providers using the same OpenAI-style API
- **SDK**: Direct Python library (`litellm.completion()`) that maps any model to the right provider
- **Proxy server**: Self-hostable FastAPI server that adds virtual API keys, budgets, fallbacks, retries, caching, and observability

**This is extremely relevant for multi-provider AI harnesses** — it lets you swap providers without changing application code.

## Installation

```bash
pip install litellm

# For proxy server
pip install 'litellm[proxy]'
```

## Python SDK: Basic Usage

```python
from litellm import completion

# OpenAI
response = completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Anthropic
response = completion(
    model="anthropic/claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Google Gemini
response = completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Vertex AI
response = completion(
    model="vertex_ai/gemini-2.0-flash-001",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Ollama (local)
response = completion(
    model="ollama/llama3",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Together AI
response = completion(
    model="together_ai/meta-llama/Llama-3-70b-chat-hf",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Groq
response = completion(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

## Provider API Key Configuration

LiteLLM reads API keys from environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google Gemini API
export GEMINI_API_KEY="AIza..."

# Vertex AI
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
export VERTEX_PROJECT="your-project-id"
export VERTEX_LOCATION="us-central1"

# AWS Bedrock
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION_NAME="us-east-1"

# Azure OpenAI
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com/"
export AZURE_API_VERSION="2024-02-01"

# Together AI
export TOGETHERAI_API_KEY="..."

# Groq
export GROQ_API_KEY="..."

# Ollama (no key needed, just base URL)
# Uses http://localhost:11434 by default
```

Or pass in code using `os.environ/` prefix in config (security best practice for proxy):

```yaml
# config.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY  # reads from env var
```

## Model Naming Convention

LiteLLM uses `provider/model-name` format:

| Provider | Example Model String |
|----------|---------------------|
| OpenAI | `openai/gpt-4o` |
| Anthropic | `anthropic/claude-sonnet-4-20250514` |
| Google Gemini | `gemini/gemini-2.0-flash` |
| Vertex AI | `vertex_ai/gemini-2.0-flash-001` |
| AWS Bedrock | `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0` |
| Azure OpenAI | `azure/your-deployment-name` |
| Together AI | `together_ai/meta-llama/Llama-3-70b-chat-hf` |
| Groq | `groq/llama-3.3-70b-versatile` |
| Ollama | `ollama/llama3` |
| HuggingFace | `huggingface/meta-llama/Llama-2-70b` |

## Proxy Server Setup

The LiteLLM Proxy is a self-hosted API gateway that exposes an OpenAI-compatible endpoint.

### Step 1: Create config file

```yaml
# config.yaml
model_list:
  - model_name: gpt-4o           # alias your clients will use
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY

  - model_name: llama3-local
    litellm_params:
      model: ollama/llama3
      api_base: http://localhost:11434

router_settings:
  num_retries: 3
  retry_after: 5

litellm_settings:
  drop_params: true              # ignore unsupported params
  success_callback: ["langfuse"] # optional observability
```

### Step 2: Start the proxy

```bash
litellm --port 4000 --config config.yaml

# Or with Docker
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -p 4000:4000 \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml
```

### Step 3: Use the proxy with any OpenAI-compatible client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="any-string"  # proxy manages real keys
)

response = client.chat.completions.create(
    model="claude-sonnet",   # uses alias from config
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Model Fallbacks

```python
from litellm import completion

# If primary fails, try fallbacks
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    fallbacks=["claude-sonnet-4-20250514", "gemini/gemini-2.0-flash"]
)
```

In proxy config:
```yaml
router_settings:
  fallbacks: [
    {"gpt-4o": ["claude-sonnet", "gemini-flash"]}
  ]
```

## Load Balancing

```yaml
model_list:
  # Multiple deployments of same model
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY_1
      rpm: 500          # requests per minute limit

  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o-deployment
      api_base: https://resource1.openai.azure.com/
      api_key: os.environ/AZURE_KEY_1
      rpm: 1000
```

## Key Management (Proxy)

The proxy supports virtual API keys with per-key budgets:

```bash
# Create a virtual key with budget
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{"max_budget": 100, "budget_duration": "30d"}'
```

## Supported Providers (partial list)

OpenAI, Anthropic, Google Gemini, Google Vertex AI, AWS Bedrock, Azure OpenAI, Ollama, Together AI, Groq, Mistral AI, Cohere, HuggingFace, Replicate, Fireworks AI, Perplexity, DeepSeek, xAI (Grok), and 80+ more.

## References

- [LiteLLM Documentation](https://docs.litellm.ai/docs/)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [Supported Providers](https://docs.litellm.ai/docs/providers)
- [Proxy Quick Start](https://docs.litellm.ai/docs/proxy/docker_quick_start)
