# OpenAI API Authentication & Quickstart
> Source: https://platform.openai.com/docs/quickstart
> Fetched: 2026-06-20

## Getting an API Key

1. Sign in or create an account at https://platform.openai.com
2. Navigate to **API Keys** in the dashboard (https://platform.openai.com/api-keys)
3. Click **Create new secret key**
4. Copy the key immediately — it will not be shown again
5. Add billing information to activate paid access

## Environment Setup

Set your API key as an environment variable (never hardcode it in source code):

```bash
# Linux / macOS
export OPENAI_API_KEY="sk-proj-..."

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-proj-..."

# Windows CMD
set OPENAI_API_KEY=sk-proj-...
```

Store in `.env` file (add to `.gitignore`):
```
OPENAI_API_KEY=sk-proj-...
```

Load with Python:
```python
from openai import OpenAI
import os

client = OpenAI()  # automatically reads OPENAI_API_KEY from environment
# or explicitly:
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
```

## Base URL

```
https://api.openai.com/v1/
```

All API endpoints are relative to this base URL.

## Authentication Headers

All requests require the `Authorization` header with a Bearer token:

```http
Authorization: Bearer sk-proj-YOUR_API_KEY
Content-Type: application/json
```

For multi-org accounts, optionally specify organization and project:

```http
Authorization: Bearer sk-proj-YOUR_API_KEY
OpenAI-Organization: org-ORGANIZATION_ID
OpenAI-Project: proj-PROJECT_ID
```

## Organization ID & Project ID

- **Organization ID**: Found in your organization settings at https://platform.openai.com/account/organization
  - Format: `org-XXXXXXXXXXXXXXXX`
  - Used when you belong to multiple organizations
- **Project ID**: Found in project settings
  - Format: `proj-XXXXXXXXXXXXXXXX`
  - Used for project-level rate limit tracking

## Workload Identity Federation (Advanced)

The API also accepts short-lived access tokens created via workload identity federation — an alternative to long-lived API keys for production environments. Provide via the same `Authorization: Bearer` header.

## Python SDK Quickstart

Install:
```bash
pip install openai
```

Basic usage:
```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ]
)

print(response.choices[0].message.content)
```

## Node.js / TypeScript SDK Quickstart

Install:
```bash
npm install openai
```

```typescript
import OpenAI from "openai";

const client = new OpenAI(); // reads OPENAI_API_KEY from env

const response = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Hello, world!" }],
});

console.log(response.choices[0].message.content);
```

## Raw HTTP Request

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Rate Limit Tiers

Usage tiers are automatically assigned based on spending history and account age. Rate limits increase as you move up tiers.

| Tier | Requirements | Notes |
|------|-------------|-------|
| **Free** | New account with $0 spend | Very low limits |
| **Tier 1** | $5+ paid | Entry-level paid access |
| **Tier 2** | $50+ paid in last 30 days | Moderate limits |
| **Tier 3** | $100+ paid in last 30 days | Higher limits |
| **Tier 4** | $250+ paid in last 30 days | High limits |
| **Tier 5** | $1,000+ paid in last 30 days | Highest standard limits |

Rate limits are set at the **organization level** and **project level**, not per user. Tier upgrades happen automatically when spend thresholds are met.

View your current limits at: https://platform.openai.com/account/limits

## Security Best Practices

- Never commit API keys to source control
- Use environment variables or a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Load keys server-side only — never expose in client-side browser code
- Rotate keys regularly
- Use project-scoped keys to limit blast radius
- Monitor usage at https://platform.openai.com/usage

## Sources
- [API Overview | OpenAI API Reference](https://developers.openai.com/api/reference/overview)
- [Rate limits | OpenAI API](https://developers.openai.com/api/docs/guides/rate-limits)
- [Production best practices | OpenAI API](https://platform.openai.com/docs/guides/production-best-practices)
