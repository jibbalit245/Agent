# Modal Images

> Source: https://modal.com/docs/guide/images
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal functions run inside Docker-compatible containers. You define container images using `modal.Image`, which provides a fluent API for building images with Python packages, system dependencies, and custom commands.

## Base Images

### `modal.Image.debian_slim()`

Minimal Debian-based Python image (recommended for most use cases):

```python
image = modal.Image.debian_slim()

# With specific Python version
image = modal.Image.debian_slim(python_version="3.11")
image = modal.Image.debian_slim(python_version="3.10")
```

### `modal.Image.from_registry()`

Use any public Docker image:

```python
# From Docker Hub
image = modal.Image.from_registry("nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04")

# From any registry
image = modal.Image.from_registry("ghcr.io/my-org/my-image:latest")
```

### `modal.Image.from_dockerfile()`

Build from a local Dockerfile:

```python
image = modal.Image.from_dockerfile("Dockerfile")

# With build args
image = modal.Image.from_dockerfile(
    "Dockerfile",
    build_args={"BASE_IMAGE": "python:3.11"}
)
```

### `modal.Image.micromamba()`

Use Micromamba (conda-compatible) for environment management:

```python
image = modal.Image.micromamba(python_version="3.11").micromamba_install(
    "cudatoolkit=11.8",
    "pytorch",
    channels=["conda-forge", "pytorch"]
)
```

## Installing Python Packages

### `pip_install()`

```python
# Single package
image = modal.Image.debian_slim().pip_install("numpy")

# Multiple packages
image = modal.Image.debian_slim().pip_install(
    "numpy",
    "pandas",
    "scikit-learn",
    "matplotlib"
)

# With version pins
image = modal.Image.debian_slim().pip_install(
    "torch==2.1.0",
    "transformers==4.35.0",
    "accelerate==0.24.0"
)

# From requirements.txt
image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

# From pyproject.toml
image = modal.Image.debian_slim().pip_install_from_pyproject("pyproject.toml")

# From git repository
image = modal.Image.debian_slim().pip_install(
    "git+https://github.com/huggingface/transformers.git@main"
)
```

### `uv_pip_install()` (Faster Alternative)

```python
# Uses uv for faster package installation
image = modal.Image.debian_slim().uv_pip_install("numpy", "pandas")
```

## System Packages

### `apt_install()`

```python
image = modal.Image.debian_slim().apt_install(
    "libgomp1",
    "libgl1-mesa-glx",
    "ffmpeg",
    "git"
)
```

## Running Commands

### `run_commands()`

```python
image = modal.Image.debian_slim().run_commands(
    "git clone https://github.com/some/repo /opt/repo",
    "cd /opt/repo && pip install -e .",
    "echo 'Build complete'"
)

# With environment variables
image = modal.Image.debian_slim().run_commands(
    "curl -fsSL https://example.com/install.sh | bash",
    env={"INSTALL_DIR": "/opt/myapp"}
)
```

## Environment Variables

### `env()`

```python
image = modal.Image.debian_slim().env({
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUNBUFFERED": "1",
    "HF_HOME": "/cache/huggingface",
    "TORCH_HOME": "/cache/torch"
})
```

## Method Chaining

Images are built by chaining methods:

```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx", "ffmpeg", "git")
    .pip_install(
        "torch==2.1.0",
        "torchvision==0.16.0",
        "transformers==4.35.0",
        "diffusers==0.21.0",
        "accelerate==0.24.0",
        "xformers==0.0.22"
    )
    .env({
        "HF_HOME": "/root/.cache/huggingface",
        "PYTHONUNBUFFERED": "1"
    })
    .run_commands("pip install flash-attn --no-build-isolation")
)
```

## Using Images in Functions

```python
import modal

app = modal.App("my-app")

image = modal.Image.debian_slim().pip_install("requests", "numpy")

@app.function(image=image)
def my_function():
    import requests
    import numpy as np
    return np.array([1, 2, 3]).mean()
```

## App-level Default Image

```python
app = modal.App("my-app", image=image)

# All functions use this image unless overridden
@app.function()
def function_one():
    pass  # Uses default image

@app.function(image=different_image)
def function_two():
    pass  # Uses different_image
```

## Common Image Patterns

### PyTorch / Deep Learning

```python
torch_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.1.0+cu118",
        "torchvision==0.16.0+cu118",
        index_url="https://download.pytorch.org/whl/cu118"
    )
    .pip_install(
        "transformers",
        "accelerate",
        "bitsandbytes",
        "scipy"
    )
)
```

### HuggingFace / Diffusers

```python
diffusers_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx")
    .pip_install(
        "torch==2.1.0",
        "diffusers==0.21.0",
        "transformers==4.35.0",
        "accelerate==0.24.0",
        "xformers==0.0.22",
        "Pillow",
        "safetensors"
    )
)
```

### Data Science

```python
data_science_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy",
        "pandas",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "jupyter",
        "plotly"
    )
)
```

### Web Scraping / Browser

```python
scraping_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "chromium",
        "chromium-driver",
        "xvfb"
    )
    .pip_install(
        "playwright",
        "selenium",
        "beautifulsoup4",
        "requests"
    )
    .run_commands("playwright install chromium")
)
```

### API Server

```python
api_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi",
        "uvicorn",
        "pydantic",
        "httpx",
        "aiohttp"
    )
)
```

## Caching

Modal caches built images, so layers are only rebuilt when they change. To force a rebuild:

```python
# Add a force_build parameter
image = modal.Image.debian_slim().pip_install(
    "numpy",
    force_build=True  # Forces this layer to rebuild
)
```

## Run Functions Inside Image Build

```python
def download_model():
    """This runs during image build to pre-download weights."""
    from huggingface_hub import snapshot_download
    snapshot_download("meta-llama/Llama-2-7b")

image = (
    modal.Image.debian_slim()
    .pip_install("huggingface_hub", "transformers")
    .run_function(
        download_model,
        secrets=[modal.Secret.from_name("huggingface-token")]
    )
)
```

## Mounts vs Images

- **Images** - Package dependencies baked into the container (rebuilt when deps change, cached)
- **Mounts** - Local files copied into container at runtime (for local code/data)

```python
# Mount local code for development
@app.function(
    image=image,
    mounts=[modal.Mount.from_local_dir("./src", remote_path="/app/src")]
)
def dev_function():
    pass
```

## Image Build Time

Images are built once and cached. Build time depends on:
- Number of packages to install
- Size of packages (PyTorch is large)
- System package installation
- Custom commands

Typical build times:
- Simple pip installs: 30-90 seconds
- PyTorch + Transformers: 3-5 minutes
- Complex ML stacks: 5-15 minutes

After initial build, subsequent runs use the cached image instantly.
