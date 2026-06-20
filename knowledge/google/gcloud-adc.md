# Application Default Credentials (ADC)

> Source: https://cloud.google.com/docs/authentication/application-default-credentials
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

Application Default Credentials (ADC) is a strategy used by Google authentication libraries to automatically find credentials based on the application's environment. When you use ADC, your code can run in different environments without changing the authentication code.

ADC is the **recommended** approach for most authentication scenarios as it provides environment-aware credential discovery.

## How ADC Works

ADC checks credential sources in the following order:

1. **`GOOGLE_APPLICATION_CREDENTIALS` environment variable** - If set, ADC uses the credentials file or configuration at this path
2. **User credentials from gcloud CLI** - Credentials configured with `gcloud auth application-default login`
3. **Attached service account** (for Google Cloud-hosted environments):
   - Google Compute Engine
   - Google Kubernetes Engine
   - Cloud Run
   - Cloud Functions
   - App Engine
4. **Default service account** - The service account attached to the resource

## Setting Up ADC

### For Local Development

Run the gcloud CLI command to authenticate your user account:

```bash
gcloud auth application-default login
```

This opens a browser window for Google account authentication. Credentials are stored at:
- Linux/macOS: `~/.config/gcloud/application_default_credentials.json`
- Windows: `%APPDATA%\gcloud\application_default_credentials.json`

Set the default project:
```bash
gcloud config set project PROJECT_ID
```

Or set via environment variable:
```bash
export GOOGLE_CLOUD_PROJECT=PROJECT_ID
```

### For Production on Google Cloud

When running on Google Cloud services (GCE, GKE, Cloud Run, Cloud Functions, App Engine), no explicit authentication setup is required. The compute resource's attached service account provides credentials automatically.

Ensure the service account has the necessary IAM permissions for your use case.

### Using a Service Account Key File

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

Or in Python:
```python
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/service-account-key.json'
```

**Note:** Service account key files are sensitive. Consider using Workload Identity Federation instead for non-Google Cloud environments.

## Using ADC in Code

### Python

```python
import google.auth

# Get ADC credentials automatically
credentials, project = google.auth.default()

# With specific scopes
credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
```

With Google Cloud client libraries (ADC used automatically):
```python
from google.cloud import aiplatform

# ADC used automatically - no credentials argument needed
aiplatform.init(project='my-project', location='us-central1')
```

With the GenAI SDK:
```python
from google import genai

# ADC used automatically when vertexai=True
client = genai.Client(
    vertexai=True,
    project='my-project',
    location='us-central1'
)
```

### Go

```go
import (
    "context"
    "golang.org/x/oauth2/google"
)

// ADC automatically
ctx := context.Background()
credentials, err := google.FindDefaultCredentials(ctx, "https://www.googleapis.com/auth/cloud-platform")
```

### Java

```java
import com.google.auth.oauth2.GoogleCredentials;

// ADC automatically
GoogleCredentials credentials = GoogleCredentials.getApplicationDefault()
    .createScoped("https://www.googleapis.com/auth/cloud-platform");
```

### Node.js

```javascript
const {GoogleAuth} = require('google-auth-library');

// ADC automatically
const auth = new GoogleAuth({
  scopes: 'https://www.googleapis.com/auth/cloud-platform'
});
const client = await auth.getClient();
```

### REST API / curl

```bash
# Get access token using ADC (via gcloud)
ACCESS_TOKEN=$(gcloud auth application-default print-access-token)

curl -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/..."
```

## Credential Types and Their ADC Priority

### 1. External Credentials File (GOOGLE_APPLICATION_CREDENTIALS)

Can point to:
- **Service account key file** - JSON with service account credentials
- **External credentials configuration** - For Workload Identity Federation
- **Impersonated service account configuration**

Example service account key JSON structure:
```json
{
  "type": "service_account",
  "project_id": "my-project",
  "private_key_id": "KEY_ID",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n",
  "client_email": "sa-name@my-project.iam.gserviceaccount.com",
  "client_id": "CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sa-name%40my-project.iam.gserviceaccount.com"
}
```

### 2. User Credentials (gcloud auth application-default)

Stored locally after running `gcloud auth application-default login`:
```json
{
  "client_id": "...",
  "client_secret": "...",
  "refresh_token": "...",
  "type": "authorized_user"
}
```

**Note:** User credentials should only be used for local development, not production.

