# Modal Volumes

> Source: https://modal.com/docs/guide/volumes
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal Volumes provide persistent, distributed storage for your Modal functions. Unlike ephemeral container storage, data in Volumes persists between function runs and can be shared across multiple containers simultaneously.

## Creating Volumes

```python
import modal

# Create or retrieve an existing volume
volume = modal.Volume.from_name("my-volume", create_if_missing=True)
```

### Volume CLI

```bash
# List volumes
modal volume list

# Create a volume
modal volume create my-volume

# Delete a volume
modal volume delete my-volume

# Copy files into a volume
modal volume put my-volume ./local-file.txt /remote-file.txt

# Download files from a volume
modal volume get my-volume /remote-file.txt ./local-file.txt

# List volume contents
modal volume ls my-volume /path
```

## Using Volumes in Functions

Attach volumes by mapping mount paths:

```python
import modal
from pathlib import Path

app = modal.App("volume-example")
volume = modal.Volume.from_name("model-weights", create_if_missing=True)

MODEL_DIR = Path("/models")

@app.function(
    gpu="A10G",
    volumes={MODEL_DIR: volume}
)
def use_volume():
    # Read from volume
    model_files = list(MODEL_DIR.iterdir())
    print(f"Files in volume: {model_files}")
    
    # Write to volume
    output_path = MODEL_DIR / "output.txt"
    output_path.write_text("Hello from Modal!")
    
    # IMPORTANT: Commit changes to persist them
    volume.commit()
    
    return str(model_files)
```

## Persisting Data

```python
@app.function(volumes={"/data": volume})
def save_data(content: str):
    import json
    from pathlib import Path
    
    # Write data
    data_file = Path("/data/results.json")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_file, "w") as f:
        json.dump({"content": content, "timestamp": "2024-01-15"}, f)
    
    # Commit to persist
    volume.commit()
    
    print(f"Saved to {data_file}")
```

## Reading Persisted Data

```python
@app.function(volumes={"/data": volume})
def read_data() -> dict:
    import json
    from pathlib import Path
    
    data_file = Path("/data/results.json")
    
    if not data_file.exists():
        return {"error": "No data found"}
    
    with open(data_file) as f:
        return json.load(f)
```

## Model Weight Caching Pattern

The most common use case: cache model weights to avoid re-downloading:

```python
import modal

app = modal.App("cached-model")
volume = modal.Volume.from_name("model-cache", create_if_missing=True)
image = modal.Image.debian_slim().pip_install("transformers", "torch", "huggingface_hub")

CACHE_DIR = "/cache"

@app.function(
    image=image,
    volumes={CACHE_DIR: volume},
    secrets=[modal.Secret.from_name("huggingface-token")],
    gpu="A100-80GB",
    timeout=600,
)
def run_model(prompt: str) -> str:
    import os
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    
    # Use volume as HuggingFace cache
    os.environ["HF_HOME"] = f"{CACHE_DIR}/huggingface"
    
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    
    # First run downloads to volume; subsequent runs use cache
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=200)
    
    return tokenizer.decode(output[0], skip_special_tokens=True)
```

## Dataset Storage

```python
@app.function(volumes={"/datasets": volume}, timeout=3600)
def prepare_dataset():
    """Download and store large dataset in volume."""
    import requests
    from pathlib import Path
    
    dataset_path = Path("/datasets/my-dataset")
    dataset_path.mkdir(parents=True, exist_ok=True)
    
    # Download dataset
    for i, url in enumerate(DATASET_URLS):
        response = requests.get(url)
        (dataset_path / f"file_{i}.jsonl").write_bytes(response.content)
    
    volume.commit()
    print(f"Dataset saved to volume")

@app.function(volumes={"/datasets": volume})
def train_on_dataset():
    """Use the stored dataset for training."""
    from pathlib import Path
    import json
    
    dataset_path = Path("/datasets/my-dataset")
    data = []
    for file in dataset_path.glob("*.jsonl"):
        with open(file) as f:
            for line in f:
                data.append(json.loads(line))
    
    print(f"Loaded {len(data)} examples")
    # Train model...
```

## Volume Commit / Reload

### `volume.commit()`

After writing files, call `commit()` to ensure changes are persisted and visible to other containers:

```python
@app.function(volumes={"/data": volume})
def writer():
    Path("/data/file.txt").write_text("hello")
    volume.commit()  # Persist changes
```

### `volume.reload()`

In long-running containers, reload to see changes made by other containers:

```python
@app.function(volumes={"/data": volume})
def reader():
    volume.reload()  # Get latest changes from other containers
    content = Path("/data/file.txt").read_text()
    return content
```

## Shared Volumes Between Functions

Multiple functions can share the same volume:

```python
volume = modal.Volume.from_name("shared-data")

@app.function(volumes={"/shared": volume})
def producer():
    Path("/shared/data.json").write_text('{"key": "value"}')
    volume.commit()

@app.function(volumes={"/shared": volume})
def consumer():
    volume.reload()  # Ensure we see latest
    data = Path("/shared/data.json").read_text()
    return data
```

## Volume Size and Limits

- Volumes can hold large amounts of data (terabytes scale)
- No hard size limit per volume
- Best for: model weights, datasets, checkpoints, outputs

## Snapshot / Checkpoint Pattern

```python
@app.function(volumes={"/checkpoints": volume}, gpu="H100", timeout=86400)
def long_training_job():
    import os
    
    # Check for existing checkpoint
    ckpt_path = "/checkpoints/latest.pt"
    start_epoch = 0
    
    if os.path.exists(ckpt_path):
        print("Resuming from checkpoint...")
        checkpoint = torch.load(ckpt_path)
        model.load_state_dict(checkpoint["model"])
        start_epoch = checkpoint["epoch"]
    
    # Training loop
    for epoch in range(start_epoch, 100):
        train_one_epoch(model, data, epoch)
        
        # Save checkpoint every 10 epochs
        if epoch % 10 == 0:
            torch.save({
                "epoch": epoch,
                "model": model.state_dict(),
            }, ckpt_path)
            volume.commit()  # Persist checkpoint
            print(f"Checkpoint saved at epoch {epoch}")
```

## NetworkFileSystem (Deprecated)

`modal.NetworkFileSystem` is the older storage primitive. It is still supported but `modal.Volume` is recommended for new projects:

```python
# Old (deprecated)
nfs = modal.NetworkFileSystem.from_name("my-nfs")

@app.function(network_file_systems={"/data": nfs})
def old_function():
    pass

# New (recommended)
volume = modal.Volume.from_name("my-volume")

@app.function(volumes={"/data": volume})
def new_function():
    pass
```

## Accessing Volumes Locally

```bash
# List volume contents
modal volume ls my-volume /

# Download files
modal volume get my-volume /models/weights.pt ./weights.pt

# Upload files
modal volume put my-volume ./weights.pt /models/weights.pt
```
