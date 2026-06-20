# Modal Web Endpoints

> Source: https://modal.com/docs/guide/web-endpoints
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal web endpoints let you expose Modal functions as public HTTP APIs. They support multiple frameworks (FastAPI, Flask, ASGI, WSGI) and automatically handle scaling, SSL, and deployment.

## Endpoint Types

### 1. `@modal.fastapi_endpoint` (Simplest)

For simple single-route handlers. Automatically has CORS enabled.

```python
import modal
from typing import Optional

app = modal.App("web-endpoints")

@app.function()
@modal.fastapi_endpoint(method="GET")
def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}

@app.function()
@modal.fastapi_endpoint(method="POST")
async def process(body: dict):
    return {"processed": True, "data": body}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | str | `"GET"` | HTTP method: GET, POST, PUT, DELETE, etc. |
| `label` | str | function name | Custom URL segment |
| `wait_for_response` | bool | `True` | Whether to wait for response |
| `custom_domains` | list | None | Custom domain names |

### 2. `@modal.asgi_app` (Full Control)

For complete FastAPI/Starlette applications:

```python
from fastapi import FastAPI
from pydantic import BaseModel

web_app = FastAPI(title="My Modal API", version="1.0.0")

class PredictRequest(BaseModel):
    text: str
    max_length: int = 100

class PredictResponse(BaseModel):
    result: str
    model: str

@web_app.get("/health")
async def health():
    return {"status": "healthy"}

@web_app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    # Process request
    result = f"Processed: {req.text[:req.max_length]}"
    return PredictResponse(result=result, model="my-model")

@app.function(gpu="A10G", timeout=60)
@modal.asgi_app()
def serve_api():
    return web_app
```

### 3. `@modal.wsgi_app` (Flask/Django)

For WSGI-compatible frameworks:

```python
from flask import Flask, request, jsonify

flask_app = Flask(__name__)

@flask_app.route("/")
def hello():
    return jsonify({"message": "Hello from Flask on Modal!"})

@flask_app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    return jsonify({"result": f"Processed: {data}"})

@app.function(image=modal.Image.debian_slim().pip_install("flask"))
@modal.wsgi_app()
def serve_flask():
    return flask_app
```

### 4. `@modal.web_server` (Custom Port)

For any web server that listens on a port:

```python
import subprocess

@app.function(
    image=modal.Image.debian_slim().pip_install("uvicorn", "fastapi")
)
@modal.web_server(port=8000)
def serve_custom():
    subprocess.Popen(["uvicorn", "myapp:app", "--host", "0.0.0.0", "--port", "8000"])
```

## Complete API Example

```python
import modal
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os

app = modal.App("production-api")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi", "torch", "transformers", "pydantic")
)

# FastAPI application
api = FastAPI(
    title="ML Inference API",
    description="Run ML models via Modal",
    version="1.0.0"
)

# CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

class GenerateResponse(BaseModel):
    text: str
    tokens_used: int

# Routes
@api.get("/")
async def root():
    return {"api": "ML Inference API", "version": "1.0.0"}

@api.get("/health")
async def health():
    return {"status": "healthy"}

@api.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if len(req.prompt) > 10000:
        raise HTTPException(status_code=400, detail="Prompt too long")
    
    # In production, call your model here
    result = f"Generated: {req.prompt[:50]}..."
    return GenerateResponse(text=result, tokens_used=len(result.split()))

# Modal function
@app.function(
    image=image,
    gpu="A10G",
    secrets=[modal.Secret.from_name("api-keys")],
    timeout=150,
    concurrency_limit=20,
)
@modal.asgi_app()
def serve():
    return api
```

## Deployment

```bash
# Deploy to Modal
modal deploy my_api.py

# Output:
# Created deployment: my-api
# Web endpoint URL: https://username--production-api-serve.modal.run
```

## URL Structure

```
https://{workspace}--{app-name}-{function-name}.modal.run
```

Examples:
- `https://johndoe--my-app-hello.modal.run`
- `https://myorg--production-api-serve.modal.run`

## Custom Domains

Configure in the Modal dashboard under your app's settings:

```
my-api.mycompany.com → username--my-app-serve.modal.run
```

## Request Limits

| Limit | Value |
|-------|-------|
| Max request timeout | 150 seconds |
| Max request body size | 10 MB (configurable) |
| Max concurrent requests | Set via `concurrency_limit` |

## Path Parameters

```python
from fastapi import FastAPI

api = FastAPI()

@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

@api.get("/items/{item_id}/details")
async def get_item_details(item_id: str, include_metadata: bool = False):
    return {"item_id": item_id, "metadata": include_metadata}
```

## Query Parameters

```python
@api.get("/search")
async def search(
    q: str,
    limit: int = 10,
    offset: int = 0,
    sort: str = "relevance"
):
    return {
        "query": q,
        "limit": limit,
        "offset": offset,
        "sort": sort
    }
```

## Request Headers

```python
from fastapi import Header, HTTPException

@api.get("/secure")
async def secure_route(
    x_api_key: Optional[str] = Header(None)
):
    if x_api_key != os.environ.get("EXPECTED_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"data": "secret"}
```

## File Uploads

```python
from fastapi import UploadFile, File

@api.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "size": len(contents),
        "content_type": file.content_type
    }
```

## Background Tasks

```python
from fastapi import BackgroundTasks

def process_in_background(data: dict):
    # Long-running operation
    pass

@api.post("/submit")
async def submit_job(body: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_in_background, body)
    return {"status": "queued"}
```

## Response Models and Status Codes

```python
from fastapi import status
from fastapi.responses import JSONResponse, StreamingResponse

@api.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: dict):
    return {"created": item}

@api.get("/stream")
async def stream():
    async def generate():
        for i in range(10):
            yield f"data: chunk {i}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request

@api.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )

@api.get("/risky")
async def risky_route():
    try:
        result = might_fail()
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Middleware

```python
from fastapi import Request
import time

@api.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Testing Web Endpoints

```python
# Local testing with httpx
import httpx

# Test against local Modal serve
BASE_URL = "https://username--my-app-serve.modal.run"

response = httpx.post(f"{BASE_URL}/generate", json={
    "prompt": "Hello world",
    "max_tokens": 50
})
print(response.json())
```
