# Google Cloud IAM Service Accounts

> Source: https://cloud.google.com/iam/docs/service-account-overview
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

A **service account** is a special kind of account used by applications (not humans) to authenticate to Google APIs and services. Service accounts are associated with a cryptographic key pair used for authentication.

Service accounts enable:
- Applications running on Google Cloud to authenticate without user credentials
- Automated processes and pipelines to access Google Cloud resources
- Workload-to-workload authentication

## Service Account Types

### 1. User-Managed Service Accounts

Created and managed by you:
- `PROJECT_ID.iam.gserviceaccount.com` format
- Full control over keys, permissions, and lifecycle
- Can be granted IAM roles at project, folder, or organization level

### 2. Google-Managed Service Accounts

Automatically created by Google for specific services:
- Default Compute Engine SA: `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
- App Engine SA: `PROJECT_ID@appspot.gserviceaccount.com`
- Vertex AI SA: `service-PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com`
- Cannot delete these; Google manages them

### 3. Default Service Accounts

Auto-created when you enable certain APIs:
- Have `Editor` role by default (too permissive; recommended to revoke)
- Examples: Compute Engine default SA, App Engine default SA

## Creating Service Accounts

### Via gcloud CLI

```bash
# Create service account
gcloud iam service-accounts create SA_ID \
  --display-name="My Service Account" \
  --description="Service account for Vertex AI" \
  --project=PROJECT_ID

# The email will be: SA_ID@PROJECT_ID.iam.gserviceaccount.com

# Verify creation
gcloud iam service-accounts describe SA_ID@PROJECT_ID.iam.gserviceaccount.com
```

### Via Cloud Console

1. Navigate to IAM & Admin > Service Accounts
2. Click "Create Service Account"
3. Enter ID, name, description
4. Optionally grant project roles
5. Optionally grant user access to this SA
6. Click "Done"

### Via Python SDK

```python
import google.auth
from googleapiclient import discovery

credentials, project = google.auth.default()
service = discovery.build('iam', 'v1', credentials=credentials)

# Create service account
service_account = service.projects().serviceAccounts().create(
    name=f'projects/{project}',
    body={
        'accountId': 'my-service-account',
        'serviceAccount': {
            'displayName': 'My Service Account',
            'description': 'Service account for Vertex AI',
        }
    }
).execute()

print(f"Created: {service_account['email']}")
```

### Via REST API

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://iam.googleapis.com/v1/projects/PROJECT_ID/serviceAccounts" \
  -d '{
    "accountId": "sa-id",
    "serviceAccount": {
      "displayName": "My Service Account",
      "description": "Service account for Vertex AI"
    }
  }'
```

## Managing Service Account Keys

### Create a Key

```bash
# Create JSON key file
gcloud iam service-accounts keys create key.json \
  --iam-account=SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com

# The key.json file contains the private key - keep it secure!
```

### List Keys

```bash
gcloud iam service-accounts keys list \
  --iam-account=SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com
```

### Delete a Key

```bash
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com
```

### Use Key for Authentication

```bash
# Activate service account with key
gcloud auth activate-service-account SA_EMAIL --key-file=key.json

# Or use in ADC
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

**Security Note:** Key files are sensitive. Prefer Workload Identity Federation over key files when possible.

## Granting Roles to Service Accounts

### At Project Level

```bash
# Grant Vertex AI user role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Grant Storage access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Grant BigQuery access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# Remove role
gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### At Resource Level (e.g., GCS Bucket)

```bash
# Grant access to specific bucket
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Using Python

```python
from google.cloud import resourcemanager_v3
import google.auth

credentials, project = google.auth.default()

# Get current IAM policy
rm_client = resourcemanager_v3.ProjectsClient(credentials=credentials)
policy = rm_client.get_iam_policy(resource=f"projects/{project}")

# Add binding
from google.iam.v1 import policy_pb2
binding = policy_pb2.Binding(
    role="roles/aiplatform.user",
    members=[f"serviceAccount:sa@{project}.iam.gserviceaccount.com"]
)
policy.bindings.append(binding)

