# Modal GPU Acceleration

> Source: https://modal.com/docs/guide/gpu
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal provides on-demand GPU compute without managing infrastructure. GPUs are requested via the `gpu` parameter on `@app.function()`.

## Basic GPU Usage

```python
import modal

app = modal.App("gpu-example")

@app.function(gpu="T4")
def gpu_function():
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return torch.cuda.get_device_name(0)
```

## Available GPU Types

| GPU | Identifier | VRAM | Best For |
|-----|-----------|------|----------|
| T4 | `"T4"` | 16 GB | Cost-effective inference |
| A10G | `"A10G"` | 24 GB | Mid-tier inference/training |
| L4 | `"L4"` | 24 GB | Cost-effective inference |
| A100 (40GB) | `"A100-40GB"` | 40 GB | Large model training |
| A100 (80GB) | `"A100-80GB"` | 80 GB | Large model training |
| H100 | `"H100"` | 80 GB | Fastest, cutting-edge workloads |
| Any | `"any"` | varies | Use whatever is available |

## GPU Specification Syntax

```python
# Single GPU by type
@app.function(gpu="T4")
@app.function(gpu="A10G")
@app.function(gpu="A100")     # A100-40GB by default
@app.function(gpu="A100-80GB")
@app.function(gpu="H100")

# Any available GPU (lowest cost)
@app.function(gpu="any")

# Specific count of GPUs
@app.function(gpu="A100:2")   # 2x A100
@app.function(gpu="H100:4")   # 4x H100 (up to 8)
```

## GPU Fallbacks

Request preferred GPU with fallback options if unavailable:

```python
from modal import gpu

@app.function(gpu=[gpu.H100(), gpu.A100(size="80GB"), gpu.A10G()])
def flexible_gpu_function():
    """Uses H100 if available, falls back to A100-80GB, then A10G."""
    import torch
    return torch.cuda.get_device_name(0)
```

### Fallback with `gpu` module

```python
from modal import gpu

# Specify GPU objects with more control
@app.function(gpu=gpu.H100())
def h100_function():
    pass

@app.function(gpu=gpu.A100(size="80GB", count=2))
def dual_a100_function():
    pass

@app.function(gpu=gpu.T4(count=1))
def t4_function():
    pass
```

## Multi-GPU Setup

```python
@app.function(gpu="A100:2")  # 2x A100 GPUs
def multi_gpu_training():
    import torch
    
    num_gpus = torch.cuda.device_count()
    print(f"Using {num_gpus} GPUs")
    
    # Use torch.nn.DataParallel or DistributedDataParallel
    # for multi-GPU training
```

## Complete ML Example

```python
import modal

app = modal.App("gpu-ml")

# Build image with ML dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.1.0",
    "transformers==4.35.0",
    "accelerate==0.24.0",
    "bitsandbytes==0.41.3",
)

@app.function(
    image=image,
    gpu="A100-80GB",
    timeout=600,
    memory=32768,
)
def run_llm_inference(prompt: str) -> str:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=200)
    
    return tokenizer.decode(output[0], skip_special_tokens=True)
```

## GPU Availability and Scheduling

- Modal allocates GPUs from its pool on demand
- Less common GPUs (H100) may have higher wait times
- Using `"any"` maximizes availability but gives non-deterministic hardware
- Using fallback lists gives priority order

## Checking GPU Info at Runtime

```python
@app.function(gpu="A100")
def check_gpu():
    import torch
    import subprocess
    
    print(f"PyTorch CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"GPU {i}: {props.name}")
        print(f"  VRAM: {props.total_memory / 1e9:.1f} GB")
        print(f"  CUDA capability: {props.major}.{props.minor}")
    
    # Get nvidia-smi output
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    print(result.stdout)
```

## Optimizing GPU Workloads

### Model Caching (Avoid Re-downloading)

```python
import modal

volume = modal.Volume.from_name("model-cache", create_if_missing=True)
app = modal.App("cached-model")

image = modal.Image.debian_slim().pip_install("transformers", "torch")

@app.function(
    image=image,
    gpu="A10G",
    volumes={"/cache": volume},
    secrets=[modal.Secret.from_name("huggingface-token")]
)
def load_and_run(prompt: str):
    import os
    from transformers import pipeline
    
    # Cache models to volume so they persist between runs
    os.environ["HF_HOME"] = "/cache/huggingface"
    
    pipe = pipeline("text-generation", model="gpt2", cache_dir="/cache")
    return pipe(prompt)[0]["generated_text"]
```

### Using Container Lifecycle for Warm Models

```python
from modal import enter

@app.cls(
    image=image,
    gpu="A10G",
)
class ModelServer:
    @enter()
    def load_model(self):
        """Called once when container starts - load model here."""
        from transformers import pipeline
        self.pipe = pipeline("text-generation", model="gpt2")
    
    @modal.method()
    def generate(self, prompt: str) -> str:
        """Called for each request - model is already loaded."""
        return self.pipe(prompt)[0]["generated_text"]
```

## GPU Metrics

Modal provides GPU utilization metrics in the dashboard at `modal.com`:
- GPU utilization %
- GPU memory usage
- Container duration
- Cost per run

## Common GPU Configurations

### Fast Image Generation

```python
@app.function(gpu="A10G", memory=16384, timeout=120)
def generate_image(prompt: str):
    # SDXL, FLUX-schnell, etc.
    pass
```

### Large LLM Inference

```python
@app.function(gpu="A100-80GB", memory=65536, timeout=300)
def llm_inference(prompt: str):
    # Llama 70B, Falcon 40B, etc.
    pass
```

### Fine-tuning / Training

```python
@app.function(gpu="H100:2", memory=98304, timeout=7200)
def train_model(dataset_path: str):
    # Training run - needs more memory and time
    pass
```

### Video/Image Processing

```python
@app.function(gpu="T4", memory=8192, timeout=60)
def process_video(video_url: str):
    # Cost-effective for shorter tasks
    pass
```
