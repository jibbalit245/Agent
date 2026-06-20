# Replit Environment Variables

> Source: https://docs.replit.com/replit-workspace/environment-variables
> Last updated: 2026-06

## Overview

Replit supports two ways to set environment variables:

1. **Secrets** — For sensitive values (API keys, passwords). Encrypted, not in code.
2. **`.replit` file** — For non-sensitive configuration values. Stored in the project file.

## Methods of Setting Environment Variables

### 1. Secrets (for sensitive data)

Use the **Secrets panel** in the workspace for sensitive values:
- API keys
- Database passwords
- OAuth secrets
- Private tokens

See `/home/user/Agent/knowledge/replit/secrets.md` for full details.

### 2. `.replit` File (for non-sensitive config)

For non-sensitive environment variables, add them to `.replit`:

```toml
# Available during 'Run' (development)
[env]
NODE_ENV = "development"
PORT = "8080"
LOG_LEVEL = "debug"
APP_NAME = "MyApp"

# Alternative: only for the run command
[run.env]
FLASK_ENV = "development"
```

### 3. Shell Export (temporary, session only)

```bash
export MY_VAR="value"
echo $MY_VAR
```

Note: Shell exports only last for the current shell session and are lost when the shell restarts.

## Built-in Replit Environment Variables

Replit automatically injects several environment variables into every Repl:

| Variable | Description | Example |
|----------|-------------|---------|
| `REPL_ID` | Unique ID for the Repl | `abc123-def456` |
| `REPL_OWNER` | Username of Repl owner | `myusername` |
| `REPL_SLUG` | Repl name/slug | `my-web-app` |
| `REPL_HOME` | Home directory path | `/home/user` |
| `REPLIT_DB_URL` | URL for Replit Key-Value DB | `https://kv.replit.com/...` |
| `REPLIT_CLUSTER` | Cluster identifier | `pit` |
| `HOME` | Home directory | `/home/user` |
| `PATH` | System PATH | Standard PATH + Nix paths |
| `PYTHONPATH` | Python module path | Auto-configured |

### Replit Object Storage Variables

When Object Storage is configured:
- `REPLIT_OBJECT_STORAGE_BUCKET` — Bucket name/ID

### Deployment-Specific Variables

These are set when running as a deployed app:
- `REPLIT_DEPLOYMENT` — Set to `1` when running as deployment

## Workspace vs. Deployment Environment Variables

| Context | Where Set | When Active |
|---------|-----------|-------------|
| Workspace | Secrets panel or `.replit [env]` | When clicking "Run" |
| Deployment | Deployments tab → Secrets/Config | When app is deployed |

**Important**: Variables set in workspace secrets do NOT automatically apply to deployments. You must configure them separately in the Deployments panel.

## Accessing Environment Variables

### Python

```python
import os

# Get value (returns None if not set)
value = os.environ.get('MY_VAR')

# Get value with default
value = os.environ.get('MY_VAR', 'default_value')

# Get value (raises KeyError if not set)
value = os.environ['MY_VAR']

# Check if set
if 'MY_VAR' in os.environ:
    print("Variable is set")

# Print all environment variables
for key, value in os.environ.items():
    print(f"{key}={value}")
```

### Node.js

```javascript
// Get value (undefined if not set)
const value = process.env.MY_VAR;

// With default
const value = process.env.MY_VAR || 'default_value';

// Required variable (throw if missing)
function requireEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
}
const apiKey = requireEnv('API_KEY');

// Using dotenv-style loading (not needed on Replit, built-in)
// process.env is already populated
```

### Shell/Bash

```bash
# Access variable
echo $MY_VAR

# With default
echo ${MY_VAR:-default_value}

# Check if set
if [ -n "$MY_VAR" ]; then
  echo "MY_VAR is set to: $MY_VAR"
fi
```

### Go

```go
import "os"

value := os.Getenv("MY_VAR")  // "" if not set

// With check
value, ok := os.LookupEnv("MY_VAR")
if !ok {
    log.Fatal("MY_VAR is not set")
}
```

### Ruby

```ruby
value = ENV['MY_VAR']           # nil if not set
value = ENV.fetch('MY_VAR')     # raises KeyError if not set
value = ENV.fetch('MY_VAR', 'default')  # with default
```

## Using python-dotenv on Replit

While not required (Replit injects env vars automatically), you can use dotenv for compatibility:

```python
# Not needed on Replit, but works
from dotenv import load_dotenv
load_dotenv()  # Loads .env file if present

import os
value = os.environ.get('MY_VAR')
```

## Environment in Deployment

When deploying, configure environment variables in the Deployments panel:

1. **Deployment Secrets**: Sensitive values (API keys, DB passwords)
2. **Deployment Config**: Non-sensitive values (NODE_ENV=production, etc.)

Access the same way in code — `os.environ`, `process.env`, etc.

## Example: Multi-Environment Configuration

```python
import os

ENV = os.environ.get('APP_ENV', 'development')

config = {
    'development': {
        'DEBUG': True,
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'sqlite:///dev.db'),
        'LOG_LEVEL': 'DEBUG',
    },
    'production': {
        'DEBUG': False,
        'DATABASE_URL': os.environ['DATABASE_URL'],  # Required in production
        'LOG_LEVEL': 'INFO',
    }
}

app_config = config[ENV]
```

## Common Issues

### Variable Not Found
- Check that the secret/variable is set in the right context (workspace vs. deployment)
- Verify spelling — environment variable names are case-sensitive
- Restart the shell/repl after changing `.replit` env section

### Variable Not in Deployment
- Deployment secrets are separate from workspace secrets
- Re-add all required secrets in Deployments → Secrets panel
- Redeploy after adding deployment secrets
