# Replicate Python Client

> Source: https://replicate.com/docs/get-started/python and https://github.com/replicate/replicate-python
> Note: replicate.com returned HTTP 403; content compiled from GitHub README and official sources.

## Installation

```bash
pip install replicate
```

**Requirements:** Python 3.8 or higher

## Authentication

### Environment Variable (Recommended)

```bash
export REPLICATE_API_TOKEN=r8_your_token_here
```

### Custom Client Instance

```python
from replicate.client import Client
import os

replicate = Client(
    api_token=os.environ["SOME_OTHER_REPLICATE_API_TOKEN"],
    headers={"User-Agent": "my-app/1.0"}
)
```

> **Warning:** Never hardcode API tokens in your code. Use environment variables or secrets management.

## Running Models

### Basic Usage with `replicate.run()`

The simplest way to run a model:

```python
import replicate

outputs = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "astronaut riding a rocket like a horse"}
)

for index, output in enumerate(outputs):
    with open(f"output_{index}.webp", "wb") as file:
        file.write(output.read())
```

### Model Identifier Formats

```python
# owner/name (latest version)
replicate.run("stability-ai/sdxl", input={...})

# owner/name:version_hash
replicate.run(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={...}
)
```

### Wait / Timeout Configuration

```python
# Wait up to 30 seconds synchronously (1-60 second range)
output = replicate.run("model/name", input={...}, wait=30)

# Don't wait - return immediately with prediction object
output = replicate.run("model/name", input={...}, wait=False)
```

## FileOutput Objects

Since version 1.0.0, `replicate.run()` returns `FileOutput` objects instead of URL strings for file outputs.

### FileOutput Interface

| Method / Attribute | Description |
|-------------------|-------------|
| `.read()` | Read entire file into bytes |
| `.aread()` | Async version of read |
| `.url` | Access the underlying URL string |
| Iterator protocol | Stream data in chunks |
| Async iterator | Stream chunks asynchronously |

### Writing to Disk

```python
output = replicate.run("black-forest-labs/flux-schnell", input={...})

# Read entire file at once
with open('output.png', 'wb') as f:
    f.write(output[0].read())

# Stream large files in chunks
with open('output.png', 'wb') as f:
    for chunk in output[0]:
        f.write(chunk)
```

### Async File Operations

```python
import aiofiles

async with aiofiles.open(filename, 'wb') as f:
    await f.write(await output.aread())

# Or stream async
async with aiofiles.open(filename, 'wb') as f:
    async for chunk in output:
        await f.write(chunk)
```

### Opt Out of FileOutput (Legacy Behavior)

```python
output = replicate.run(
    "acmecorp/acme-model",
    input={...},
    use_file_output=False  # Returns URL strings instead
)
```

## Passing Files as Input

```python
# Pass a file object directly
output = replicate.run(
    "andreasjansson/blip-2:f677695e5e89f8b236e52ecd1d3f01beb44c34606419bcc19345e046d8f786f9",
    input={"image": open("path/to/image.jpg", "rb")}
)

# Pass a URL string
output = replicate.run(
    "some-model",
    input={"image": "https://example.com/image.jpg"}
)
```

## Streaming Output

### Stream Text Generation

```python
import replicate

for event in replicate.stream(
    "meta/meta-llama-3-70b-instruct",
    input={"prompt": "Please write a haiku about llamas."}
):
    print(str(event), end="")
```

### Stream from an Existing Prediction

```python
prediction = replicate.predictions.create(
    model="meta/meta-llama-3-70b-instruct",
    input={"prompt": "Please write a haiku about llamas."},
    stream=True,
)

for event in prediction.stream():
    print(str(event), end="")
```

## Asynchronous Operations

### Run Multiple Models Concurrently

```python
import asyncio
import replicate

model_version = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
prompts = [
    f"A chariot pulled by a team of {count} rainbow unicorns"
    for count in ["two", "four", "six", "eight"]
]

async with asyncio.TaskGroup() as tg:
    tasks = [
        tg.create_task(
            replicate.async_run(model_version, input={"prompt": prompt})
        )
        for prompt in prompts
    ]

results = [task.result() for task in tasks]
```

## Background Predictions

### Create and Poll

