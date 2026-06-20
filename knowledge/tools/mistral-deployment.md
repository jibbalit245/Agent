# Mistral AI Cloud Deployment

> **Fetch status:** HTTP 403 Forbidden from https://docs.mistral.ai/deployment/cloud/overview/ — content below is from model training data (knowledge cutoff August 2025).

## Overview

Mistral AI models are available through multiple deployment channels beyond La Plateforme (api.mistral.ai):

1. **La Plateforme** — Mistral's own hosted API
2. **Azure AI Foundry (formerly Azure AI Studio)**
3. **Amazon Bedrock**
4. **Google Cloud Vertex AI**
5. **Self-hosted** — Open-weight models on your own infrastructure

---

## La Plateforme (api.mistral.ai)

The primary API offering from Mistral AI.

- **URL:** `https://api.mistral.ai/v1`
- **All models available:** Large, Small, Nemo, Codestral, Pixtral, Embed
- **Fine-tuning:** Supported
- **Pricing:** Pay-per-token (see mistral-pricing.md)

```python
from mistralai import Mistral

client = Mistral(api_key="your_mistral_api_key")
```

---

## Azure AI Foundry / Azure AI Studio

Deploy Mistral models through Microsoft Azure.

### Available Models on Azure

- Mistral Large
- Mistral Small
- Mistral Nemo
- Pixtral Large
- Mixtral 8x7B
- Mixtral 8x22B
- Mistral 7B

### Setup on Azure

1. Go to [Azure AI Studio](https://ai.azure.com/)
2. Navigate to **Model catalog**
3. Search for "Mistral"
4. Click **Deploy** → Choose serverless (pay-per-token) or managed compute

### Azure Endpoint

After deployment, you get an endpoint like:
```
https://your-endpoint-name.eastus.models.ai.azure.com
```

### Python with Azure

```python
# Option 1: Using MistralAI SDK with Azure endpoint
from mistralai import Mistral

client = Mistral(
    api_key="your_azure_api_key",
    server_url="https://your-endpoint.eastus.models.ai.azure.com",
)

response = client.chat.complete(
    model="mistral-large",  # Model name may differ on Azure
    messages=[{"role": "user", "content": "Hello!"}],
)
```

```python
# Option 2: Using Azure AI Inference SDK
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint="https://your-endpoint.eastus.models.ai.azure.com",
    credential=AzureKeyCredential("your_azure_api_key"),
)

from azure.ai.inference.models import SystemMessage, UserMessage

response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Hello!"),
    ],
    model="mistral-large",
)
print(response.choices[0].message.content)
```

```python
# Option 3: OpenAI SDK with Azure endpoint
from openai import OpenAI

client = OpenAI(
    base_url="https://your-endpoint.eastus.models.ai.azure.com",
    api_key="your_azure_api_key",
)
```

---

## Amazon Bedrock

Access Mistral models through AWS Bedrock.

### Available Models on Bedrock

| Mistral Model | Bedrock Model ID |
|---|---|
| Mistral 7B Instruct | `mistral.mistral-7b-instruct-v0:2` |
| Mixtral 8x7B | `mistral.mixtral-8x7b-instruct-v0:1` |
| Mistral Large | `mistral.mistral-large-2402-v1:0` |
| Mistral Large 2 | `mistral.mistral-large-2407-v1:0` |
| Mistral Small | `mistral.mistral-small-2402-v1:0` |

### Python with Bedrock

```python
import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

payload = {
    "prompt": "<s>[INST] Hello! [/INST]",
    "max_tokens": 512,
    "temperature": 0.7,
}

response = bedrock.invoke_model(
    modelId="mistral.mistral-7b-instruct-v0:2",
    body=json.dumps(payload),
)

result = json.loads(response["body"].read())
print(result["outputs"][0]["text"])
```

### Using Bedrock with Chat Format (Mistral Large on Bedrock)

```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

messages = [
    {"role": "user", "content": "What is machine learning?"}
]

payload = {
    "messages": messages,
    "max_tokens": 512,
    "temperature": 0.7,
}

response = bedrock.invoke_model(
    modelId="mistral.mistral-large-2407-v1:0",
    body=json.dumps(payload),
    contentType="application/json",
    accept="application/json",
)

result = json.loads(response["body"].read())
print(result["choices"][0]["message"]["content"])
```

### LangChain with Bedrock

```python
from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id="mistral.mistral-large-2407-v1:0",
    region_name="us-east-1",
)

response = llm.invoke("What is quantum computing?")
print(response.content)
```

---

## Google Cloud Vertex AI

Deploy Mistral through Google's Vertex AI Model Garden.

### Available Models on Vertex

- Mistral Large
- Mistral Nemo
- Codestral

### Setup

1. Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. Search for "Mistral"
3. Click **Deploy**
4. Choose an endpoint

### Python with Vertex

```python
from mistralai_gcp import MistralGoogleCloud
from google.auth.credentials import AnonymousCredentials

client = MistralGoogleCloud(project_id="your-project-id", region="us-central1")

response = client.chat.complete(
    model="mistral-large@latest",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

```python
# Via direct REST call with OAuth
import requests
import google.auth
import google.auth.transport.requests

credentials, project = google.auth.default()
credentials.refresh(google.auth.transport.requests.Request())

endpoint = "https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/mistralai/models/mistral-large@latest:rawPredict"

response = requests.post(
    endpoint,
    headers={"Authorization": f"Bearer {credentials.token}"},
    json={
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": "Hello!"}],
    }
)
```

---

## Self-Hosting Open-Weight Models

### HuggingFace Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "mistralai/Mistral-7B-Instruct-v0.3"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

messages = [{"role": "user", "content": "Hello!"}]

# Apply chat template
inputs = tokenizer.apply_chat_template(
    messages,
    return_tensors="pt",
    return_dict=True,
).to("cuda")

outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### vLLM (Production Serving)

```bash
# Install vLLM
pip install vllm

# Serve Mistral 7B with OpenAI-compatible API
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.3 \
  --dtype bfloat16 \
  --port 8000

# Or Mixtral 8x7B (requires multiple GPUs)
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mixtral-8x7B-Instruct-v0.1 \
  --tensor-parallel-size 4 \
  --port 8000
```

Connect to self-hosted vLLM:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",
)

response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull and run Mistral
ollama pull mistral
ollama run mistral "Hello, how are you?"

# Serve as API
ollama serve  # Runs on localhost:11434
```

---

## Choosing a Deployment Option

| Factor | La Plateforme | Azure/AWS/GCP | Self-Hosted |
|---|---|---|---|
| Setup complexity | Low | Medium | High |
| Data residency | Mistral (EU) | Cloud provider | Your infra |
| Compliance | SOC2 | SOC2/HIPAA/etc | You control |
| Pricing | Per token | Per token or compute | GPU cost |
| Latest models | Always | Lagged | Manual update |
| Fine-tuning | Yes | Limited | Yes (manual) |
| SLA | Mistral SLA | Cloud provider SLA | You handle |
| Open models | No | No | Yes |
