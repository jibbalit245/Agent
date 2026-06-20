# OpenRouter Authentication
> Source: https://openrouter.ai/docs/authentication
> Fetched: 2026-06-20
---

## API Keys

### Generating an API Key

1. Log in at [openrouter.ai](https://openrouter.ai)
2. Navigate to **Keys** → **API Keys**
3. Click **Create Key**
4. Copy the key immediately — it is shown only once

API keys start with `sk-or-v1-`.

### Using an API Key

Pass the key as a Bearer token in the `Authorization` header:

```http
Authorization: Bearer sk-or-v1-your-key-here
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)
```

### Environment Variable Best Practice

Never hardcode API keys. Use environment variables:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

```python
import os
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not set")
```

## Optional Attribution Headers

These headers are optional but recommended:

```http
HTTP-Referer: https://yourapp.com
X-Title: My Application Name
```

- `HTTP-Referer`: Your site URL. Used for analytics and to appear on public leaderboards.
- `X-Title`: Your app's display name. Appears in OpenRouter dashboards and leaderboards.

Neither header is required for authentication — they are informational only.

## OAuth / User API Keys

OpenRouter supports OAuth flows for user-specific API keys (PKCE flow):

### Authorization URL

```
https://openrouter.ai/auth?callback_url=https://yourapp.com/callback&code_challenge=...&code_challenge_method=S256
```

### Token Exchange

```
POST https://openrouter.ai/api/v1/auth/keys
Content-Type: application/json

{
  "code": "auth-code-from-callback",
  "code_verifier": "verifier-string"
}
```

The response contains a user-specific API key (`sk-or-v1-...`) tied to the user's OpenRouter account.

### OAuth Scopes

- Users authenticate with their own OpenRouter account
- Requests billed to their account, not your organization
- Useful for user-pay models where each user has their own credits

## Bring Your Own Key (BYOK)

Route requests using your own provider API keys (Anthropic, OpenAI, etc.):

1. Go to **Settings** → **Integrations** → **API Keys** in the OpenRouter dashboard
2. Add your provider API key (e.g., Anthropic, OpenAI, Google)
3. Route requests to that provider using `provider.order` + `provider.allow_fallbacks: false`

BYOK pricing: **5% routing fee** (vs. standard markup on pass-through costs).

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "provider": {
    "order": ["Anthropic"],
    "allow_fallbacks": false
  }
}
```

## Key Permissions and Usage Limits

- Set per-key credit limits and rate limits in the dashboard
- Monitor per-key usage in **Usage** → **By Key**
- Rotate or revoke keys at any time without affecting other keys

## Free Tier Authentication

Free accounts (no payment method added) can still authenticate:

- Same API key format
- Limited to free models (suffix `:free`, e.g., `meta-llama/llama-3.3-70b-instruct:free`)
- Rate limited: 20 requests/min, 200 requests/day
- Some models require adding credits regardless of `:free` suffix

## Verifying Your Key

```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer sk-or-v1-..."
```

Response:
```json
{
  "data": {
    "label": "My Key",
    "usage": 1234,
    "limit": null,
    "is_free_tier": false,
    "rate_limit": {
      "requests": 200,
      "interval": "10s"
    }
  }
}
```
