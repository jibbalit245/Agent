# Google Cloud Authentication  
> Source: https://cloud.google.com/docs/authentication  
> Fetched: 2026-06-20

## Overview

Google Cloud supports several authentication methods. The right choice depends on your environment (local dev, CI/CD, production on GCP, production off-GCP).

## Three Main Credential Types

### 1. API Keys

- Simple string token (e.g., `AIza...`)
- Used with: Gemini API (Google AI Studio), Maps API, some other Google APIs
- **Not supported** for most Vertex AI / Google Cloud APIs
- No expiration by default, but can be restricted by IP or referrer
- Best for: Simple APIs, client-side usage, prototyping

```bash
export GEMINI_API_KEY="AIzaSy..."
```

### 2. Service Accounts

- A "robot" Google account for programmatic access
- Has a JSON key file containing private key
- Assigned IAM roles to control permissions
- Best for: Production systems, CI/CD, running outside GCP

```bash
# Create service account
gcloud iam service-accounts create my-sa \
  --display-name="My Service Account"

# Grant role
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:my-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download JSON key
gcloud iam service-accounts keys create key.json \
  --iam-account=my-sa@YOUR_PROJECT.iam.gserviceaccount.com
```

**Security warning**: Service account JSON keys are long-lived credentials. Google recommends using Workload Identity Federation or ADC with impersonation instead when possible. A leaked key can be used without any additional information.

### 3. Application Default Credentials (ADC)

ADC is a strategy that automatically finds credentials by checking several locations in order:

**ADC Credential Search Order:**
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable (points to a JSON file)
2. User credentials from `gcloud auth application-default login` (`~/.config/gcloud/application_default_credentials.json`)
3. Attached service account (on GCE, GKE, Cloud Run, App Engine, Cloud Functions — uses metadata server)

ADC is the recommended approach because your code doesn't change between environments.

## Setting Up ADC for Local Development

### Option A: User Credentials (recommended for personal dev)

```bash
gcloud auth application-default login
```

Opens browser, authenticates your Google account, saves credentials to `~/.config/gcloud/application_default_credentials.json`.

Client libraries automatically use these credentials.

```python
# No credentials code needed — ADC finds them automatically
import vertexai
vertexai.init(project="my-project", location="us-central1")
```

### Option B: Service Account JSON Key via Environment Variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account-key.json"
```

**Important**: This variable applies only to the current shell session. Add to `.bashrc`/`.zshrc` or `.env` for persistence.

```python
# Again, no credentials code needed — ADC reads GOOGLE_APPLICATION_CREDENTIALS
from google.cloud import aiplatform
aiplatform.init(project="my-project", location="us-central1")
```

### Option C: Service Account Impersonation (best practice for dev)

Avoids downloading a key file; instead impersonates the SA using your user credentials:

```bash
gcloud auth application-default login \
  --impersonate-service-account=my-sa@PROJECT.iam.gserviceaccount.com
```

## Setting Up ADC for Production (Non-GCP)

For servers running outside Google Cloud (AWS, Azure, on-prem):

```bash
# Set the key file path
export GOOGLE_APPLICATION_CREDENTIALS="/etc/gcloud/service-account.json"
```

Or pass credentials explicitly in code:

```python
from google.oauth2 import service_account
from google.cloud import aiplatform

credentials = service_account.Credentials.from_service_account_file(
    "/path/to/key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

aiplatform.init(
    project="my-project",
    location="us-central1",
    credentials=credentials
)
```

## GCP-Hosted Environments (Automatic ADC)

On these services, ADC automatically uses the attached service account — no configuration needed:
- Google Compute Engine (GCE)
- Google Kubernetes Engine (GKE) — requires Workload Identity for best practices
- Cloud Run
- Cloud Functions
- App Engine
- Cloud Build

The default service account is used unless you specify a custom one.

## Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON key file |
| `GOOGLE_CLOUD_PROJECT` | Default GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Default region (used by some SDKs) |
| `GEMINI_API_KEY` | API key for Gemini API (AI Studio only) |

## Common Gotchas

1. **`GOOGLE_APPLICATION_CREDENTIALS` is session-scoped**: Set it in your shell profile or `.env` file, not just once in a terminal.

2. **Wrong scopes**: Service account credentials need `https://www.googleapis.com/auth/cloud-platform` for most GCP APIs.

3. **ADC picks up the wrong credentials**: If both `GOOGLE_APPLICATION_CREDENTIALS` and `gcloud` user credentials exist, the env var takes priority.

4. **Quota project**: When using user credentials with `gcloud auth application-default login`, you may need to set a quota project:
   ```bash
   gcloud auth application-default set-quota-project YOUR_PROJECT
   ```

5. **Service account key rotation**: Keys don't expire but should be rotated regularly. List active keys:
   ```bash
   gcloud iam service-accounts keys list --iam-account=my-sa@PROJECT.iam.gserviceaccount.com
   ```

6. **Docker/containers**: Mount the credentials file and set `GOOGLE_APPLICATION_CREDENTIALS` inside the container.

## Required IAM Roles for Vertex AI

| Role | Description |
|------|-------------|
| `roles/aiplatform.user` | Use Vertex AI resources |
| `roles/aiplatform.admin` | Full Vertex AI admin |
| `roles/ml.admin` | Legacy ML role (also works) |

## References

- [How ADC Works](https://cloud.google.com/docs/authentication/application-default-credentials)
- [Set Up ADC for Local Dev](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment)
- [Vertex AI Authentication](https://cloud.google.com/vertex-ai/docs/authentication)
- [gcloud auth application-default](https://cloud.google.com/sdk/gcloud/reference/auth/application-default)
- [Troubleshoot ADC](https://cloud.google.com/docs/authentication/troubleshoot-adc)
