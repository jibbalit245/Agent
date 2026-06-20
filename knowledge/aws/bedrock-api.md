# Bedrock API — invoke_model vs converse, Streaming, Model IDs
> Source: https://docs.aws.amazon.com/bedrock/latest/userguide/inference-api.html, https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html, https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html
> Fetched: 2026-06-20

## Two Data Plane APIs

Amazon Bedrock Runtime offers two ways to invoke models:

| API | Best For | Portability |
|-----|----------|-------------|
| `invoke_model` | Model-specific payloads, full control over native format | Low — payload format differs per model |
| `converse` / `converse_stream` | Chat/conversation use cases | High — single unified format across all models |

Use `converse` for new projects unless you need model-specific features not exposed through the unified API.

## Client Setup

```python
import boto3

# Data plane — always use "bedrock-runtime" for inference
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Management plane — use "bedrock" for listing models, provisioned throughput, etc.
mgmt_client = boto3.client("bedrock", region_name="us-east-1")
```

## Converse API (Recommended)

The `converse` API provides a **unified interface** that works across all Bedrock models supporting the Messages format. Write code once; swap models by changing `modelId`.

### Basic Example

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    messages=[
        {
            "role": "user",
            "content": [{"text": "What is the capital of France?"}]
        }
    ],
    inferenceConfig={
        "maxTokens": 1024,
        "temperature": 0.7,
        "topP": 0.9,
    },
    system=[{"text": "You are a helpful assistant."}]
)

output = response["output"]["message"]["content"][0]["text"]
print(output)
```

### Streaming with converse_stream

```python
response = client.converse_stream(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    messages=[
        {"role": "user", "content": [{"text": "Write a haiku about clouds."}]}
    ],
    inferenceConfig={"maxTokens": 256}
)

# Iterate over the stream
for event in response["stream"]:
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"]["delta"]
        if "text" in delta:
            print(delta["text"], end="", flush=True)

# Required permissions: bedrock:InvokeModelWithResponseStream
```

### Multi-turn Conversation

```python
messages = []

def chat(user_input):
    messages.append({
        "role": "user",
        "content": [{"text": user_input}]
    })
    response = client.converse(
        modelId="anthropic.claude-sonnet-4-6-v1:0",
        messages=messages,
        inferenceConfig={"maxTokens": 2048}
    )
    assistant_msg = response["output"]["message"]
    messages.append(assistant_msg)  # Append to maintain history
    return assistant_msg["content"][0]["text"]
```

## invoke_model API (Model-Native Format)

`invoke_model` sends raw JSON in the model's native format. Useful for models not supporting the Converse API, or for model-specific features.

### Anthropic Claude (native format)

```python
import json

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
})

response = client.invoke_model(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    body=body,
    contentType="application/json",
    accept="application/json"
)

result = json.loads(response["body"].read())
print(result["content"][0]["text"])
```

### Amazon Titan (native format)

```python
body = json.dumps({
    "inputText": "Explain quantum computing",
    "textGenerationConfig": {
        "maxTokenCount": 512,
        "temperature": 0.5,
        "topP": 0.9
    }
})

response = client.invoke_model(
    modelId="amazon.titan-text-premier-v1:0",
    body=body,
    contentType="application/json",
    accept="application/json"
)
```

### Streaming with invoke_model_with_response_stream

```python
response = client.invoke_model_with_response_stream(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Tell me a story"}]
    }),
    contentType="application/json"
)

for event in response["body"]:
    chunk = json.loads(event["chunk"]["bytes"])
    if chunk.get("type") == "content_block_delta":
        print(chunk["delta"].get("text", ""), end="", flush=True)
```

## Model IDs

### Format

Standard format: `{provider}.{model-name}-{date}-v{N}:{minor}`

Example: `anthropic.claude-3-5-sonnet-20241022-v2:0`

Cross-region inference format: `{region-prefix}.{provider}.{model-name}`

Example: `us.anthropic.claude-sonnet-4-6-v1:0` or `global.anthropic.claude-sonnet-4-6-v1:0`

### Common Model IDs (2026)

**Anthropic Claude:**
```
anthropic.claude-opus-4-6-v1:0
anthropic.claude-sonnet-4-6-v1:0
anthropic.claude-haiku-4-5-20251001-v1:0
anthropic.claude-3-5-sonnet-20241022-v2:0
anthropic.claude-3-haiku-20240307-v1:0
```

**Cross-region (US routing):**
```
us.anthropic.claude-sonnet-4-6-v1:0
us.anthropic.claude-opus-4-6-v1:0
```

**Global (automatic cross-region):**
```
global.anthropic.claude-sonnet-4-5-20250929-v1:0
global.anthropic.claude-haiku-4-5-20251001-v1:0
global.anthropic.claude-opus-4-6-v1
global.anthropic.claude-sonnet-4-6
```

**Amazon Nova:**
```
amazon.nova-pro-v1:0
amazon.nova-lite-v1:0
amazon.nova-micro-v1:0
```

**Amazon Titan:**
```
amazon.titan-text-premier-v1:0
amazon.titan-text-express-v1
amazon.titan-embed-text-v2:0
```

**Meta Llama:**
```
meta.llama3-70b-instruct-v1:0
meta.llama3-8b-instruct-v1:0
meta.llama3-3-70b-instruct-v1:0
```

**Mistral:**
```
mistral.mistral-large-2402-v1:0
mistral.mixtral-8x7b-instruct-v0:1
```

**Cohere:**
```
cohere.command-r-plus-v1:0
cohere.command-r-v1:0
```

**AI21:**
```
ai21.jamba-1-5-large-v1:0
ai21.jamba-instruct-v1:0
```

### Listing Available Models

```python
mgmt = boto3.client("bedrock", region_name="us-east-1")
models = mgmt.list_foundation_models()
for m in models["modelSummaries"]:
    print(m["modelId"], m["providerName"])
```

## Bedrock Runtime vs Bedrock (Management)

| boto3 client | API calls |
|-------------|-----------|
| `boto3.client("bedrock-runtime")` | `invoke_model`, `invoke_model_with_response_stream`, `converse`, `converse_stream` |
| `boto3.client("bedrock")` | `list_foundation_models`, `get_foundation_model`, `create_provisioned_model_throughput`, `list_provisioned_model_throughputs` |

## Response Structure (Converse API)

```python
{
    "ResponseMetadata": {...},
    "output": {
        "message": {
            "role": "assistant",
            "content": [{"text": "The response text..."}]
        }
    },
    "stopReason": "end_turn",  # or "max_tokens", "stop_sequence"
    "usage": {
        "inputTokens": 42,
        "outputTokens": 150,
        "totalTokens": 192
    },
    "metrics": {
        "latencyMs": 1234
    }
}
```
