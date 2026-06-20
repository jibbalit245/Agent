# HuggingFace Common Errors and Debugging
> Sources: https://huggingface.co/docs/hub/rate-limits, https://github.com/huggingface/huggingface_hub/issues/3312, https://github.com/huggingface/huggingface_hub/issues/3553, https://drdroid.io/integration-diagnosis-knowledge/hugging-face-inference-endpoints-ratelimitexceeded-error-encountered-during-api-requests, https://discuss.huggingface.co/t/how-to-get-around-rate-limits/151947, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## HTTP 503 — Model Loading / Service Unavailable

### What it means
The model is "cold" — it has been idle and needs to load into memory before it can serve requests.

### Typical response body
```json
{
  "error": "Model is currently loading",
  "estimated_time": 20.0
}
```
Or:
```json
{
  "error": "Model is loading",
  "estimated_time": 45.234
}
```

### When it happens
- First request after the model has been idle (~15 minutes on serverless)
- Deploying a new model to a serverless endpoint
- After model eviction from GPU memory due to server load

### Solutions

**Option 1: Wait and retry**
```python
import time
import requests
import os

def query_with_retry(model_id: str, payload: dict, max_retries: int = 10) -> dict:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
    
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        
        if response.status_code == 503:
            data = response.json()
            wait_time = data.get("estimated_time", 20.0)
            print(f"Model loading (attempt {attempt + 1}), waiting {wait_time:.1f}s...")
            time.sleep(wait_time + 2)  # Add buffer
            continue
        
        response.raise_for_status()
    
    raise RuntimeError(f"Failed after {max_retries} retries")
```

**Option 2: Use `wait_for_model` option**
```python
response = requests.post(url, headers=headers, json={
    "inputs": "Hello",
    "options": {"wait_for_model": True}  # HF waits up to ~60s for model
})
```

**Option 3: Use InferenceClient (handles retries automatically)**
```python
from huggingface_hub import InferenceClient

# InferenceClient has built-in retry logic
client = InferenceClient(token=os.environ["HF_TOKEN"])
result = client.text_generation("Hello", model="gpt2")
```

**Option 4: Use dedicated endpoints (no cold starts)**
```python
# Inference Endpoints with min_replica=1 never cold start
client = InferenceClient(
    model="https://your-endpoint.aws.endpoints.huggingface.cloud",
    token=os.environ["HF_TOKEN"],
)
```

---

## HTTP 429 — Rate Limit Exceeded (Too Many Requests)

### What it means
You've exceeded the allowed request rate for your account tier.

### Response format
```
HTTP 429 Too Many Requests
```
Headers may include:
```
RateLimit-Limit: 100
RateLimit-Remaining: 0
RateLimit-Reset: 1735000060
Retry-After: 300
```

### When it happens
- Making too many requests in a 5-minute fixed window
- Using a token-less request (anonymous users have extremely low limits)
- Heavy concurrent requests from a free account
- Exceeding monthly credit limits (HTTP 402 instead, but sometimes 429)

### Solutions

**Root cause #1: Not passing a token**
```python
# WRONG - no auth = near-zero rate limit
response = requests.post(url, json={"inputs": "hello"})

# CORRECT - always pass your token
headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
response = requests.post(url, headers=headers, json={"inputs": "hello"})
```

**Root cause #2: Not using HF_TOKEN in all downstream calls**
```bash
# Make sure HF_TOKEN is exported in your shell/environment
export HF_TOKEN=hf_xxxxxxxxxxxxxxxx
```

**Retry with backoff**
```python
import time
import requests
from requests.exceptions import HTTPError

def query_with_rate_limit_retry(url: str, headers: dict, payload: dict) -> dict:
    for attempt in range(5):
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 429:
            # Use Retry-After header if available
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after}s (attempt {attempt + 1}/5)")
            time.sleep(retry_after)
            continue
        
        response.raise_for_status()
        return response.json()
    
    raise RuntimeError("Rate limit retry budget exhausted")
```

**Using huggingface_hub SDK (automatically handles 429)**
```python
# The huggingface_hub SDK parses Retry-After header and waits automatically
from huggingface_hub import InferenceClient

client = InferenceClient(token=os.environ["HF_TOKEN"])
# Automatically retries on 429 with correct backoff
```

