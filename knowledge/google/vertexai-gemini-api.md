# Vertex AI Gemini API Reference

> Source: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content sourced from PyPI google-genai package documentation (v2.9.0).
> Fetched: 2026-06-20

## Overview

The Gemini API on Vertex AI allows you to use Google's multimodal generative AI models. Access it via:
- The `google-genai` Python SDK (recommended)
- REST API
- gRPC API

## Installation

```bash
pip install google-genai
```

Optional extras:
- `google-genai[aiohttp]` - Faster async client
- `google-genai[local-tokenizer]` - Local tokenization
- `google-genai[pyopenssl]` - Enhanced SSL/TLS

## Client Initialization

### Vertex AI (Enterprise) - Recommended for Production

```python
from google import genai

client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1'
)
```

### Gemini Developer API (for testing/prototyping)

```python
from google import genai

client = genai.Client(api_key='GEMINI_API_KEY')
```

### Environment Variable Configuration

For Vertex AI:
```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

For Gemini Developer API:
```bash
export GEMINI_API_KEY='your-api-key'
# or
export GOOGLE_API_KEY='your-api-key'
```

Then initialize without parameters:
```python
from google import genai
client = genai.Client()
```

## API Version Selection

```python
from google import genai
from google.genai import types

# Vertex AI with specific API version
client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1',
    http_options=types.HttpOptions(api_version='v1')  # or 'v1beta'
)

# Gemini Developer API with alpha features
client = genai.Client(
    api_key='GEMINI_API_KEY',
    http_options=types.HttpOptions(api_version='v1alpha')
)
```

## Content Generation

### Basic Text Generation

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)
print(response.text)
```

### With Configuration

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Write a haiku about mountains.',
    config=types.GenerateContentConfig(
        system_instruction='You are a poet who specializes in haiku.',
        max_output_tokens=100,
        temperature=0.7,
        top_p=0.95,
        top_k=40,
    ),
)
print(response.text)
```

### GenerateContentConfig Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `system_instruction` | str | Instructions for model behavior |
| `max_output_tokens` | int | Maximum tokens in response |
| `temperature` | float | Randomness (0.0=deterministic, 1.0=creative) |
| `top_p` | float | Nucleus sampling (0.0-1.0) |
| `top_k` | int | Top-k sampling |
| `response_mime_type` | str | e.g., `'application/json'`, `'text/plain'` |
| `response_json_schema` | dict | JSON schema for structured output |
| `safety_settings` | list | Content safety thresholds |
| `tools` | list | Functions/tools the model can call |
| `tool_config` | ToolConfig | Tool calling configuration |
| `cached_content` | str | Name of cached content to use |
| `response_modalities` | list | e.g., `['TEXT']`, `['IMAGE']` |
| `automatic_function_calling` | AutomaticFunctionCallingConfig | AFC settings |

## Multimodal Inputs

### Image from Cloud Storage

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        'What is in this image?',
        types.Part.from_uri(
            file_uri='gs://bucket/image.jpg',
            mime_type='image/jpeg',
        ),
    ],
)
print(response.text)
```

### Image from Local File

```python
from google.genai import types

with open('image.jpg', 'rb') as f:
    image_bytes = f.read()

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        'Describe this image.',
        types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
    ],
)
print(response.text)
```

### Content Structure

The SDK converts various input formats to `list[types.Content]`:

```python
from google.genai import types

# Using Content objects explicitly
contents = [
    types.Content(
        role='user',
        parts=[
            types.Part.from_text('What is in this image?'),
            types.Part.from_uri(
                file_uri='gs://bucket/image.jpg',
                mime_type='image/jpeg',
            ),
        ]
    )
]
```

## Streaming

### Synchronous Streaming

```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Asynchronous Streaming

```python
async for chunk in await client.aio.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Async Non-Streaming

```python
response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
)
print(response.text)
```

## Function Calling (Tool Use)

### Automatic (Python Functions)

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)
print(response.text)
```

### Manual Function Declaration

```python
from google.genai import types

function = types.FunctionDeclaration(
    name='get_current_weather',
    description='Get the current weather in a given location',
    parameters_json_schema={
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The city and state, e.g. San Francisco, CA',
            }
        },
        'required': ['location'],
    },
)

tool = types.Tool(function_declarations=[function])

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[tool]),
)

