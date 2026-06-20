# Replicate - Overview

> Source: https://replicate.com/docs
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## What is Replicate?

Replicate is a cloud platform for running machine learning models via a simple API. It hosts 50,000+ open-source models that can be run with a single API call, without managing infrastructure. You can also deploy and host your own models.

## Key Features

- **Run any model via API** - Single unified API to run image generation, language, audio, and video models
- **Pay-as-you-go billing** - Only pay for compute time used; no idle charges for serverless runs
- **50,000+ models** - Access to a vast library of open-source models
- **Multiple client libraries** - Python, Node.js, and HTTP API support
- **Webhooks** - Async prediction updates via webhook callbacks
- **Fine-tuning** - Train custom versions of existing models
- **Deployments** - Deploy models with persistent instances for low-latency use

## Quick Start

### Install the Python Client

```bash
pip install replicate
```

### Set API Token

```bash
export REPLICATE_API_TOKEN=r8_your_token_here
```

### Run a Model

```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "an astronaut riding a rainbow unicorn"}
)

for index, item in enumerate(output):
    with open(f"output_{index}.webp", "wb") as f:
        f.write(item.read())
```

## Core Concepts

### Models
A model is a machine learning algorithm, packaged with code and weights. Models on Replicate have owners (users or organizations), names, and versions.

### Predictions
A prediction is a single run of a model. You provide inputs, the model runs, and you get outputs back. Predictions can be synchronous (wait for result) or asynchronous (poll for result).

### Versions
Each model can have multiple versions. A version is an immutable snapshot of a model at a point in time, identified by a SHA256 hash.

### Hardware
Replicate runs models on different hardware tiers. The hardware used affects both speed and cost.

## API Base URL

```
https://api.replicate.com/v1/
```

## Authentication

All API requests require a Bearer token:

```
Authorization: Bearer r8_your_api_token
```

Tokens start with `r8_` and are 40 characters long. Create tokens at: https://replicate.com/account/api-tokens

## Available Client Libraries

| Language | Package | Install |
|----------|---------|---------|
| Python | `replicate` | `pip install replicate` |
| Node.js | `replicate` | `npm install replicate` |
| HTTP | - | Use any HTTP client |

## Key Documentation Sections

- **Get Started** - Python quickstart, fine-tuning guide
- **Topics** - Predictions, models, webhooks, billing, deployments, fine-tuning
- **Reference** - HTTP API, how Replicate works
- **Guides** - Specific use case guides

## How Replicate Works

1. You send a POST request to create a prediction
2. Replicate queues the prediction and finds available hardware
3. The model runs and generates output
4. You retrieve the output (synchronously or by polling)
5. Billing is calculated based on compute time used

## Rate Limits

| Endpoint | Rate Limit |
|----------|-----------|
| Create prediction | 600 requests/minute |
| All other endpoints | 3000 requests/minute |
