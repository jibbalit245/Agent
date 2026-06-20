# Modal Secrets

> Source: https://modal.com/docs/guide/secrets
> Note: Page returned HTTP 403 during crawl; content compiled from search results and official sources.

## Overview

Modal Secrets are a secure way to inject sensitive information (API keys, passwords, tokens) into your Modal functions as environment variables. Secrets are encrypted at rest and only decrypted at container startup.

## Creating Secrets

### Via Dashboard (Recommended)

1. Go to https://modal.com/secrets
2. Click "New Secret"
3. Choose a template (OpenAI, HuggingFace, AWS, etc.) or "Custom"
4. Enter key-value pairs
5. Give the secret a name (e.g., `openai-key`)

### Via CLI

```bash
modal secret create my-secret MY_API_KEY=sk-abc123 OTHER_KEY=value
```

### Via Python (for testing/CI)

```python
import modal

# Create a temporary secret from a dict
secret = modal.Secret.from_dict({
    "MY_API_KEY": "sk-abc123",
    "OTHER_KEY": "value"
})
```

## Using Secrets in Functions

### Basic Usage

```python
import modal
import os

app = modal.App("my-app")

@app.function(secrets=[modal.Secret.from_name("my-secret")])
def my_function():
    api_key = os.environ["MY_API_KEY"]
    # Use the API key
    return api_key[:5] + "..."  # Don't log full key!
```

### Multiple Secrets

```python
@app.function(
    secrets=[
        modal.Secret.from_name("openai-key"),
        modal.Secret.from_name("database-credentials"),
        modal.Secret.from_name("aws-credentials"),
    ]
)
def multi_secret_function():
    import os
    
    openai_key = os.environ["OPENAI_API_KEY"]
    db_host = os.environ["DATABASE_HOST"]
    aws_key = os.environ["AWS_ACCESS_KEY_ID"]
```

> **Note:** If secrets have conflicting key names, later secrets in the list override earlier ones.

### Secrets with Required Keys Validation

```python
@app.function(
    secrets=[
        modal.Secret.from_name(
            "postgres-secret",
            required_keys=["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"]
        )
    ]
)
def database_function():
    import os
    host = os.environ["PGHOST"]
    # Will raise an error at runtime if any required key is missing
```

## Secret Methods

### `modal.Secret.from_name()`

```python
# Reference a secret stored in Modal
secret = modal.Secret.from_name("my-secret-name")

# With required keys validation
secret = modal.Secret.from_name(
    "my-secret",
    required_keys=["KEY1", "KEY2"]
)
```

### `modal.Secret.from_dict()`

```python
# Create a secret from a Python dictionary (useful for testing)
secret = modal.Secret.from_dict({
    "API_KEY": "my-key",
    "SECRET": "my-secret-value"
})
```

### `modal.Secret.from_local_environ()`

```python
# Pull specific keys from your local environment
secret = modal.Secret.from_local_environ(["OPENAI_API_KEY", "ANTHROPIC_API_KEY"])
```

### `modal.Secret.from_dotenv()`

```python
# Load from a .env file
secret = modal.Secret.from_dotenv()           # Loads .env in current directory
secret = modal.Secret.from_dotenv("/path/to/.env")  # Specific path
```

## Common Secret Templates

Modal has templates for popular services:

| Template | Keys Injected |
|----------|--------------|
| OpenAI | `OPENAI_API_KEY` |
| HuggingFace | `HUGGING_FACE_HUB_TOKEN` |
| Anthropic | `ANTHROPIC_API_KEY` |
| AWS | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` |
| GitHub | `GITHUB_TOKEN` |
| PostgreSQL | `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` |
| Stripe | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` |
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` |
| Slack | `SLACK_BOT_TOKEN` |
| Custom | Any key-value pairs |

## Real-World Examples

### OpenAI Integration

```python
import modal
import os

app = modal.App("openai-app")

image = modal.Image.debian_slim().pip_install("openai")

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-key")]
)
def call_openai(prompt: str) -> str:
    from openai import OpenAI
    
    # OPENAI_API_KEY is automatically available via environment
    client = OpenAI()  # Uses OPENAI_API_KEY from env
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### HuggingFace with Private Models

```python
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("huggingface-token")]
)
def load_private_model():
    from transformers import AutoModel
    import os
    
    # HF_TOKEN is set automatically
    model = AutoModel.from_pretrained(
        "meta-llama/Llama-2-7b",
        token=os.environ["HF_TOKEN"]
    )
    return model
```

### Database Connection

```python
@app.function(
    secrets=[modal.Secret.from_name("postgres-creds")]
)
def query_database(sql: str):
    import psycopg2
    import os
    
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ["PGPORT"]),
        database=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"]
    )
    
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
```

### AWS S3 Access

```python
@app.function(
    secrets=[modal.Secret.from_name("aws-credentials")]
)
def upload_to_s3(local_path: str, bucket: str, key: str):
    import boto3
    # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
    # are automatically set from the secret
    
    s3 = boto3.client("s3")
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"
```

## Managing Secrets

### List Secrets

```bash
modal secret list
```

### Delete a Secret

```bash
modal secret delete my-secret-name
```

### Update a Secret

Update via the dashboard or delete and recreate via CLI.

## Security Best Practices

1. **Never log secret values** - Only log the presence, not the value
2. **Use required_keys** - Validate expected keys at deploy time
3. **Separate secrets by service** - Don't put all keys in one secret
4. **Rotate regularly** - Update secrets periodically
5. **Least privilege** - Only include keys your function actually needs
6. **Use templates** - Modal's templates enforce naming conventions

```python
# Good: validate required keys
secret = modal.Secret.from_name("db-creds", required_keys=["DB_URL"])

# Bad: no validation, silent failure if key missing
secret = modal.Secret.from_name("db-creds")
```

## Secrets in Classes

```python
@app.cls(
    secrets=[modal.Secret.from_name("api-keys")]
)
class MyService:
    @modal.enter()
    def setup(self):
        import os
        self.api_key = os.environ["API_KEY"]
    
    @modal.method()
    def call_api(self, data):
        # self.api_key is available from setup
        pass
```