# Get the function call
print(response.function_calls[0])
```

### Disabling Automatic Function Calling

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_current_weather],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    ),
)
function_calls = response.function_calls
```

### Processing Function Responses

```python
from google.genai import types

# Build the conversation
user_content = types.Content(
    role='user',
    parts=[types.Part.from_text('What is the weather like in Boston?')],
)
function_call_part = response.function_calls[0]
function_call_content = response.candidates[0].content

# Execute the function
try:
    result = get_current_weather(**function_call_part.function_call.args)
    function_response = {'result': result}
except Exception as e:
    function_response = {'error': str(e)}

# Send function response back
function_response_part = types.Part.from_function_response(
    name=function_call_part.name,
    response=function_response,
)
function_response_content = types.Content(
    role='tool', 
    parts=[function_response_part]
)

final_response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[user_content, function_call_content, function_response_content],
    config=types.GenerateContentConfig(tools=[tool]),
)
print(final_response.text)
```

### Tool Config Modes

```python
from google.genai import types

# Force function call with ANY mode
config = types.GenerateContentConfig(
    tools=[get_current_weather],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode='ANY')
    ),
)

# Limit remote calls
config = types.GenerateContentConfig(
    tools=[get_current_weather],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        maximum_remote_calls=2
    ),
)
```

### Model Context Protocol (MCP) - Experimental

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

client = genai.Client()
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@philschmid/weather-mcp"],
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents="What is the weather in London today?",
                config=genai.types.GenerateContentConfig(tools=[session]),
            )
            print(response.text)
```

## Structured Output (JSON)

### With JSON Schema

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me a random user profile.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_json_schema={
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'age': {'type': 'integer'},
                'email': {'type': 'string'},
            },
            'required': ['username', 'age'],
        },
    ),
)
print(response.text)
```

### With Pydantic Models

```python
from pydantic import BaseModel
from google.genai import types

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_json_schema=CountryInfo.model_json_schema(),
    ),
)
print(response.text)
```

## Safety Settings

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt here.',
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_ONLY_HIGH',
            ),
            types.SafetySetting(
                category='HARM_CATEGORY_DANGEROUS_CONTENT',
                threshold='BLOCK_MEDIUM_AND_ABOVE',
            ),
        ]
    ),
)
```

Safety categories:
- `HARM_CATEGORY_HATE_SPEECH`
- `HARM_CATEGORY_DANGEROUS_CONTENT`
- `HARM_CATEGORY_SEXUALLY_EXPLICIT`
- `HARM_CATEGORY_HARASSMENT`

Safety thresholds:
- `BLOCK_NONE`
- `BLOCK_ONLY_HIGH`
- `BLOCK_MEDIUM_AND_ABOVE`
- `BLOCK_LOW_AND_ABOVE`

## Chat / Multi-Turn Conversations

### Synchronous Chat

```python
chat = client.chats.create(model='gemini-2.5-flash')
response = chat.send_message('Tell me a story.')
print(response.text)

response = chat.send_message('Summarize in 1 sentence.')
print(response.text)
```

### Streaming Chat

```python
chat = client.chats.create(model='gemini-2.5-flash')
for chunk in chat.send_message_stream('Tell me a story.'):
    print(chunk.text, end='')
```

### Async Chat

```python
chat = client.aio.chats.create(model='gemini-2.5-flash')
response = await chat.send_message('Tell me a story.')
print(response.text)
```

## Token Counting

```python
# Count tokens
response = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?',
)
print(response)

# Compute tokens (Vertex AI only - returns token IDs)
response = client.models.compute_tokens(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?',
)
print(response)

# Local tokenization (no API call)
from google.genai import local_tokenizer
tokenizer = local_tokenizer.LocalTokenizer(model_name='gemini-2.5-flash')
result = tokenizer.count_tokens("What is your name?")
```

## Embeddings

```python
from google.genai import types

# Single embedding
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents='Why is the sky blue?',
)
print(response)

# Multiple embeddings with custom dimensionality
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=['Why is the sky blue?', 'What is your age?'],
    config=types.EmbedContentConfig(output_dimensionality=10),
)
print(response)
```

## Content Caching

```python
from google.genai import types

