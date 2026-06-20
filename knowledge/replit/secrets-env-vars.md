# Replit Secrets & Environment Variables
> Source: https://docs.replit.com/replit-workspace/secrets
> Fetched: 2026-06-20

## Overview

Replit Secrets are environment variables with enhanced security features. They allow you to store API keys, passwords, and other sensitive configuration without hardcoding them in your source code.

Secrets are:
- **Encrypted at rest**
- **Hidden from the code editor** (not visible as plain text files)
- **Not visible in version history** (not committed to git)
- **Not transferred when someone forks your Repl** — forkers must add their own secrets
- Available as standard environment variables in your running code

## Accessing the Secrets Panel

In the Replit workspace, find the **Secrets** tool:
- Click the lock icon (🔒) in the left sidebar
- Or: Tools menu → Secrets

## Adding a Secret

1. Open the Secrets panel
2. Click **"+ New Secret"** (or "Add new secret")
3. Enter the **Key** (environment variable name, e.g., `OPENAI_API_KEY`)
4. Enter the **Value** (the secret value)
5. Click **"Add Secret"**

The secret is immediately available in the running environment.

## Accessing Secrets in Code

Secrets are injected as standard OS environment variables. Access them using your language's native env var API:

### Python

```python
import os

# Using os.environ (raises KeyError if not set)
api_key = os.environ["OPENAI_API_KEY"]

# Using os.getenv (returns None if not set, or use default)
api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY", "default-value")

# Common pattern with error handling
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY secret not set")
```

### Node.js

```javascript
// Access via process.env
const apiKey = process.env.OPENAI_API_KEY;
const hfToken = process.env.HF_TOKEN;

// With default
const port = process.env.PORT || 3000;

// Common pattern
if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY is not set");
}
```

### Shell (bash)

```bash
echo $MY_SECRET
curl -H "Authorization: Bearer $HF_TOKEN" https://api.example.com
```

## Workspace Secrets vs Deployment Secrets

This is a **critical distinction** in Replit:

| | Workspace Secrets | Deployment Secrets |
|---|---|---|
| Where set | Secrets panel in workspace | Deploy → Settings → Secrets |
| Available in | Development environment | Deployed/production app |
| Auto-synced | Sometimes (see note) | Must be set separately |

**By default, workspace secrets do NOT automatically transfer to deployed apps.** You must add secrets separately in the deployment configuration.

### Exception (2025 update)
Replit added automatic syncing of workspace secrets to deployment secrets for some plans. Check your deployment settings to confirm whether secrets auto-sync or need to be added manually.

### Adding Secrets to a Deployment

1. Go to the **Deploy** panel in your Repl
2. Click on your deployment's **Settings** or **Configuration** tab
3. Find the **Secrets** or **Environment Variables** section
4. Add each required secret (key + value)
5. Re-deploy for changes to take effect

> **Important**: Static deployments do NOT support secrets at all. Only Autoscale, Reserved VM, and Scheduled deployment types support secrets.

## App Secrets vs Repl Secrets

Replit has two levels of secrets visible in the Secrets panel:

1. **Workspace Secrets** (aka "Repl Secrets"): Used during development in the editor
2. **App Secrets**: Secrets associated specifically with your deployed Replit App; managed in the App Secrets tab

## Security Properties

### What Replit Secrets Protect Against
- Secrets don't appear in git history (not committed to the repository)
- Not visible in the code editor's file tree
- Encrypted at rest by Replit's infrastructure
- Not exposed when someone forks/clones your Repl

### What Replit Secrets Do NOT Protect Against
- A collaborator with edit access to your Repl can read secrets from running code (via `print(os.environ)`)
- Secrets visible in Replit's UI to authorized workspace collaborators
- If your code logs the secret value, it appears in logs

### Best Practices
- Never print or log secret values in production
- Use fine-grained API keys (least privilege)
- Rotate secrets regularly
- Don't store secrets in `.env` files committed to the Repl's git

## Using .env Files (Alternative)

While Replit's Secrets panel is preferred, you can also use `.env` files:

```bash
# .env file (NOT committed to git — add to .gitignore)
OPENAI_API_KEY=sk-...
HF_TOKEN=hf_...
DATABASE_URL=postgresql://...
```

Load with python-dotenv:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

> **Caution**: `.env` files are visible in Replit's file tree to anyone with access to the Repl. Use the Secrets panel for true security.

## Plan Differences

Replit Secrets functionality is available on all plans (free and paid). Key differences:
- **Starter (free)**: Secrets available; deployment secrets must be configured separately
- **Core ($20/month)**: Same secrets functionality; automatic sync may be available; more secrets supported
- **Pro/Teams**: Organization-level secret management, more collaborators

## Common Use Cases

### HuggingFace Token

```python
import os
from huggingface_hub import InferenceClient

# Set HF_TOKEN in Replit Secrets panel
client = InferenceClient(token=os.environ["HF_TOKEN"])
```

### OpenAI API Key

```python
import os
from openai import OpenAI

# Set OPENAI_API_KEY in Replit Secrets panel
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
```

### Database URL

```python
import os
import psycopg2

DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL)
```

## References

- [Replit Secrets Docs](https://docs.replit.com/replit-workspace/workspace-features/secrets)
- [Replit Announcing Secrets Management](https://blog.replit.com/secrets)
- [How to Store Secrets Safely in Replit](https://www.rapidevelopers.com/replit-tutorial/how-to-securely-manage-project-secrets-in-replit-without-exposing-sensitive-data)
- [Replit Secrets & Environment Variables Guide](https://vibeappscanner.com/replit-secrets-environment-variables)