**Spreading requests over time**
```python
import asyncio
from huggingface_hub import AsyncInferenceClient

async def process_with_rate_limiting(items: list, delay: float = 0.5):
    client = AsyncInferenceClient(token=os.environ["HF_TOKEN"])
    results = []
    
    for item in items:
        result = await client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": item}],
        )
        results.append(result.choices[0].message.content)
        await asyncio.sleep(delay)  # Rate-limit yourself
    
    return results
```

**Upgrading to avoid rate limits:**
- Free → PRO ($9/mo): 8x more quota
- PRO → Enterprise: highest available quota
- Use your own provider API key to bypass HF rate limits entirely

---

## HTTP 401 — Unauthorized

### What it means
No token provided, or token is invalid/expired.

### Response body
```json
{"error": "Authorization error"}
```
Or:
```json
{"error": "A token is required to access this endpoint"}
```

### Solutions

```python
# Check your token is set
import os
token = os.environ.get("HF_TOKEN")
if not token:
    raise ValueError("HF_TOKEN not set!")

# Verify token is valid
from huggingface_hub import whoami
try:
    info = whoami(token=token)
    print(f"Logged in as: {info['name']}")
except Exception as e:
    print(f"Token invalid: {e}")
    # Go to https://huggingface.co/settings/tokens to create a new token

# Regenerate token if expired
# 1. Go to https://huggingface.co/settings/tokens
# 2. Delete the old token
# 3. Create a new one
# 4. Update your environment variable
```

---

## HTTP 403 — Forbidden (Permission Denied)

### What it means
Your token is valid, but doesn't have permission to access this resource.

**Common causes:**
1. **Gated model** — you haven't accepted the model's license
2. **Token scope too narrow** — fine-grained token missing required permissions
3. **Private repo** — you're not a collaborator/member of the org
4. **Inference permission missing** — token lacks "Make calls to Inference Providers"

### Response body examples
```json
{"error": "Access to model meta-llama/Llama-3.1-8B-Instruct is restricted. You must have access to it and be authenticated to access it."}
```
```
"403 Forbidden - Make sure your token has the correct permissions"
```

### Solutions

**For gated models:**
```python
# 1. Visit the model page and accept terms:
#    https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
# 2. Click "Request access" and fill out the form
# 3. Wait for approval (usually instant for auto-approved models)
# 4. Use the same account's token

# Check if you have access:
from huggingface_hub import HfApi
api = HfApi(token=os.environ["HF_TOKEN"])
try:
    info = api.model_info("meta-llama/Llama-3.1-8B-Instruct")
    print("Access granted!")
except Exception as e:
    print(f"No access: {e}")
```

**For token scope issues (fine-grained tokens):**
```python
# The token needs "Make calls to Inference Providers" permission
# Go to: https://huggingface.co/settings/tokens
# Create a new fine-grained token with:
# - "Make calls to Inference Providers" checked
# - OR use a read/write token (simpler, broader access)
```

---

## HTTP 402 — Payment Required (Credit Exhausted)

### What it means
Your monthly inference credits are exhausted and pay-as-you-go is not enabled.

### Response body
```json
{"error": "You've exceeded your monthly quota for Inference Providers"}
```

### Solutions
1. **Upgrade to PRO** ($9/mo) for higher monthly credits
2. **Enable pay-as-you-go** in your billing settings
3. **Wait until next month** when credits reset
4. **Use your own provider API key** (bypass HF credits entirely):

```python
from huggingface_hub import InferenceClient

# Use your own Featherless API key directly
client = InferenceClient(
    provider="featherless-ai",
    api_key="your-featherless-api-key",  # Not your HF token
)
```

---

## Model Not Found / 404

### What it means
The model ID doesn't exist on the Hub, or it's a private model you can't see.

