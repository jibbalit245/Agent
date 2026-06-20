# Vertex AI Authentication

> Source: https://cloud.google.com/vertex-ai/docs/authentication
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

Vertex AI uses standard Google Cloud authentication methods. Authentication determines the identity (who you are) and authorization determines what resources you can access.

## Authentication Methods

### 1. Application Default Credentials (ADC) - Recommended

ADC is the standard way to authenticate when running on Google Cloud or locally during development. The SDK automatically searches for credentials in a predefined order.

**ADC Search Order:**
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable (path to service account JSON)
2. User credentials set by `gcloud auth application-default login`
3. Google Cloud service account attached to compute resource (GCE, Cloud Run, GKE, etc.)
4. Google Cloud project set in environment

**For local development:**
```bash
gcloud auth application-default login
```

**For production on Google Cloud (no code changes needed)** - the compute resource's attached service account is used automatically.

### 2. Service Account Key File

```python
from google.oauth2 import service_account
from google.cloud import aiplatform

credentials = service_account.Credentials.from_service_account_file(
    '/path/to/service-account-key.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

aiplatform.init(
    project='my-project',
    location='us-central1',
    credentials=credentials
)
```

With the GenAI SDK:
```python
import google.auth
from google import genai

# Load credentials from file
credentials, project = google.auth.load_credentials_from_file(
    '/path/to/service-account-key.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

client = genai.Client(
    vertexai=True,
    project=project,
    location='us-central1',
    credentials=credentials
)
```

### 3. Explicit OAuth2 Credentials

```python
import google.auth
import google.auth.transport.requests

# Get ADC credentials with refresh
credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Refresh if needed
request = google.auth.transport.requests.Request()
credentials.refresh(request)

# Use access token in requests
access_token = credentials.token
```

### 4. Workload Identity Federation (No Key Files)

Preferred for non-Google Cloud environments (AWS, Azure, GitHub Actions, etc.):

```python
from google.auth import identity_pool

credentials = identity_pool.Credentials.from_info({
    "type": "external_account",
    "audience": "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
    "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
    "token_url": "https://sts.googleapis.com/v1/token",
    "credential_source": {
        "file": "/var/run/service-account/token",
        "format": {
            "type": "text"
        }
    },
    "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SA_EMAIL:generateAccessToken"
})
```

## Required IAM Roles for Vertex AI

### Minimum Required Roles

| Role | Resource Level | Use Case |
|------|---------------|----------|
| `roles/aiplatform.user` | Project | Use Vertex AI resources |
| `roles/aiplatform.viewer` | Project | View resources only |
| `roles/aiplatform.admin` | Project | Full access to all resources |

### Generative AI Specific Roles

| Role | Description |
|------|-------------|
| `roles/aiplatform.user` | Required to call Gemini/generative AI APIs |
| `roles/ml.developer` | Train and deploy models |
| `roles/ml.viewer` | View ML resources |

### Granting Roles

```bash
# Grant Vertex AI user role to a service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Grant to a user
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:user@example.com" \
  --role="roles/aiplatform.user"
```

## Setting Up Authentication for Different Environments

### Local Development

```bash
# Install Google Cloud SDK
# Then authenticate
gcloud auth application-default login

# Set project
gcloud config set project PROJECT_ID

# Verify authentication
gcloud auth application-default print-access-token
```

Python code (no explicit credentials needed with ADC):
```python
from google.cloud import aiplatform

aiplatform.init(project='PROJECT_ID', location='us-central1')
```

### Google Compute Engine / Cloud Run / App Engine

No code changes needed. The service account attached to the compute resource is used automatically.

Ensure the service account has the required IAM roles:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:COMPUTE_SA@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Google Kubernetes Engine (GKE)

Use Workload Identity to map Kubernetes service accounts to Google service accounts:

```bash
# Enable Workload Identity on cluster
gcloud container clusters update CLUSTER_NAME \
  --workload-pool=PROJECT_ID.svc.id.goog

# Annotate Kubernetes service account
kubectl annotate serviceaccount KSA_NAME \
  --namespace NAMESPACE \
  iam.gke.io/gcp-service-account=GSA_EMAIL
```

### CI/CD Pipelines

**Using Workload Identity Federation (recommended):**
```yaml
# GitHub Actions example
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID'
    service_account: 'SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com'
```

**Using service account key (less recommended):**
```yaml
- uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_CREDENTIALS }}
```

## REST API Authentication

For direct REST API calls, use a Bearer token:

```bash
# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Make API call
curl -X POST \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/publishers/google/models/gemini-2.5-flash:generateContent" \
  -d '{"contents": [{"role": "user", "parts": [{"text": "Hello"}]}]}'
```

## Using GOOGLE_APPLICATION_CREDENTIALS

```bash
# Set environment variable to service account key file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Python code uses it automatically
from google.cloud import aiplatform
aiplatform.init(project='PROJECT_ID', location='us-central1')
```

## Impersonating a Service Account

```python
from google.auth import impersonated_credentials
import google.auth

# Get source credentials (e.g., your user credentials)
source_credentials, project = google.auth.default()

# Impersonate target service account
target_credentials = impersonated_credentials.Credentials(
    source_credentials=source_credentials,
    target_principal='TARGET_SA@PROJECT_ID.iam.gserviceaccount.com',
    target_scopes=['https://www.googleapis.com/auth/cloud-platform'],
)

from google.cloud import aiplatform
aiplatform.init(
    project='PROJECT_ID',
    location='us-central1',
    credentials=target_credentials
)
```

## Checking Your Authentication

```bash
# Check current authenticated user
gcloud auth list

# Check ADC
gcloud auth application-default print-access-token

# Check service account impersonation
gcloud auth print-identity-token --impersonate-service-account=SA@PROJECT.iam.gserviceaccount.com
```

## Common Authentication Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `UNAUTHENTICATED` | No credentials found | Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS` |
| `PERMISSION_DENIED` | Insufficient IAM roles | Grant `roles/aiplatform.user` to the authenticated identity |
| `Project not found` | Wrong project ID or not enabled | Check project ID and enable Vertex AI API |
| `Credentials expired` | Token has expired | Refresh with `gcloud auth application-default login` |

## Required APIs

Enable the Vertex AI API:
```bash
gcloud services enable aiplatform.googleapis.com
```

Additional APIs that may be needed:
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com
```

## Related Resources

- Application Default Credentials: https://cloud.google.com/docs/authentication/application-default-credentials
- Service Accounts: https://cloud.google.com/iam/docs/service-account-overview
- Workload Identity Federation: https://cloud.google.com/iam/docs/workload-identity-federation
- IAM Roles for Vertex AI: https://cloud.google.com/vertex-ai/docs/general/access-control
