# Modal Web Functions (Webhooks)

> Source: https://modal.com/docs/guide/webhooks
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal's "Web Functions" (also called webhooks) allow you to expose Modal functions as HTTP endpoints. This is the primary way to receive webhook callbacks, build APIs, or integrate with external services.

## Types of Web Endpoints

| Decorator | Use Case |
|-----------|----------|
| `@modal.fastapi_endpoint` (formerly `@modal.web_endpoint`) | Simple request handlers, auto CORS |
| `@modal.asgi_app` | Full ASGI apps (FastAPI, Starlette) |
| `@modal.wsgi_app` | WSGI apps (Flask, Django) |
| `@modal.web_server` | Any app that listens on a port |

## Simple Web Endpoint

```python
import modal
from fastapi import Request

app = modal.App("webhooks-app")

@app.function()
@modal.fastapi_endpoint(method="POST")
async def handle_webhook(request: Request):
    """Receive and process webhooks."""
    body = await request.json()
    
    print(f"Received webhook: {body}")
    
    # Process the webhook
    event_type = body.get("type")
    if event_type == "payment.completed":
        # Handle payment
        pass
    
    return {"status": "received", "event": event_type}
```

### GET Endpoint

```python
@app.function()
@modal.fastapi_endpoint(method="GET")
def health_check():
    return {"status": "ok", "service": "my-modal-app"}
```

## Stripe Webhook Example

```python
import modal
import os
from fastapi import Request, HTTPException

app = modal.App("stripe-webhooks")

image = modal.Image.debian_slim().pip_install("stripe", "fastapi")

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("stripe-credentials")]
)
@modal.fastapi_endpoint(method="POST")
async def stripe_webhook(request: Request):
    import stripe
    
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
    
    body = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(body, sig_header, webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"Payment succeeded: {payment_intent['id']}")
    
    return {"received": True}
```

## GitHub Webhook Example

```python
import modal
import hashlib
import hmac
import os
from fastapi import Request, HTTPException

app = modal.App("github-webhooks")

@app.function(secrets=[modal.Secret.from_name("github-webhook-secret")])
@modal.fastapi_endpoint(method="POST")
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Verify HMAC signature
    secret = os.environ["GITHUB_WEBHOOK_SECRET"].encode()
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = request.headers.get("X-GitHub-Event")
    data = await request.json()
    
    if event == "push":
        repo = data["repository"]["full_name"]
        branch = data["ref"].split("/")[-1]
        print(f"Push to {repo}:{branch}")
    elif event == "pull_request":
        action = data["action"]
        pr_number = data["number"]
        print(f"PR #{pr_number}: {action}")
    
    return {"processed": True, "event": event}
```

## Full FastAPI Application

```python
import modal
from fastapi import FastAPI
from pydantic import BaseModel

app = modal.App("fastapi-app")
image = modal.Image.debian_slim().pip_install("fastapi", "pydantic")

web_app = FastAPI(title="My API")

class Item(BaseModel):
    name: str
    description: str = None
    price: float

@web_app.get("/")
async def root():
    return {"message": "Hello World"}

@web_app.post("/items/")
async def create_item(item: Item):
    return {"item": item.dict(), "created": True}

@web_app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.function(image=image)
@modal.asgi_app()
def fastapi_endpoint():
    return web_app
```

## Request Timeouts

All Modal web endpoints have a **maximum HTTP request timeout of 150 seconds**. For longer operations, use async processing:

```python
import modal
from fastapi import Request, BackgroundTasks

app = modal.App("async-webhooks")

@app.function()
def process_long_task(data: dict):
    """Long-running task - runs asynchronously."""
    import time
    time.sleep(30)  # Simulate long work
    return {"processed": True, "data": data}

@app.function()
@modal.fastapi_endpoint(method="POST")
async def webhook_handler(request: Request):
    """Returns immediately, processes in background."""
    body = await request.json()
    
    # Spawn long-running task without waiting
    process_long_task.spawn(body)
    
    # Return immediately (before 150s timeout)
    return {"status": "queued", "message": "Processing started"}
```

## Getting Webhook URLs

### After Deployment

```bash
modal deploy my_app.py
# Output includes URL like:
# https://your-username--my-app-fastapi-endpoint.modal.run
```

### URL Format

```
https://{workspace-name}--{app-name}-{function-name}.modal.run
```

### Custom Domains

Custom domains can be configured in the Modal dashboard.

## CORS Configuration

`@modal.fastapi_endpoint` automatically enables CORS for browser-based clients.

For custom CORS in `@modal.asgi_app`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

web_app = FastAPI()
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Authentication / Proxy Auth

Modal can add a layer of authentication to web endpoints:

```python
@app.function()
@modal.fastapi_endpoint(method="GET")
def protected_endpoint():
    return {"secret": "data"}
```

Access tokens can be configured in the Modal dashboard for rate-limiting or authentication.

## Serving Files / Static Assets

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

web_app = FastAPI()
web_app.mount("/static", StaticFiles(directory="static"), name="static")

@web_app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.function(
    mounts=[modal.Mount.from_local_dir("./static", remote_path="/root/static")]
)
@modal.asgi_app()
def serve():
    return web_app
```

## Streaming Responses

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

web_app = FastAPI()

@web_app.post("/stream")
async def stream_response(request: Request):
    body = await request.json()
    prompt = body["prompt"]
    
    async def generate():
        # Stream LLM output
        for token in some_llm_generator(prompt):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```
