# Ollama  
> Source: https://ollama.com/blog/openai-compatibility, https://github.com/ollama/ollama  
> Fetched: 2026-06-20

## What Is Ollama?

Ollama is an open-source tool for running large language models locally on your own hardware. It provides:
- Easy model management (pull, list, delete)
- REST API on port 11434 (OpenAI-compatible)
- Native GPU acceleration (NVIDIA, AMD, Apple Silicon)
- CPU fallback if no GPU available
- Active model library with 100+ pre-quantized models

## Installation

### macOS
```bash
# Download from https://ollama.com/download
# Or via Homebrew:
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download the installer from [ollama.com/download/windows](https://ollama.com/download)

Native Windows application with NVIDIA and AMD Radeon GPU support.

### Docker
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# With GPU support (NVIDIA)
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Running Ollama

```bash
# Start the Ollama server
ollama serve

# Server runs at http://localhost:11434
```

On macOS/Windows, Ollama runs as a background service automatically after installation.

## Pulling and Managing Models

```bash
# Pull a model
ollama pull llama3.2          # Llama 3.2 3B (default)
ollama pull llama3.2:1b       # Smaller variant
ollama pull llama3.1:8b       # Llama 3.1 8B
ollama pull llama3.1:70b      # Llama 3.1 70B (needs ~40GB VRAM)
ollama pull mistral:7b        # Mistral 7B
ollama pull mistral-nemo      # Mistral NeMo 12B
ollama pull gemma3:9b         # Google Gemma 3 9B
ollama pull gemma3:27b        # Google Gemma 3 27B
ollama pull qwen2.5:7b        # Qwen 2.5 7B
ollama pull deepseek-r1:7b    # DeepSeek R1 7B
ollama pull phi4              # Microsoft Phi-4 14B
ollama pull codellama         # Meta Code Llama (code-focused)
ollama pull nomic-embed-text  # Embedding model

# List downloaded models
ollama list

# Remove a model
ollama rm llama3.2

# Run interactively
ollama run llama3.2
```

## Memory Requirements

| Model Size | Min VRAM (GPU) | Min RAM (CPU) |
|-----------|----------------|---------------|
| 1B-3B | 2-4 GB | 4-8 GB |
| 7B-8B | 6-8 GB | 8-16 GB |
| 13B | 10-12 GB | 16-32 GB |
| 34B | 20-24 GB | 32-64 GB |
| 70B | 40+ GB (2x A100) | 80+ GB |
| 405B | 240+ GB | Not practical |

Quantized models (Q4, Q5, Q8) use less memory at some quality cost. Ollama downloads Q4 by default.

## REST API

Ollama exposes a REST API on `http://localhost:11434`:

### Generate (single-turn completion)

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "What is the capital of France?",
  "stream": false
}'
```

### Chat (multi-turn with history)

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "4"},
    {"role": "user", "content": "Multiply that by 3"}
  ],
  "stream": false
}'
```

### List Models

```bash
curl http://localhost:11434/api/tags
```

### Model Info

```bash
curl http://localhost:11434/api/show -d '{"name": "llama3.2"}'
```

## OpenAI-Compatible API (v1 Endpoint)

Ollama also exposes an OpenAI-compatible endpoint at `/v1`, allowing you to use existing OpenAI clients:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # required but ignored
)

response = client.chat.completions.create(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

## Python with the ollama Package

```python
import ollama

# Simple chat
response = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Why is the sky blue?"}]
)
print(response["message"]["content"])

# Streaming
for chunk in ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    print(chunk["message"]["content"], end="", flush=True)

# Embeddings
embedding = ollama.embeddings(
    model="nomic-embed-text",
    prompt="The quick brown fox"
)
print(embedding["embedding"])
```

Install with: `pip install ollama`

## Tool/Function Calling

Supported by tool-capable models: Llama 3.1+, Mistral Small, Qwen 2.5+, Qwen 3.

```python
import ollama

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

response = ollama.chat(
    model="llama3.1",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)
```

## GPU Support

Ollama automatically detects and uses available GPUs:
- **NVIDIA**: CUDA-based, requires NVIDIA drivers
- **AMD**: ROCm-based (Linux only for best performance)
- **Apple Silicon**: Metal acceleration (M1/M2/M3/M4)
- **CPU fallback**: Works without GPU, slower

Environment variable to control GPU layers:
```bash
OLLAMA_NUM_GPU=1 ollama run llama3.2  # force GPU
OLLAMA_NUM_GPU=0 ollama run llama3.2  # force CPU
```

## Useful Environment Variables

```bash
OLLAMA_HOST=0.0.0.0:11434   # Listen on all interfaces (for remote access)
OLLAMA_MODELS=/path/to/dir  # Custom model storage directory
OLLAMA_NUM_PARALLEL=2       # Concurrent requests
OLLAMA_MAX_LOADED_MODELS=3  # Max models in memory
```

## Model Library

Available at [ollama.com/library](https://ollama.com/library). Highlights include:
- `llama3.2`, `llama3.1` — Meta Llama series
- `mistral`, `mistral-nemo` — Mistral models
- `gemma3` — Google Gemma
- `qwen2.5`, `qwen3` — Alibaba Qwen
- `deepseek-r1`, `deepseek-v3` — DeepSeek
- `phi4` — Microsoft Phi
- `codellama` — Code-focused Llama
- `nomic-embed-text`, `mxbai-embed-large` — Embedding models

## References

- [Ollama GitHub](https://github.com/ollama/ollama)
- [OpenAI Compatibility Blog](https://ollama.com/blog/openai-compatibility)
- [Tool Support Blog](https://ollama.com/blog/tool-support)
- [Model Library](https://ollama.com/library)
- [Ollama Windows Docs](https://docs.ollama.com/windows)
