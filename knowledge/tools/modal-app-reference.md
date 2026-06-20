# Modal App Reference

> Source: https://modal.com/docs/reference/modal.App
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## modal.App

The `App` class is the top-level container for a Modal application. Previously called `modal.Stub` (deprecated).

## Constructor

```python
import modal

app = modal.App(
    name="my-app",           # Optional: app name (default: script filename)
    image=my_image,          # Optional: default image for all functions
    secrets=[my_secret],     # Optional: default secrets for all functions
    mounts=[my_mount],       # Optional: default mounts for all functions
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | script filename | App name (used in URLs and dashboard) |
| `image` | modal.Image | `modal.Image.debian_slim()` | Default container image |
| `secrets` | list[modal.Secret] | `[]` | Default secrets applied to all functions |
| `mounts` | list[modal.Mount] | `[]` | Default mounts applied to all functions |

## Decorators

### `@app.function()`

Register a function to run on Modal:

```python
@app.function(
    image=modal.Image.debian_slim().pip_install("numpy"),
    gpu="A100",
    memory=32768,
    cpu=8,
    timeout=3600,
    retries=2,
    concurrency_limit=10,
    allow_concurrent_inputs=5,
    secrets=[modal.Secret.from_name("my-secret")],
    mounts=[modal.Mount.from_local_dir("./data", remote_path="/data")],
    volumes={"/models": modal.Volume.from_name("model-weights")},
    schedule=modal.Period(hours=1),
    keep_warm=1,
    cloud="aws",
)
def my_function(x: int) -> int:
    return x * 2
```

#### `@app.function()` Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `image` | modal.Image | Container image to use |
| `gpu` | str or list | GPU type: `"T4"`, `"A10G"`, `"A100"`, `"H100"`, `"any"` |
| `memory` | int | Memory in MB |
| `cpu` | float | CPU cores |
| `timeout` | int | Max runtime in seconds (default: 300) |
| `retries` | int | Number of retry attempts on failure |
| `concurrency_limit` | int | Max parallel instances |
| `allow_concurrent_inputs` | int | Max concurrent inputs per container |
| `secrets` | list | Secrets to inject as env vars |
| `mounts` | list | Local directories to mount |
| `volumes` | dict | Persistent volumes to mount |
| `schedule` | modal.Period or modal.Cron | Run on a schedule |
| `keep_warm` | int | Min number of warm containers to maintain |
| `cloud` | str | Cloud provider: `"aws"`, `"gcp"`, `"oci"` |
| `region` | str | Specific region to run in |
| `ephemeral_disk` | int | Ephemeral disk in GB |

### `@app.cls()`

Register a class with methods as Modal functions:

```python
@app.cls(
    image=image,
    gpu="A10G",
    secrets=[modal.Secret.from_name("api-keys")],
)
class ModelServer:
    @modal.enter()
    def setup(self):
        """Called once when container starts."""
        self.model = load_model()
    
    @modal.exit()
    def cleanup(self):
        """Called when container shuts down."""
        self.model = None
    
    @modal.method()
    def predict(self, input: str) -> str:
        return self.model(input)
    
    @modal.method()
    def batch_predict(self, inputs: list) -> list:
        return [self.model(i) for i in inputs]
```

### `@app.local_entrypoint()`

Mark a function to run locally when using `modal run`:

```python
@app.local_entrypoint()
def main():
    # Runs on your local machine
    result = my_modal_function.remote("hello")
    print(result)
```

## Calling Remote Functions

### `.remote()` - Single Call

```python
result = my_function.remote(arg1, arg2, kwarg=value)
```

### `.map()` - Parallel Map

```python
# Synchronous parallel map
results = list(my_function.map([item1, item2, item3]))

# With keyword args
results = list(my_function.map(items, kwargs={"param": "value"}))

# Async map
async for result in my_function.map.aio(items):
    print(result)
```

### `.starmap()` - Parallel Map with Unpacking

```python
# Each item is unpacked as positional args
results = list(my_function.starmap([(1, 2), (3, 4), (5, 6)]))
```

### `.spawn()` - Fire and Forget

```python
# Returns a handle immediately
future = my_function.spawn(arg)

# Later, get the result
result = future.get()
```

### `.for_each()` - Side Effects Only

```python
# Parallel execution, ignores return values
my_function.for_each(items)
```

## App Lifecycle Methods

### `app.run()` (Context Manager)

```python
# Programmatic alternative to `modal run`
with app.run():
    result = my_function.remote(data)
    print(result)
```

### `app.local_entrypoint()`

```python
@app.local_entrypoint()
def main():
    pass
```

## Class Lifecycle Decorators

### `@modal.enter()`

```python
@app.cls(gpu="A10G")
class MyClass:
    @modal.enter()
    def load_model(self):
        """Runs once when container starts. Use for expensive setup."""
        self.model = load_expensive_model()
    
    @modal.enter(snap=True)
    def setup_with_snapshot(self):
        """Like enter() but can be snapshotted for faster cold starts."""
        self.data = prepare_data()
```

### `@modal.exit()`

```python
@app.cls()
class MyClass:
    @modal.exit()
    def teardown(self):
        """Runs when container is being shut down."""
        self.cleanup()
```

### `@modal.method()`

```python
@app.cls()
class MyClass:
    @modal.method()
    def my_method(self, arg):
        return self.model(arg)
    
    # Methods can also be web endpoints
    @modal.method()
    @modal.fastapi_endpoint()
    def web_method(self):
        return {"status": "ok"}
```

## Function Reference

### `modal.Function.from_name()`

Reference a deployed function from another app:

```python
# In a different script, reference a deployed function
deployed_fn = modal.Function.from_name("my-app", "my_function")
result = deployed_fn.remote("input")
```

## App Configuration Examples

### App with Default Image

```python
image = modal.Image.debian_slim().pip_install("numpy", "pandas")

app = modal.App("data-processing", image=image)

# All functions use this image by default
@app.function()
def process(data):
    import numpy as np
    return np.array(data).mean()

@app.function()
def analyze(data):
    import pandas as pd
    return pd.DataFrame(data).describe().to_dict()
```

### App with Default Secrets

```python
app = modal.App(
    "api-service",
    secrets=[
        modal.Secret.from_name("openai-key"),
        modal.Secret.from_name("database-creds")
    ]
)

# All functions have access to these secrets
@app.function()
def call_openai(prompt: str):
    import os
    from openai import OpenAI
    client = OpenAI()  # Uses OPENAI_API_KEY from default secret
    return client.chat.completions.create(...)
```

### Multi-Function App

```python
import modal

app = modal.App("ml-pipeline")
image = modal.Image.debian_slim().pip_install("torch", "transformers")

@app.function(image=image, gpu="T4")
def preprocess(data: dict) -> dict:
    """Light preprocessing, T4 is sufficient."""
    return {"processed": data}

@app.function(image=image, gpu="A100-80GB", timeout=600)
def train(data: dict) -> str:
    """Heavy training, needs A100."""
    return "model_weights.pt"

@app.function(image=image, gpu="A10G")
def inference(model_path: str, input: str) -> str:
    """Inference, A10G is cost-effective."""
    return f"Result for: {input}"

@app.local_entrypoint()
def main():
    data = {"samples": list(range(1000))}
    processed = preprocess.remote(data)
    model = train.remote(processed)
    result = inference.remote(model, "test input")
    print(result)
```

## Deprecated: modal.Stub

`modal.Stub` was the old name for `modal.App`. It is now deprecated and raises `AttributeError`:

```python
# Old (deprecated) - DO NOT USE
stub = modal.Stub("my-app")

# New (correct)
app = modal.App("my-app")
```
