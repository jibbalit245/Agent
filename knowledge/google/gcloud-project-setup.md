# Google Cloud Project Setup and Management

> Source: https://cloud.google.com/resource-manager/docs/creating-managing-projects
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

A Google Cloud project is the fundamental organizing unit for Google Cloud resources. Before using Vertex AI or other Google Cloud services, you must create a project and configure it appropriately.

Every resource in Google Cloud must belong to a project. A project consists of:
- **Project ID**: Globally unique identifier (immutable after creation)
- **Project Name**: Human-readable name (mutable)
- **Project Number**: Numerically unique identifier (assigned by Google, immutable)

## Creating a Project

### Via Cloud Console

1. Go to https://console.cloud.google.com
2. Click the project selector in the top bar
3. Click "New Project"
4. Enter a project name
5. Optionally select an organization or billing account
6. Click "Create"

### Via gcloud CLI

```bash
# Create a new project
gcloud projects create PROJECT_ID \
  --name="My Project Name" \
  --organization=ORGANIZATION_ID  # Optional

# Create under a folder
gcloud projects create PROJECT_ID \
  --name="My Project Name" \
  --folder=FOLDER_ID

# Verify creation
gcloud projects describe PROJECT_ID
```

### Via REST API

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://cloudresourcemanager.googleapis.com/v3/projects" \
  -d '{
    "projectId": "my-project-id",
    "displayName": "My Project Name",
    "parent": "organizations/ORGANIZATION_ID"
  }'
```

## Project Naming Rules

**Project ID** requirements:
- Must be 6-30 characters
- Can only contain lowercase letters, digits, and hyphens
- Must start with a letter
- Cannot end with a hyphen
- Must be globally unique across all Google Cloud

**Project Name** requirements:
- 4-30 characters
- Can contain any Unicode characters
- Not required to be unique

## Setting Up a Project for Vertex AI

### Step 1: Select or Create Project

```bash
# List existing projects
gcloud projects list

# Set active project
gcloud config set project PROJECT_ID

# Verify
gcloud config get-value project
```

### Step 2: Enable Billing

A billing account must be linked to use paid services:

```bash
# List billing accounts
gcloud billing accounts list

# Link billing account to project
gcloud billing projects link PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID

# Check billing status
gcloud billing projects describe PROJECT_ID
```

Or via Console: Billing > Manage Billing Accounts > Link

### Step 3: Enable Required APIs

For Vertex AI:
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable additional commonly needed APIs
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  bigquery.googleapis.com

# Verify enabled APIs
gcloud services list --enabled --filter="NAME:aiplatform"
```

### Step 4: Set Up IAM Permissions

```bash
# Get your user email
gcloud config get-value account

# Grant Vertex AI user role to yourself
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/aiplatform.user"

# Grant Storage access (for GCS buckets)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/storage.objectAdmin"
```

### Step 5: Configure Authentication

```bash
# Authenticate with your Google account
gcloud auth login

# Set up Application Default Credentials
gcloud auth application-default login

# Set quota project
gcloud auth application-default set-quota-project PROJECT_ID
```

### Step 6: Create GCS Bucket (for staging)

```bash
# Create bucket in US
gsutil mb -p PROJECT_ID -l US gs://my-staging-bucket/

# Create bucket in specific region
gsutil mb -p PROJECT_ID -l us-central1 gs://my-regional-bucket/

# Or using gcloud (newer approach)
gcloud storage buckets create gs://my-bucket \
  --project=PROJECT_ID \
  --location=us-central1
```

## Managing Projects

### List Projects

```bash
# List all projects you have access to
gcloud projects list

# Filter by name
gcloud projects list --filter="name:my-project"

# List with details
gcloud projects list --format="table(projectId, name, projectNumber, lifecycleState)"
```

### Describe a Project

```bash
gcloud projects describe PROJECT_ID
```

Output includes:
```
createTime: '2024-01-01T00:00:00.000Z'
lifecycleState: ACTIVE
name: My Project Name
parent:
  id: '1234567890'
  type: organization
projectId: my-project-id
projectNumber: '9876543210'
```

### Update a Project

