# Google Gemini Python SDK (google-genai)

> Source: Fetched from PyPI (pypi.org/project/google-genai) and GitHub (github.com/googleapis/python-genai)
> Note: googleapis.github.io/python-genai returned HTTP 403
> Date: 2026-06-20

## Package Information

| Property | Value |
|----------|-------|
| Package name | `google-genai` |
| Latest version | 2.9.0 (released June 19, 2026) |
| License | Apache-2.0 |
| Python requirement | >=3.10 |
| GitHub | https://github.com/googleapis/python-genai |
| Stars | 3.8k |
| Forks | 918 |

## Installation

```bash
pip install google-genai
```

With uv:
```bash
uv pip install google-genai
```

With optional extras:
```bash
pip install google-genai[aiohttp]           # Enhanced async support
pip install google-genai[local-tokenizer]   # Local tokenization
pip install google-genai[pyopenssl]         # SSL support
```

## Core Imports

```python
from google import genai
from google.genai import types
```

## Client Initialization

### Gemini Developer API

```python
from google import genai

client = genai.Client(api_key='GEMINI_API_KEY')
```

### Agent Platform (Enterprise / Vertex AI)

```python
from google import genai

client = genai.Client(
    enterprise=True,
    project='your-project-id',
    location='global'
)
```

### Via Environment Variables

```bash
# Gemini Developer API
export GEMINI_API_KEY='your-api-key'
# OR
export GOOGLE_API_KEY='your-api-key'

# Agent Platform
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
```

```python
client = genai.Client()  # Auto-detects from environment
```

## Client Lifecycle Management

### Context Manager (Sync)

```python
from google.genai import Client

with Client() as client:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello',
    )
```

### Context Manager (Async)

```python
async with Client().aio as aclient:
    response = await aclient.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello',
    )
```

### Manual Close

```python
client = Client()
# ... use client ...
client.close()  # Sync

# Async
await aclient.aclose()
```

## API Configuration

### Setting API Version

```python
from google.genai import types

# Vertex AI (v1)
client = genai.Client(
    enterprise=True,
    project='your-project-id',
    location='global',
    http_options=types.HttpOptions(api_version='v1')
)

# Gemini Developer API (v1alpha for experimental features)
client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(api_version='v1alpha')
)
```

### Proxy Configuration

```bash
# Standard proxy
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export SSL_CERT_FILE='client.pem'
```

```python
# SOCKS5 proxy
http_options = types.HttpOptions(
    client_args={'proxy': 'socks5://user:pass@host:port'},
    async_client_args={'proxy': 'socks5://user:pass@host:port'},
)
client = Client(..., http_options=http_options)
```

## Models Module

### Generate Content

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)
print(response.text)
```

### Generate Content with Config

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        max_output_tokens=3,
        temperature=0.3,
    ),
)
print(response.text)
```

### Generate Content Stream

```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Async Generate Content

```python
response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents='Tell me a story.'
)
print(response.text)
```

### Async Generate Content Stream

```python
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story.'
):
    print(chunk.text, end='')
```

### List Models

```python
for model in client.models.list():
    print(model)

# With pagination
pager = client.models.list(config={'page_size': 10})
pager.next_page()
```

### Count Tokens

```python
response = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents='why is the sky blue?',
)
print(response.total_tokens)
```

### Compute Tokens (Vertex AI only)

```python
response = client.models.compute_tokens(
    model='gemini-2.5-flash',
    contents='why is the sky blue?',
)
```

### Local Tokenization

```python
from google.genai import local_tokenizer

tokenizer = local_tokenizer.LocalTokenizer(model_name='gemini-2.5-flash')
result = tokenizer.count_tokens("What is your name?")
result2 = tokenizer.compute_tokens("What is your name?")
```

### Embed Content

```python
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents='why is the sky blue?',
)

# With configuration
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['text 1', 'text 2'],
    config=types.EmbedContentConfig(output_dimensionality=512),
)
```

### Generate Images (Imagen)

```python
response = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt='An umbrella in the foreground, and a rainy night sky in the background',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response.generated_images[0].image.show()
```

### Generate Videos (Veo)

```python
import time

