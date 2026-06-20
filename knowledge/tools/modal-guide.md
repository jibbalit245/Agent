# Modal - Introduction & Guide

> Source: https://modal.com/docs/guide
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## What is Modal?

Modal is a serverless cloud platform for Python that lets you run compute-intensive code (especially ML/AI) in the cloud without managing infrastructure. You write Python, decorate functions, and Modal handles containers, scaling, and hardware.

## Key Features

- **Serverless GPU compute** - On-demand H100, A100, A10G, T4 GPUs
- **Auto-scaling** - Zero to thousands of parallel workers
- **No idle charges** - Pay only for actual compute time
- **Fast cold starts** - Optimized container caching
- **Python-first** - Deploy directly from your local code
- **Persistent storage** - Volumes and distributed file systems
- **Web endpoints** - Expose functions as HTTP APIs
- **Scheduled jobs** - Cron-based scheduling
- **Secrets management** - Secure environment variable injection

## Installation

```bash
pip install modal
```

## Authentication

```bash
# Create account and authenticate
modal token new
```

This opens a browser to create an account or log in. Your token is stored at `~/.modal.toml`.

## Hello World

```python
# hello.py
import modal

app = modal.App("hello-world")

@app.function()
def hello():
    print("Hello from Modal!")
    return "Hello, World!"

@app.local_entrypoint()
def main():
    result = hello.remote()
    print(result)
```

Run it:
```bash
modal run hello.py
```

## Core Concepts

### Apps

An `App` is the top-level container for your Modal code:

```python
import modal

app = modal.App("my-app")
```

All functions, images, volumes, and secrets belong to an App.

### Functions

Functions are the unit of work in Modal. Decorate any Python function with `@app.function()`:

```python
@app.function(
    gpu="A100",           # Hardware
    memory=16384,         # Memory in MB
    cpu=4,                # CPU cores
    timeout=600,          # Max runtime in seconds
    retries=2,            # Auto-retry on failure
    concurrency_limit=10, # Max parallel instances
    image=my_image        # Custom container image
)
def my_ml_function(data):
    import torch
    # Your code here
    return result
```

### Calling Functions

```python
# Remote execution (runs in Modal cloud)
result = my_function.remote(arg1, arg2)

# Parallel map over a list
results = list(my_function.map([item1, item2, item3]))

# Async parallel
async_results = my_function.map.aio([item1, item2, item3])

# Spawn in background
future = my_function.spawn(arg1)
result = future.get()

# Batch parallel with gather
futures = [my_function.spawn(item) for item in items]
results = [f.get() for f in futures]
```

### Local Entrypoint

The `@app.local_entrypoint()` decorator marks the function that runs locally when you use `modal run`:

```python
@app.local_entrypoint()
def main():
    # This runs on YOUR machine
    result = my_modal_function.remote()  # This runs in Modal cloud
    print(result)
```

## Deploying Apps

### Ephemeral Run (Development)

```bash
modal run my_script.py
```
Runs once and stops. Good for testing.

### Deployed App (Production)

```bash
modal deploy my_script.py
```
Creates a persistent deployment. Web endpoints stay live, scheduled functions keep running.

### Serve (Live Development)

```bash
modal serve my_script.py
```
Hot-reloads on code changes. Great for web endpoint development.

## Complete Example: ML Inference

```python
import modal

app = modal.App("ml-inference")

# Define the container image
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch",
    "transformers",
    "accelerate"
)

@app.function(
    image=image,
    gpu="A10G",
    timeout=300
)
def generate_text(prompt: str) -> str:
    from transformers import pipeline
    
    generator = pipeline("text-generation", model="gpt2")
    result = generator(prompt, max_length=100)
    return result[0]["generated_text"]

@app.local_entrypoint()
def main():
    result = generate_text.remote("Once upon a time")
    print(result)
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `modal run file.py` | Run app ephemerally |
| `modal deploy file.py` | Deploy app permanently |
| `modal serve file.py` | Run with hot-reload |
| `modal token new` | Set up authentication |
| `modal app list` | List your apps |
| `modal app stop my-app` | Stop a deployed app |
| `modal app logs my-app` | View app logs |
| `modal volume list` | List volumes |
| `modal secret list` | List secrets |
| `modal profile list` | List auth profiles |

## Project Structure

```
my_project/
├── modal_app.py      # Main Modal app
├── models/           # Model files
├── utils/            # Utility functions
└── requirements.txt  # Dependencies (included in image)
```

### Module-based deployment

```bash
# Deploy a module
modal deploy -m my_package.my_module

# Run a function in a module
modal run my_package.my_module::my_function
```

## Environment Variables

```python
import os

@app.function(
    env={"MY_VAR": "my_value", "DEBUG": "true"}
)
def my_function():
    value = os.environ["MY_VAR"]
    return value
```

## Timeouts and Retries

```python
@app.function(
    timeout=3600,    # 1 hour max runtime
    retries=3,       # Retry up to 3 times on failure
)
def long_running_task():
    pass
```

## Resource Configuration

```python
@app.function(
    gpu="H100",         # GPU type
    memory=32768,       # 32 GB RAM
    cpu=8,              # 8 CPU cores
    ephemeral_disk=100  # 100 GB ephemeral disk (GB)
)
def resource_intensive_task():
    pass
```