### 3. Attached Service Account

When running on Google Cloud infrastructure, metadata server provides credentials:
- URL: `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token`
- No configuration needed

## Workload Identity Federation (Non-Google Cloud Environments)

For environments outside Google Cloud (AWS, Azure, GitHub Actions, on-premises), use Workload Identity Federation instead of service account keys.

### Configuration File Format

```json
{
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
  "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
  "token_url": "https://sts.googleapis.com/v1/token",
  "credential_source": {
    "file": "/var/run/service-account/token"
  },
  "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com:generateAccessToken"
}
```

Set via environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/workload-identity-config.json
```

### AWS Example

```json
{
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
  "subject_token_type": "urn:ietf:params:oauth:token-type:aws4_request",
  "token_url": "https://sts.googleapis.com/v1/token",
  "credential_source": {
    "environment_id": "aws1",
    "regional_cred_verification_url": "https://sts.{region}.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15"
  }
}
```

### GitHub Actions Example

```yaml
jobs:
  deploy:
    permissions:
      id-token: write  # Required for OIDC
      contents: read
    steps:
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID'
          service_account: 'sa-name@project-id.iam.gserviceaccount.com'

      - name: Use Google Cloud
        run: |
          gcloud auth list
          python my_script.py  # Uses ADC automatically
```

## Quotas and Project Detection

ADC can detect the project from:
1. `GOOGLE_CLOUD_PROJECT` or `GCLOUD_PROJECT` environment variables
2. `gcloud config get-value project`
3. Compute metadata server (for Google Cloud resources)

```python
import google.auth

credentials, project = google.auth.default()
print(f"Using project: {project}")
```

## Refreshing Credentials

```python
import google.auth
import google.auth.transport.requests

credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Refresh credentials if needed
if not credentials.valid:
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)

print(f"Access token: {credentials.token}")
print(f"Token expiry: {credentials.expiry}")
```

## Impersonating a Service Account

```python
from google.auth import impersonated_credentials
import google.auth

# Base credentials (user or service account)
source_credentials, project = google.auth.default()

# Impersonate another service account
impersonated = impersonated_credentials.Credentials(
    source_credentials=source_credentials,
    target_principal='target-sa@project.iam.gserviceaccount.com',
    target_scopes=['https://www.googleapis.com/auth/cloud-platform'],
    lifetime=3600  # 1 hour
)
```

Or with gcloud:
```bash
gcloud auth application-default login --impersonate-service-account=SA_EMAIL
```

## Testing and Debugging

### Verify ADC is Configured

```bash
# Print current ADC token
gcloud auth application-default print-access-token

# Show current gcloud credentials
gcloud auth list

# Test with curl
curl -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=$(gcloud auth application-default print-access-token)"
```

### Python Debug

```python
import google.auth
import google.auth.transport.requests

credentials, project = google.auth.default()
print(f"Credentials type: {type(credentials)}")
print(f"Project: {project}")

# Refresh to get token
request = google.auth.transport.requests.Request()
credentials.refresh(request)
print(f"Token valid: {credentials.valid}")
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "Could not automatically determine credentials" | Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS` |
| "Quota project not set" | Set `GOOGLE_CLOUD_PROJECT` or use `gcloud config set project PROJECT_ID` |
| "Permission denied" | Ensure service account or user has required IAM roles |
| "Invalid JWT signature" | Service account key file may be corrupted; generate a new key |
| Token expiration errors | Credentials auto-refresh; if not, call `credentials.refresh(request)` |

## Security Best Practices

1. **Prefer ADC over key files** - Eliminates credential management overhead
2. **Use Workload Identity Federation** instead of service account keys for non-Google Cloud environments
3. **Never commit credentials to version control** - Add key files to `.gitignore`
4. **Rotate service account keys regularly** - Or better, eliminate them with Workload Identity
5. **Use least-privilege IAM** - Grant only the minimum necessary permissions
6. **Set `GOOGLE_APPLICATION_CREDENTIALS` in environment** - Not hardcoded in code

## Related Resources

- Vertex AI Authentication: https://cloud.google.com/vertex-ai/docs/authentication
- Service Accounts: https://cloud.google.com/iam/docs/service-account-overview
- Workload Identity Federation: https://cloud.google.com/iam/docs/workload-identity-federation
- google-auth Python library: https://pypi.org/project/google-auth/