operation = client.models.generate_videos(
    model='veo-3.1-generate-preview',
    prompt='A neon hologram of a cat driving at top speed',
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

## Chats Module

```python
# Create chat
chat = client.chats.create(model='gemini-2.5-flash')

# Send message
response = chat.send_message('tell me a story')
print(response.text)

# Stream message
for chunk in chat.send_message_stream('tell me a story'):
    print(chunk.text, end='')

# Async chat
chat = client.aio.chats.create(model='gemini-2.5-flash')
response = await chat.send_message('tell me a story')

# Async stream
async for chunk in await chat.send_message_stream('tell me a story'):
    print(chunk.text, end='')
```

## Files Module (Gemini Developer API Only)

```python
# Upload
file = client.files.upload(file='document.pdf')
file = client.files.upload(
    file='data.csv',
    config=types.UploadFileConfig(display_name='My Dataset')
)

# Get info
file_info = client.files.get(name=file.name)

# List
for f in client.files.list():
    print(f.name, f.state)

# Delete
client.files.delete(name=file.name)

# Download (batch results)
content = client.files.download(file=result_file).decode('utf-8')
```

## Caches Module

```python
from google.genai import types

# Create cache
cached_content = client.caches.create(
    model='gemini-2.5-flash',
    config=types.CreateCachedContentConfig(
        contents=[...],
        system_instruction='...',
        display_name='my cache',
        ttl='3600s',
    ),
)

# Get cache
cached_content = client.caches.get(name=cached_content.name)

# Update TTL
client.caches.update(
    name=cached_content.name,
    config=types.UpdateCachedContentConfig(ttl='7200s')
)

# List caches
for cache in client.caches.list():
    print(cache.name)

# Delete cache
client.caches.delete(name=cached_content.name)

# Use with generate_content
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your question',
    config=types.GenerateContentConfig(
        cached_content=cached_content.name,
    ),
)
```

## Batches Module

```python
# Create batch job (inline)
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=[{
        "contents": [{"parts": [{"text": "Hello!"}], "role": "user"}],
    }],
    config={'display_name': 'my-batch'}
)

# Create batch job (file-based)
file = client.files.upload(file='requests.json')
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=file.name,
)

# Monitor status
import time
while batch_job.state.name not in ('JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED', 'JOB_STATE_CANCELLED'):
    time.sleep(30)
    batch_job = client.batches.get(name=batch_job.name)

# Get results
results = client.files.download(file=batch_job.dest.file_name).decode('utf-8')

# List batch jobs
for job in client.batches.list(config=types.ListBatchJobsConfig(page_size=10)):
    print(job.name, job.state.name)

# Cancel
client.batches.cancel(name=batch_job.name)

# Delete
client.batches.delete(name=batch_job.name)
```

## Interactions Module (Stateful Conversations)

```python
# Basic interaction
interaction = client.interactions.create(
    model='gemini-2.5-flash',
    input='Tell me a short joke.'
)
print(interaction.outputs[-1].text)

# Stateful conversation
interaction1 = client.interactions.create(
    model='gemini-2.5-flash',
    input='Hi, my name is Alice.'
)
interaction2 = client.interactions.create(
    model='gemini-2.5-flash',
    input='What is my name?',
    previous_interaction_id=interaction1.id
)
print(interaction2.outputs[-1].text)  # Will say "Alice"

# With tools
interaction = client.interactions.create(
    model='gemini-2.5-flash',
    input='Calculate the 50th Fibonacci number.',
    tools=[{'type': 'code_execution'}]
)

# Background (async) with deep research agent
interaction = client.interactions.create(
    input='Research the history of AI in 2025-2026.',
    agent='deep-research-pro-preview-12-2025',
    background=True
)
# Poll for completion
while True:
    interaction = client.interactions.get(id=interaction.id)
    if interaction.status in ("completed", "failed", "cancelled"):
        break
    time.sleep(10)
```

## Tunings Module (Vertex AI Only)

```python
tuning_job = client.tunings.tune(
    base_model='gemini-2.5-flash',
    training_dataset=types.TuningDataset(
        gcs_uri='gs://your-bucket/tuning-data.jsonl',
    ),
    config=types.CreateTuningJobConfig(
        epoch_count=1,
        tuned_model_display_name='my-tuned-model'
    ),
)

# Monitor
while tuning_job.state not in completed_states:
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(10)

# Use tuned model
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents='Your prompt',
)
```

## Types Reference

### GenerateContentConfig

```python
types.GenerateContentConfig(
    system_instruction="str",           # Model persona/behavior
    temperature=0.7,                    # 0.0-1.0 randomness
    top_p=0.95,                         # Nucleus sampling
    top_k=20,                           # Top-k sampling
    max_output_tokens=1024,             # Max response length
    candidate_count=1,                  # Number of candidates
    seed=42,                            # Reproducibility
    stop_sequences=['END'],             # Stop tokens
    presence_penalty=0.0,              # Repetition penalty
    frequency_penalty=0.0,             # Frequency penalty
    response_mime_type='text/plain',   # Output format
    response_schema=MyTypedDict,       # Schema constraint
    response_json_schema={...},        # Raw JSON schema
    safety_settings=[...],             # Safety configuration
    tools=[...],                       # Available tools
    tool_config=...,                   # Tool behavior config
    cached_content='caches/xxx',       # Use cached context
    thinking_config=...,               # Thinking mode config
    service_tier='standard',           # standard/flex/priority
    http_options=types.HttpOptions(timeout=30000),
)
```

### ThinkingConfig

```python
types.ThinkingConfig(
    thinking_budget=4096,    # Token budget (0 disables, max 24576/32768)
    include_thoughts=True,   # Include thought summaries in output
)
```

### SafetySetting

```python
types.SafetySetting(
    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
)
```

### ToolConfig

```python
types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(
        mode='auto',  # auto, any, none
        allowed_function_names=['func1', 'func2'],
    )
)
```

### AutomaticFunctionCallingConfig

```python
types.AutomaticFunctionCallingConfig(
    disable=False,           # True to disable auto execution
    maximum_remote_calls=10  # Max auto calls (default 10)
)
```

## Content and Part Types

```python
# Create content
types.Content(role='user', parts=[...])
types.UserContent(parts=[...])
types.ModelContent(parts=[...])

# Create parts
types.Part.from_text(text='Hello')
types.Part.from_bytes(data=bytes_data, mime_type='image/png')
types.Part.from_uri(file_uri='gs://...', mime_type='image/jpeg')
types.Part.from_function_call(name='fn', args={'key': 'val'})
types.Part.from_function_response(name='fn', response={'result': ...})
```

## Error Handling

```python
from google.genai import errors

try:
    response = client.models.generate_content(
        model="invalid-model",
        contents="Hello",
    )
except errors.APIError as e:
    print(f"Error code: {e.code}")     # HTTP status code
    print(f"Error message: {e.message}")

# Common error codes:
# 400 - Bad request (invalid parameters)
# 403 - Forbidden (invalid API key)
# 404 - Not found (invalid model name)
# 429 - Rate limit exceeded
# 503 - Service unavailable (Flex tier shedding)
```

## Extra Request Body (Experimental Features)

Access new or experimental backend features:

```python
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Your prompt",
    config=types.GenerateContentConfig(
        tools=[my_function],
        http_options=types.HttpOptions(
            extra_body={
                'tool_config': {
                    'function_calling_config': {
                        'mode': 'COMPOSITIONAL'  # Experimental mode
                    }
                }
            }
        ),
    ),
)
```

## Supported Python Versions

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

## Upcoming Breaking Change

The SDK will introduce a breaking change to Automatic Function Calling (AFC): users will not be able to invoke AFC from direct calls to `Models.generate_content`. Instead, AFC will only be available through the `chats` module.

## Documentation

- PyPI: https://pypi.org/project/google-genai/
- GitHub: https://github.com/googleapis/python-genai
- Official Docs: https://googleapis.github.io/python-genai/
- Gemini API: https://ai.google.dev/gemini-api/docs
- Agent Platform: https://docs.cloud.google.com/gemini-enterprise-agent-platform