# Set the policy
rm_client.set_iam_policy(
    resource=f"projects/{project}",
    policy=policy
)
```

## Common IAM Roles for Vertex AI

### Predefined Roles

| Role | Title | Description |
|------|-------|-------------|
| `roles/aiplatform.admin` | Vertex AI Administrator | Full admin access |
| `roles/aiplatform.user` | Vertex AI User | Use Vertex AI resources |
| `roles/aiplatform.viewer` | Vertex AI Viewer | View Vertex AI resources |
| `roles/aiplatform.featurestoreAdmin` | Feature Store Admin | Manage feature stores |
| `roles/aiplatform.tensorboardWebAppUser` | TensorBoard Web App User | Access TensorBoard |
| `roles/ml.admin` | ML Engine Admin | Legacy ML Engine admin |
| `roles/ml.developer` | ML Engine Developer | Train/deploy models |
| `roles/ml.viewer` | ML Engine Viewer | View ML resources |

### Storage Roles (often needed with Vertex AI)

| Role | Title | Description |
|------|-------|-------------|
| `roles/storage.admin` | Storage Admin | Full control of GCS |
| `roles/storage.objectAdmin` | Storage Object Admin | Create, view, delete objects |
| `roles/storage.objectCreator` | Storage Object Creator | Create objects only |
| `roles/storage.objectViewer` | Storage Object Viewer | View objects only |

### BigQuery Roles (for batch predictions)

| Role | Title | Description |
|------|-------|-------------|
| `roles/bigquery.admin` | BigQuery Admin | Full BQ access |
| `roles/bigquery.dataOwner` | BigQuery Data Owner | Read/write/delete data |
| `roles/bigquery.dataEditor` | BigQuery Data Editor | Read/write data |
| `roles/bigquery.dataViewer` | BigQuery Data Viewer | Read data only |
| `roles/bigquery.jobUser` | BigQuery Job User | Run BQ jobs |

## Service Account Impersonation

Allows a principal to act as a service account without creating keys:

### Grant Impersonation Permission

```bash
# Allow a user to impersonate a service account
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="user:user@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"

# Allow another service account to impersonate
gcloud iam service-accounts add-iam-policy-binding TARGET_SA_EMAIL \
  --member="serviceAccount:CALLER_SA_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"
```

### Use Impersonation with gcloud

```bash
# Run as impersonated service account
gcloud --impersonate-service-account=SA_EMAIL projects list

# Set ADC to impersonate
gcloud auth application-default login \
  --impersonate-service-account=SA_EMAIL
```

### Use Impersonation in Python

```python
from google.auth import impersonated_credentials
import google.auth

# Source credentials (your current identity)
source_credentials, project = google.auth.default()

# Impersonate target service account
impersonated = impersonated_credentials.Credentials(
    source_credentials=source_credentials,
    target_principal='target-sa@project.iam.gserviceaccount.com',
    target_scopes=['https://www.googleapis.com/auth/cloud-platform'],
    lifetime=3600  # Token lifetime in seconds (max 3600 for regular, up to 43200 with delegation)
)

# Use with Vertex AI
from google.cloud import aiplatform
aiplatform.init(
    project=project,
    location='us-central1',
    credentials=impersonated
)
```

## Workload Identity Federation

Allows external identities (non-Google) to impersonate service accounts without keys:

### Set Up Workload Identity Pool

```bash
# Create identity pool
gcloud iam workload-identity-pools create POOL_ID \
  --location=global \
  --display-name="My WIF Pool" \
  --description="Pool for external workloads"

# Create OIDC provider (e.g., for GitHub Actions)
gcloud iam workload-identity-pools providers create-oidc PROVIDER_ID \
  --workload-identity-pool=POOL_ID \
  --location=global \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --display-name="GitHub Provider"
```

### Grant Access

```bash
# Allow GitHub Actions repo to impersonate SA
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/GITHUB_ORG/REPO_NAME" \
  --role="roles/iam.workloadIdentityUser"
```

### GitHub Actions Workflow

```yaml
name: Vertex AI Job
on: [push]