### Solutions
```python
# Verify the model exists on HuggingFace Hub
# Go to: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

# Check capitalization — model IDs are case-sensitive
# WRONG: "Meta-Llama/llama-3.1-8b-instruct"
# RIGHT: "meta-llama/Llama-3.1-8B-Instruct"

# List files in a repo to verify it exists
from huggingface_hub import HfApi
api = HfApi()
try:
    files = list(api.list_repo_files("meta-llama/Llama-3.1-8B-Instruct"))
    print("Model exists:", files[:3])
except Exception as e:
    print(f"Model not found or no access: {e}")
```

---

## Provider Not Supporting a Model

### What it means
You're requesting a model from a provider that doesn't host it.

### Error example
```
"Provider 'featherless-ai' does not support model 'some-obscure-model'"
```

### Solutions
```python
# Check which providers support the model:
# Go to the model page on HuggingFace and look for "Inference Providers" section

# Use :auto to let HF pick a supporting provider
from openai import OpenAI
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)
# Instead of :featherless-ai
response = client.chat.completions.create(
    model="some-model:auto",  # HF picks available provider
    messages=[{"role": "user", "content": "Hello"}],
)

# Or try featherless-ai which has the largest catalog (6,700+ models)
response = client.chat.completions.create(
    model="some-model:featherless-ai",
    messages=[{"role": "user", "content": "Hello"}],
)
```

---

## Token Permission Error (Fine-Grained Tokens)

### Error: "ValueError: Provider 'featherless-ai' not supported"

This can indicate you need a newer version of `huggingface_hub`:

```bash
# Featherless-ai support requires v0.33.0+
pip install --upgrade huggingface_hub
python -c "import huggingface_hub; print(huggingface_hub.__version__)"
```

---

## SSL / Connection Errors

```python
# If behind a proxy or SSL issues:
import os
os.environ["REQUESTS_CA_BUNDLE"] = "/path/to/custom/ca-bundle.crt"

# Or disable SSL verification (NOT for production):
import requests
session = requests.Session()
session.verify = False
```

---

## Debugging Tips

### Enable verbose logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# huggingface_hub uses 'huggingface_hub' logger
logger = logging.getLogger("huggingface_hub")
logger.setLevel(logging.DEBUG)
```

### Check what token you're using
```python
from huggingface_hub import whoami
import os

token = os.environ.get("HF_TOKEN", "NOT SET")
print(f"Token starts with: {token[:10] if token != 'NOT SET' else 'NOT SET'}...")

info = whoami(token=token)
print(f"Logged in as: {info['name']}")
print(f"Email: {info['email']}")
```

### Test basic connectivity
```bash
# Test token validity
curl https://huggingface.co/api/whoami \
  -H "Authorization: Bearer $HF_TOKEN"

# Test inference API
curl https://api-inference.huggingface.co/models/gpt2 \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Hello"}'

# Test inference router
curl https://router.huggingface.co/v1/chat/completions \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-3.1-8B-Instruct:auto", "messages": [{"role": "user", "content": "Hello"}]}'
```

### Check Hub rate limits documentation
Rate limits are documented (somewhat) at: https://huggingface.co/docs/hub/rate-limits

All quotas reset on **5-minute fixed windows** — spread requests evenly to avoid hitting limits in short bursts.

---

## Quick Error Reference

| HTTP Code | Error | Quick Fix |
|-----------|-------|-----------|
| 401 | Unauthorized | Set/fix HF_TOKEN |
| 402 | Payment Required | Enable pay-as-you-go or upgrade plan |
| 403 | Forbidden | Accept model license / check token permissions |
| 404 | Not Found | Verify model ID, check access to private repos |
| 429 | Too Many Requests | Add retry with backoff, upgrade plan, add token |
| 500 | Internal Server Error | Retry, report to HF if persistent |
| 503 | Service Unavailable | Model loading — retry after `estimated_time` seconds |

---

## References

- [Hub Rate Limits Docs](https://huggingface.co/docs/hub/rate-limits)
- [GitHub Issue: 429 handling](https://github.com/huggingface/huggingface_hub/issues/3553)
- [Forum: Rate limit solutions](https://discuss.huggingface.co/t/how-to-get-around-rate-limits/151947)
- [Gated Models](https://huggingface.co/docs/hub/en/models-gated)
- [InferenceClient Error Handling](https://huggingface.co/docs/huggingface_hub/package_reference/inference_client)