# Create cache
cached_content = client.caches.create(
    model='gemini-2.5-flash',
    config=types.CreateCachedContentConfig(
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_uri(
                        file_uri='gs://bucket/document.pdf',
                        mime_type='application/pdf'
                    ),
                ],
            )
        ],
        system_instruction='You are a document assistant.',
        display_name='document_cache',
        ttl='3600s',  # 1 hour TTL
    ),
)

# Use cached content
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Summarize the document',
    config=types.GenerateContentConfig(
        cached_content=cached_content.name,
    ),
)
print(response.text)

# Get cache info
cache_info = client.caches.get(name=cached_content.name)
```

## File Management (Developer API Only)

```python
# Upload file
file = client.files.upload(file='document.pdf')

# Use in generation
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=['Summarize this document.', file]
)

# Get file info
file_info = client.files.get(name=file.name)

# Delete file
client.files.delete(name=file.name)
```

## Image Generation

```python
from google.genai import types

response = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt='A sunset over the Golden Gate Bridge',
    config=types.GenerateImagesConfig(
        number_of_images=1,
        include_rai_reason=True,
        output_mime_type='image/jpeg',
    ),
)
response.generated_images[0].image.show()
```

## Video Generation (Veo)

```python
from google.genai import types
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

# Poll for completion
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

## Batch Prediction

```python
from google.genai import types
import time

# Create batch job (Vertex AI - BigQuery source)
job = client.batches.create(
    model='gemini-2.5-flash',
    src='bq://my-project.my-dataset.my-table',
)

# Poll for completion
completed_states = {'JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED', 'JOB_STATE_CANCELLED'}
while job.state not in completed_states:
    print(job.state)
    job = client.batches.get(name=job.name)
    time.sleep(30)

# Delete batch job
client.batches.delete(name=job.name)
```

## Model Tuning

```python
from google.genai import types
import time

# Create tuning job
tuning_job = client.tunings.tune(
    base_model='gemini-2.0-flash',
    training_dataset=types.TuningDataset(
        gcs_uri='gs://your-bucket/training-data.jsonl',
    ),
    config=types.CreateTuningJobConfig(
        epoch_count=1,
        tuned_model_display_name='my-tuned-model'
    ),
)

# Wait for completion
completed_states = {'JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED', 'JOB_STATE_CANCELLED'}
while tuning_job.state not in completed_states:
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(10)

# Use tuned model
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents='Your prompt here.',
)
print(response.text)
```

## Model Listing

```python
# List available models
for model in client.models.list():
    print(model)

# Paginated listing
pager = client.models.list(config={'page_size': 10})
print(pager[0])
pager.next_page()
```

## Error Handling

```python
from google.genai import errors

try:
    client.models.generate_content(
        model="invalid-model-name",
        contents="Hello",
    )
except errors.APIError as e:
    print(e.code)     # HTTP status code, e.g. 404
    print(e.message)  # Error description
```

## Context Management

```python
# Synchronous context manager
with genai.Client(vertexai=True, project='proj', location='us-central1') as client:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )

# Async context manager
async with genai.Client(vertexai=True, project='proj', location='us-central1').aio as client:
    response = await client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )
```

## Gemini Model IDs (on Vertex AI)

| Model | ID | Context Window | Key Features |
|-------|----| --------------|--------------|
| Gemini 2.5 Pro | `gemini-2.5-pro` | 1M tokens | Best reasoning, coding |
| Gemini 2.5 Flash | `gemini-2.5-flash` | 1M tokens | Fast, cost-effective |
| Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` | 1M tokens | Lowest latency/cost |
| Gemini 2.0 Flash | `gemini-2.0-flash` | 1M tokens | Multimodal, tool use |
| Gemini 2.0 Flash Lite | `gemini-2.0-flash-lite` | 1M tokens | Ultra-low cost |
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | 1M+ tokens | Latest generation |
| Gemini 3.5 Flash | `gemini-3.5-flash` | 1M+ tokens | Latest Flash model |
| Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite` | 1M+ tokens | Latest Lite model |

## REST API (Direct)

For Vertex AI, the base endpoint is:
```
https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent
```

Example with curl:
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/MY_PROJECT/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Why is the sky blue?"}]
    }]
  }'
```

## Related Resources

- Python SDK: https://github.com/googleapis/python-genai
- PyPI: https://pypi.org/project/google-genai/
- Documentation: https://googleapis.github.io/python-genai/
- Vertex AI Docs: https://cloud.google.com/vertex-ai/generative-ai/docs