jobs:
  run:
    permissions:
      id-token: write
      contents: read
    
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID'
          service_account: 'sa@project.iam.gserviceaccount.com'
      
      - uses: google-github-actions/setup-gcloud@v2
      
      - run: |
          gcloud ai endpoints list --region=us-central1
          python vertex_ai_script.py
```

## Attaching Service Accounts to Resources

### Compute Engine

```bash
# Create instance with specific service account
gcloud compute instances create INSTANCE_NAME \
  --service-account=SA_EMAIL \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --zone=ZONE

# Change service account on existing instance (must stop first)
gcloud compute instances stop INSTANCE_NAME --zone=ZONE
gcloud compute instances set-service-account INSTANCE_NAME \
  --service-account=SA_EMAIL \
  --scopes=cloud-platform \
  --zone=ZONE
gcloud compute instances start INSTANCE_NAME --zone=ZONE
```

### Cloud Run

```bash
# Deploy with specific service account
gcloud run deploy SERVICE_NAME \
  --image=IMAGE_URI \
  --service-account=SA_EMAIL \
  --region=REGION
```

### Cloud Functions

```bash
# Deploy with specific service account
gcloud functions deploy FUNCTION_NAME \
  --runtime=python310 \
  --service-account=SA_EMAIL \
  --trigger-http \
  --region=REGION
```

## Service Account Best Practices

### 1. Principle of Least Privilege
```bash
# Don't grant broad roles like Editor or Owner
# Instead, grant specific roles for what's needed

# Bad:
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/editor"

# Good:
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### 2. Avoid Service Account Key Files When Possible
- Use Workload Identity Federation for non-Google Cloud environments
- Use attached service accounts for Google Cloud resources
- If keys are necessary, rotate them regularly (every 90 days)

### 3. One Service Account Per Application/Purpose
```bash
# Create dedicated SAs for each workload
gcloud iam service-accounts create vertex-training-sa \
  --display-name="Vertex AI Training SA"
gcloud iam service-accounts create vertex-prediction-sa \
  --display-name="Vertex AI Prediction SA"
```

### 4. Audit Service Account Activity
```bash
# View recent activity (via Cloud Logging)
gcloud logging read \
  'protoPayload.authenticationInfo.principalEmail:"sa@project.iam.gserviceaccount.com"' \
  --limit=50
```

### 5. Disable Unused Service Accounts
```bash
# Disable (soft delete - preserves audit trail)
gcloud iam service-accounts disable SA_EMAIL

# Re-enable
gcloud iam service-accounts enable SA_EMAIL

# Delete (permanent)
gcloud iam service-accounts delete SA_EMAIL
```

## Listing and Auditing

```bash
# List all service accounts in project
gcloud iam service-accounts list --project=PROJECT_ID

# Get IAM bindings for a service account
gcloud iam service-accounts get-iam-policy SA_EMAIL

# Find all roles granted to a service account
gcloud projects get-iam-policy PROJECT_ID \
  --filter="bindings.members:serviceAccount:SA_EMAIL" \
  --format="table(bindings.role)"

# List all service account keys
gcloud iam service-accounts keys list \
  --iam-account=SA_EMAIL \
  --managed-by=user  # Only user-managed keys
```

## Service Account for Vertex AI Typical Setup

```bash
#!/bin/bash
PROJECT_ID="my-project"
SA_ID="vertex-ai-sa"
SA_EMAIL="${SA_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create ${SA_ID} \
  --display-name="Vertex AI Service Account" \
  --project=${PROJECT_ID}

# Grant Vertex AI access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user"

# Grant GCS access for staging bucket
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectAdmin"

# Grant BigQuery access (for batch predictions)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.dataEditor"

echo "Service account ${SA_EMAIL} configured successfully"
```

## Related Resources

- IAM Documentation: https://cloud.google.com/iam/docs
- Workload Identity Federation: https://cloud.google.com/iam/docs/workload-identity-federation
- Service Account Best Practices: https://cloud.google.com/iam/docs/best-practices-for-using-service-accounts
- Vertex AI Authentication: https://cloud.google.com/vertex-ai/docs/authentication
- IAM Conditions: https://cloud.google.com/iam/docs/conditions-overview
