# Ollama Model Library

Source: https://ollama.com/library
Note: The Ollama library page (ollama.com/library) returned HTTP 403 during crawl. This file contains known models from Ollama's documentation and public sources.

## Overview

Ollama provides a library of pre-built models that can be pulled and run locally. Models are specified in the format `model:tag` where the tag indicates the size/variant.

## How to Use Models

```bash
# Pull a model
ollama pull llama3

# Run a model interactively
ollama run llama3

# Run with specific tag/size
ollama run llama3:70b

# List local models
ollama list

# Remove a model
ollama rm llama3
```

## Popular Models

### Meta Llama
```bash
ollama pull llama3           # Llama 3 8B (default)
ollama pull llama3:70b       # Llama 3 70B
ollama pull llama3.1         # Llama 3.1 8B
ollama pull llama3.1:70b     # Llama 3.1 70B
ollama pull llama3.1:405b    # Llama 3.1 405B
ollama pull llama3.2         # Llama 3.2 3B
ollama pull llama3.2:1b      # Llama 3.2 1B
ollama pull llama3.2-vision  # Llama 3.2 Vision 11B
ollama pull llama3.3         # Llama 3.3 70B
```

### Google Gemma
```bash
ollama pull gemma            # Gemma 7B
ollama pull gemma:2b         # Gemma 2B
ollama pull gemma2           # Gemma 2 9B
ollama pull gemma2:27b       # Gemma 2 27B
ollama pull gemma3           # Gemma 3 4B
ollama pull gemma3:1b        # Gemma 3 1B
ollama pull gemma3:12b       # Gemma 3 12B
ollama pull gemma3:27b       # Gemma 3 27B
```

### Microsoft Phi
```bash
ollama pull phi3             # Phi-3 Mini 3.8B
ollama pull phi3:medium      # Phi-3 Medium 14B
ollama pull phi3.5           # Phi-3.5 Mini 3.8B
ollama pull phi4             # Phi-4 14B
ollama pull phi4-mini        # Phi-4 Mini 3.8B
```

### Mistral / Mixtral
```bash
ollama pull mistral          # Mistral 7B
ollama pull mistral-nemo     # Mistral Nemo 12B
ollama pull mistral-large    # Mistral Large 123B
ollama pull mixtral          # Mixtral 8x7B
ollama pull mixtral:8x22b    # Mixtral 8x22B
```

### Qwen (Alibaba)
```bash
ollama pull qwen             # Qwen 4B
ollama pull qwen:7b          # Qwen 7B
ollama pull qwen:14b         # Qwen 14B
ollama pull qwen:72b         # Qwen 72B
ollama pull qwen2            # Qwen2 7B
ollama pull qwen2:0.5b       # Qwen2 0.5B
ollama pull qwen2:72b        # Qwen2 72B
ollama pull qwen2.5          # Qwen2.5 7B
ollama pull qwen2.5:72b      # Qwen2.5 72B
ollama pull qwen2.5-coder    # Qwen2.5 Coder 7B
ollama pull qwen3            # Qwen3 8B
ollama pull qwen3:0.6b       # Qwen3 0.6B
ollama pull qwen3:4b         # Qwen3 4B
ollama pull qwen3:14b        # Qwen3 14B
ollama pull qwen3:32b        # Qwen3 32B
ollama pull qwen3:30b-a3b    # Qwen3 30B MoE
ollama pull qwen3:235b-a22b  # Qwen3 235B MoE
```

### DeepSeek
```bash
ollama pull deepseek-r1      # DeepSeek R1 7B
ollama pull deepseek-r1:1.5b # DeepSeek R1 1.5B
ollama pull deepseek-r1:8b   # DeepSeek R1 8B
ollama pull deepseek-r1:14b  # DeepSeek R1 14B
ollama pull deepseek-r1:32b  # DeepSeek R1 32B
ollama pull deepseek-r1:70b  # DeepSeek R1 70B
ollama pull deepseek-r1:671b # DeepSeek R1 671B
ollama pull deepseek-v2      # DeepSeek V2
ollama pull deepseek-coder   # DeepSeek Coder 6.7B
ollama pull deepseek-coder-v2 # DeepSeek Coder V2
```

### Coding Models
```bash
ollama pull codellama        # Code Llama 7B
ollama pull codellama:13b    # Code Llama 13B
ollama pull codellama:34b    # Code Llama 34B
ollama pull codegemma        # CodeGemma 7B
ollama pull starcoder2       # StarCoder2 7B
ollama pull starcoder2:15b   # StarCoder2 15B
ollama pull qwen2.5-coder    # Qwen2.5 Coder 7B
ollama pull qwen2.5-coder:32b # Qwen2.5 Coder 32B
```

### Embedding Models
```bash
ollama pull nomic-embed-text         # Nomic Embed Text 137M
ollama pull mxbai-embed-large        # MixedBread Large 334M
ollama pull all-minilm               # All-MiniLM 22M
ollama pull snowflake-arctic-embed   # Snowflake Arctic Embed
ollama pull bge-m3                   # BGE M3
ollama pull bge-large                # BGE Large
```

### Vision Models
```bash
ollama pull llava            # LLaVA 7B
ollama pull llava:13b        # LLaVA 13B
ollama pull llava:34b        # LLaVA 34B
ollama pull llava-llama3     # LLaVA with Llama 3
ollama pull moondream        # Moondream 1.8B
ollama pull bakllava         # BakLLaVA
ollama pull llama3.2-vision  # Llama 3.2 Vision 11B
ollama pull llama3.2-vision:90b # Llama 3.2 Vision 90B
```

### Specialized Models
```bash
ollama pull llama3-groq-tool-use  # Llama 3 for tool use
ollama pull llama3.1-storm        # Storm variant
ollama pull solar                  # Solar 10.7B
ollama pull wizard-vicuna-uncensored # Wizard Vicuna
ollama pull orca-mini              # Orca Mini 3B
ollama pull vicuna                 # Vicuna 7B
ollama pull neural-chat            # Intel Neural Chat
ollama pull starling-lm            # Starling LM 7B
ollama pull dolphin-mistral        # Dolphin Mistral 7B
ollama pull nous-hermes2           # Nous Hermes 2
```

## Model Tags / Sizes

Most models support multiple size tags:
- `:1b`, `:3b`, `:7b`, `:8b` - Small models
- `:13b`, `:14b` - Medium models  
- `:30b`, `:32b`, `:34b` - Large models
- `:70b`, `:72b` - Extra large models
- `:405b`, `:671b` - Massive models

## Quantization Tags

Models also support quantization variants:
- `q4_0` - 4-bit quantization (smallest, fastest)
- `q4_K_M` - 4-bit with medium K-quant
- `q5_0` - 5-bit quantization
- `q5_K_M` - 5-bit with medium K-quant
- `q8_0` - 8-bit quantization (highest quality)
- `f16` - Full 16-bit (largest, most accurate)

Example: `ollama pull llama3:8b-instruct-q4_0`

## Model File Format

Models are stored in `~/.ollama/models/` by default.

## Search Models

Browse all models at: https://ollama.com/library

Or search via CLI:
```bash
ollama search llama
```

## Custom Model Registration

You can create custom models using a Modelfile:
```bash
# Create a Modelfile
cat > Modelfile << 'EOF'
FROM llama3
SYSTEM You are a helpful assistant.
EOF

# Create the model
ollama create my-assistant -f Modelfile

# Run it
ollama run my-assistant
```