```bash
# Update project name
gcloud projects update PROJECT_ID --name="New Project Name"
```

### Set IAM Policy

```bash
# View IAM policy
gcloud projects get-iam-policy PROJECT_ID

# Add IAM binding
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Remove IAM binding
gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="user:user@example.com" \
  --role="roles/viewer"
```

### Delete a Project

```bash
# Mark for deletion (30-day grace period)
gcloud projects delete PROJECT_ID

# Restore deleted project (within 30 days)
gcloud projects undelete PROJECT_ID
```

**Warning:** Deleting a project:
- Stops billing immediately
- Deletes all resources after 30 days
- Cannot be undone after 30 days

## Project Organization Hierarchy

```
Organization
├── Folder (optional grouping)
│   ├── Project A
│   └── Project B
└── Project C (directly under org)
```

IAM policies inherit from parent resources:
- Organization policies cascade to all projects
- Folder policies cascade to contained projects
- Project policies apply only to that project

## Resource Manager via Python

```python
from google.cloud import resourcemanager_v3

# Create project
client = resourcemanager_v3.ProjectsClient()

project = resourcemanager_v3.Project(
    project_id='my-new-project',
    display_name='My New Project',
    parent='organizations/ORG_ID',  # or 'folders/FOLDER_ID'
)

operation = client.create_project(project=project)
created_project = operation.result()
print(f"Created: {created_project.name}")

# List projects
request = resourcemanager_v3.ListProjectsRequest(
    parent='organizations/ORG_ID'
)
for project in client.list_projects(request=request):
    print(f"{project.project_id}: {project.display_name}")

# Get project
project = client.get_project(name='projects/PROJECT_ID')
```

## Quotas and Limits

| Resource | Default Quota |
|----------|--------------|
| Projects per billing account | 25 (can be increased) |
| Projects per organization | Unlimited (with Organization) |
| Projects per user (no org) | 25 |

Request quota increases:
- Console: IAM & Admin > Quotas
- Or file a support request

## Best Practices

1. **Use separate projects** for dev/staging/production environments
2. **Enable only needed APIs** to maintain security posture
3. **Use labels** to organize and track resources:
   ```bash
   gcloud projects update PROJECT_ID --update-labels=env=production,team=ml
   ```
4. **Set budget alerts** to avoid unexpected charges:
   - Billing > Budgets & Alerts > Create Budget
5. **Use folders** to organize projects at scale
6. **Apply organization policies** for compliance at scale

## Environment Variables for Vertex AI

After setting up a project, configure these environment variables:

```bash
export GOOGLE_CLOUD_PROJECT=my-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json  # If not using gcloud ADC
```

Or in Python:
```python
import os
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

from google import genai
# Will pick up environment variables automatically
client = genai.Client(vertexai=True)
```

## Complete Setup Script

```bash
#!/bin/bash
set -e

PROJECT_ID="my-vertex-ai-project"
REGION="us-central1"
BUCKET_NAME="${PROJECT_ID}-staging"
BILLING_ACCOUNT="BILLING_ACCOUNT_ID"

# Create project
gcloud projects create ${PROJECT_ID} --name="Vertex AI Project"

# Link billing
gcloud billing projects link ${PROJECT_ID} \
  --billing-account=${BILLING_ACCOUNT}

# Enable APIs
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  --project=${PROJECT_ID}

# Set default project
gcloud config set project ${PROJECT_ID}

# Create staging bucket
gcloud storage buckets create gs://${BUCKET_NAME} \
  --project=${PROJECT_ID} \
  --location=${REGION}

# Set up ADC
gcloud auth application-default login
gcloud auth application-default set-quota-project ${PROJECT_ID}

echo "Project setup complete!"
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Staging bucket: gs://${BUCKET_NAME}"
```

## Related Resources

- Cloud Console: https://console.cloud.google.com
- Billing Setup: https://cloud.google.com/billing/docs/how-to/manage-billing-account
- IAM Documentation: https://cloud.google.com/iam/docs
- gcloud CLI Reference: https://cloud.google.com/sdk/gcloud/reference
- Resource Manager API: https://cloud.google.com/resource-manager/docs
