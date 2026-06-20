# Replit Secrets (Environment Variables for Sensitive Data)

> Source: https://docs.replit.com/replit-workspace/secrets
> Last updated: 2026-06

## What are Secrets?

Secrets in Replit are **encrypted environment variables** for storing sensitive information like API keys, database passwords, and tokens. They are the secure way to store credentials that should not be committed to your code.

Secrets are:
- Encrypted at rest
- Not visible in version control
- Injected as environment variables at runtime
- Only accessible to the Repl owner and collaborators

## Workspace Secrets vs. Deployment Secrets

**IMPORTANT**: Replit has two separate sets of secrets:

| Type | When Used | Where to Set |
|------|-----------|--------------|
| **Workspace Secrets** | When clicking "Run" in development | Secrets panel in workspace |
| **Deployment Secrets** | When app is deployed | Deployments tab → Secrets |

You must add secrets **separately** for deployment. Workspace secrets do NOT automatically transfer to deployed apps.

This allows you to use different values in dev vs. production (e.g., test API keys in dev, production keys in deployment).

## Setting Workspace Secrets

### Via the UI

1. Open your Replit App
2. Click the **Tools** icon in the sidebar (or find "Secrets" in the tools panel)
3. Click **+ New Secret**
4. Enter a **Key** (variable name, e.g., `API_KEY`)
5. Enter the **Value** (the secret value)
6. Click **Add Secret**

### Via Shell (Alternative)

Secrets cannot be set via shell commands — always use the UI or the Secrets panel.

## Accessing Secrets in Code

Secrets are injected as environment variables and accessed with standard language APIs:

### Python

```python
import os

api_key = os.environ.get('API_KEY')
database_url = os.environ['DATABASE_URL']  # Raises KeyError if not set

# Safer with default:
debug = os.environ.get('DEBUG', 'false')
```

### Node.js

```javascript
const apiKey = process.env.API_KEY;
const databaseUrl = process.env.DATABASE_URL;

// Using dotenv (not needed on Replit, but works)
// require('dotenv').config();
```

### Other Languages

Secrets are available as standard environment variables in all languages:

```bash
# Shell
echo $API_KEY

# Go
import "os"
apiKey := os.Getenv("API_KEY")

# Ruby
api_key = ENV['API_KEY']
```

## Setting Deployment Secrets

When you deploy your app, add secrets for the deployed environment:

1. Go to the **Deployments** tab
2. Find the **Secrets** section
3. Click **Add Secret**
4. Enter the Key and Value
5. Save

Then redeploy for changes to take effect.

## Best Practices

### Do Store in Secrets:
- API keys (OpenAI, Stripe, SendGrid, etc.)
- Database passwords and connection strings
- OAuth client secrets
- JWT signing secrets
- Webhook secrets
- Private keys

### Do NOT Store in Secrets:
- Public API keys (use `.replit` `[env]` section instead)
- Non-sensitive configuration values
- Public URLs

### Naming Conventions

Use uppercase with underscores:
```
DATABASE_URL
OPENAI_API_KEY
STRIPE_SECRET_KEY
SENDGRID_API_KEY
JWT_SECRET
REDIS_URL
```

## Common Secret Patterns

### Database Connection String

```
Key: DATABASE_URL
Value: postgresql://user:password@host:5432/dbname
```

```python
import os
from sqlalchemy import create_engine

engine = create_engine(os.environ['DATABASE_URL'])
```

### OpenAI API Key

```
Key: OPENAI_API_KEY
Value: sk-...
```

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
```

### Stripe Keys

```
# Development
Key: STRIPE_SECRET_KEY
Value: sk_test_...

# Production (in Deployment Secrets)
Key: STRIPE_SECRET_KEY
Value: sk_live_...
```

## Checking for Missing Secrets

Good practice to validate secrets on startup:

```python
import os
import sys

required_secrets = ['DATABASE_URL', 'API_KEY', 'SECRET_KEY']

for secret in required_secrets:
    if not os.environ.get(secret):
        print(f"ERROR: Missing required secret: {secret}")
        sys.exit(1)

print("All required secrets present")
```

## Notes

- Secrets are **not** visible in the editor or file explorer
- Collaborators with access to a Repl can see secret **names** but not values (behavior may vary)
- Secrets are stored per-Repl, not globally
- There's no built-in secret sharing between Repls (use a secrets manager like HashiCorp Vault for that)