```python
model = replicate.models.get("kvfrans/clipdraw")
version = model.versions.get("5797a99edc939ea0e9242d5e8c9cb3bc7d125b1eac21bda852e5cb79ede2cd9b")

prediction = replicate.predictions.create(
    version=version,
    input={"prompt": "Watercolor painting of an underwater submarine"}
)

print(prediction.status)  # 'starting'
prediction.reload()
print(prediction.status)  # 'processing'
print(prediction.logs)
prediction.wait()
print(prediction.status)  # 'succeeded'
print(prediction.output)
```

### Create with Webhook

```python
prediction = replicate.predictions.create(
    version=version,
    input={"prompt": "Watercolor painting of an underwater submarine"},
    webhook="https://example.com/your-webhook",
    webhook_events_filter=["completed"]
)
```

## Prediction Management

### Cancel a Prediction

```python
prediction.cancel()
prediction.reload()
print(prediction.status)  # 'canceled'
```

### List Predictions

```python
# Get first page
page1 = replicate.predictions.list()

# Get next page
if page1.next:
    page2 = replicate.predictions.list(page1.next)
```

## Error Handling

```python
from replicate.exceptions import ModelError

try:
    output = replicate.run(
        "stability-ai/stable-diffusion-3",
        input={"prompt": "An astronaut riding a rainbow unicorn"}
    )
except ModelError as e:
    print("Failed prediction ID: " + e.prediction.id)
    print("Error logs:", e.prediction.logs)
```

## Model Management

### Get Model Info

```python
model = replicate.models.get("stability-ai/sdxl")
print(model.name)
print(model.description)
print(model.latest_version.id)
```

### List Your Models

```python
# Simple list
your_models = replicate.models.list()

# Paginate through all
models = []
for page in replicate.paginate(replicate.models.list):
    models.extend(page.results)
    if len(models) > 100:
        break
```

### Create a Model

```python
model = replicate.models.create(
    owner="your-username",
    name="my-model",
    visibility="public",  # or "private"
    hardware="gpu-a40-large"
)
```

### List Available Hardware SKUs

```python
hardware_list = replicate.hardware.list()
# Returns: ['cpu', 'gpu-t4', 'gpu-a40-small', 'gpu-a40-large', 'gpu-a100-large', 'gpu-h100']
```

## Collections

```python
# List available collections
collections = [
    collection
    for page in replicate.paginate(replicate.collections.list)
    for collection in page
]

# Get models in a collection
text_to_image_models = replicate.collections.get("text-to-image").models
```

## Fine-Tuning / Training

```python
training = replicate.trainings.create(
    model="stability-ai/sdxl",
    version="39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={
        "input_images": "https://my-domain/training-images.zip",
        "token_string": "TOK",
        "caption_prefix": "a photo of TOK",
        "max_train_steps": 1000,
        "use_face_detection_instead": False
    },
    destination="your-username/my-fine-tuned-model"
)

print(training.status)
training.wait()
print(training.status)  # 'succeeded'
```

## Web Framework Integration

### FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import replicate

app = FastAPI()

@app.get("/generate")
async def generate():
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "A beautiful sunset"}
    )
    return StreamingResponse(output[0], media_type='image/webp')
```

### Django

```python
from django.http import HttpResponse
from django.views.decorators.http import condition
import replicate

@condition(etag_func=None)
def stream_image(request):
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "A beautiful sunset"}
    )
    return HttpResponse(output[0], content_type='image/webp')
```

### Flask

```python
from flask import Flask, stream_with_context
import replicate

app = Flask(__name__)

@app.route('/generate')
def generate():
    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "A beautiful sunset"}
    )
    return app.response_class(
        stream_with_context(output[0]),
        content_type='image/webp'
    )
```

## Model Pipelines (Chaining)

```python
# Get model versions
laionide = replicate.models.get("afiaka87/laionide-v4").versions.get(
    "b21cbe271e65c1718f2999b038c18b45e21e4fba961181fbfae9342fc53b9e05"
)
swinir = replicate.models.get("jingyunliang/swinir").versions.get(
    "660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a"
)

# Chain outputs as inputs
image = laionide.predict(prompt="avocado armchair")
upscaled_image = swinir.predict(image=image)
```

## Prediction Status Values

| Status | Description |
|--------|-------------|
| `starting` | Prediction is queued and waiting to start |
| `processing` | Model is actively running |
| `succeeded` | Prediction completed successfully |
| `failed` | Prediction encountered an error |
| `canceled` | Prediction was canceled by user |
