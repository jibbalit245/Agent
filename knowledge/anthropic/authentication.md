# Anthropic API Authentication & Quickstart
> Source: https://docs.anthropic.com/en/api/getting-started
> Fetched: 2026-06-20

## Getting an API Key

1. Go to [https://console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys** in the dashboard
4. Click **Create Key**
5. Copy and store the key securely — it won't be shown again

## Setting the API Key

### Environment Variable (Recommended)

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) to persist across sessions.

### Conflict Warning

If both `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` are set, the SDK sends both and the API **rejects the request**. Unset one of them.

### In Code (Python)

```python
import anthropic

# Reads ANTHROPIC_API_KEY env var automatically
client = anthropic.Anthropic()

# Or pass explicitly
client = anthropic.Anthropic(api_key="sk-ant-api03-...")
```

### In Code (Node.js)

```javascript
import Anthropic from "@anthropic-ai/sdk";

// Reads ANTHROPIC_API_KEY env var automatically
const client = new Anthropic();

// Or pass explicitly
const client = new Anthropic({ apiKey: "sk-ant-api03-..." });
```

## Base URL

```
https://api.anthropic.com
```

Main endpoint: `POST https://api.anthropic.com/v1/messages`

## Authentication Header

The API uses `x-api-key` header (the SDK handles this automatically):

```
x-api-key: sk-ant-api03-...
anthropic-version: 2023-06-01
content-type: application/json
```

## First API Call

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)
print(message.content[0].text)
```

## Rate Limits

Rate limits are enforced per API key and depend on your **spend tier**:

| Tier | Requirement | RPM | Notes |
|------|-------------|-----|-------|
| Free / Build | No deposit | ~5 RPM | Very limited |
| Tier 1 | $5 deposit | 50 RPM | Entry paid tier |
| Tier 2 | Higher spend | 1,000 RPM | — |
| Tier 3 | Higher spend | 2,000 RPM | — |
| Tier 4 | $400+ spend | 4,000 RPM | Highest self-serve |

Rate limits have three dimensions per model class:
- **RPM** — Requests Per Minute
- **ITPM** — Input Tokens Per Minute
- **OTPM** — Output Tokens Per Minute

**Important**: Cached token reads generally do NOT count against ITPM, making effective throughput higher for cache-heavy workloads.

When rate-limited, the API returns HTTP `429`. Implement exponential backoff with jitter.

## Rate Limit Response Headers

```
x-ratelimit-limit-requests: 50
x-ratelimit-limit-tokens: 40000
x-ratelimit-remaining-requests: 45
x-ratelimit-remaining-tokens: 36000
x-ratelimit-reset-requests: 2026-06-20T12:00:00Z
x-ratelimit-reset-tokens: 2026-06-20T12:00:10Z
```

## Common Errors

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request / invalid params | Fix request format |
| 401 | Invalid API key | Check `ANTHROPIC_API_KEY` |
| 403 | Permission denied | Check key permissions |
| 429 | Rate limited | Backoff and retry |
| 500 | Server error | Retry with backoff |
| 529 | Overloaded | Retry with backoff |

## SDK Installation

```bash
# Python
pip install anthropic

# Node.js
npm install @anthropic-ai/sdk
```

## Custom Base URL

If you need to route through a proxy or use a different endpoint:

```python
client = anthropic.Anthropic(base_url="https://your-proxy.example.com")
```

## API Versioning

Include `anthropic-version: 2023-06-01` header (SDK adds this automatically). Newer beta features may require additional `anthropic-beta` headers.
