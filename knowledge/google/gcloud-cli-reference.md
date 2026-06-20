# gcloud CLI Reference

> Source: https://cloud.google.com/sdk/gcloud/reference
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

The `gcloud` command-line interface is the primary CLI for Google Cloud services. Commands follow the pattern:

```
gcloud [GROUP] [COMMAND] [FLAGS] [POSITIONAL_ARGS]
```

## Global Flags

These flags can be used with any command:

| Flag | Description |
|------|-------------|
| `--account=ACCOUNT` | Google Cloud account to use |
| `--billing-project=PROJECT` | Project for billing quota |
| `--configuration=CONFIGURATION` | Named configuration to use |
| `--flags-file=YAML_FILE` | YAML file of flags |
| `--flatten=[KEY,...]` | Flatten resource field keys |
| `--format=FORMAT` | Output format (json, yaml, csv, table, text, none) |
| `--help`, `-h` | Show help |
| `--impersonate-service-account=EMAIL` | Run as this service account |
| `--log-http` | Log HTTP requests/responses |
| `--project=PROJECT` | Google Cloud project ID |
| `--quiet`, `-q` | Disable interactive prompts |
| `--trace-token=TOKEN` | Token for debugging |
| `--user-output-enabled` | Print output to stdout |
| `--verbosity=VERBOSITY` | Verbosity level (debug, info, warning, error, critical, none) |
| `--version`, `-v` | Print gcloud version |

## Output Formats

```bash
# JSON output
gcloud projects list --format=json

# YAML output
gcloud projects list --format=yaml

# Table with specific fields
gcloud projects list --format="table(projectId, name, projectNumber)"

# CSV
gcloud projects list --format="csv(projectId, name)"

# Get single value
gcloud config get-value project
gcloud projects describe PROJECT_ID --format="value(projectNumber)"

# Filter results
gcloud projects list --filter="name:my-project"
gcloud services list --enabled --filter="name:aiplatform"
```

## Core Commands

### gcloud auth

Authentication and authorization management.

```bash
# Login interactively
gcloud auth login

# Login with service account
gcloud auth activate-service-account --key-file=key.json

# List accounts
gcloud auth list

# Print access token
gcloud auth print-access-token

# Print identity token
gcloud auth print-identity-token

# Revoke credentials
gcloud auth revoke [ACCOUNT]
gcloud auth revoke --all

# Application Default Credentials
gcloud auth application-default login
gcloud auth application-default print-access-token
gcloud auth application-default set-quota-project PROJECT_ID
gcloud auth application-default revoke
```

### gcloud config

Configuration management.

```bash
# View all configuration
gcloud config list

# Set property
gcloud config set core/project PROJECT_ID
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Get property value
gcloud config get-value project
gcloud config get-value compute/region

# Unset property
gcloud config unset compute/zone

# Configuration profiles
gcloud config configurations create dev-config
gcloud config configurations list
gcloud config configurations activate dev-config
gcloud config configurations describe
gcloud config configurations delete config-name
```

### gcloud projects

Project lifecycle management.

```bash
# List projects
gcloud projects list
gcloud projects list --filter="lifecycleState=ACTIVE"

# Create project
gcloud projects create PROJECT_ID \
  --name="Display Name" \
  --organization=ORG_ID

# Describe project
gcloud projects describe PROJECT_ID

# Update project
gcloud projects update PROJECT_ID --name="New Name"

# Delete project
gcloud projects delete PROJECT_ID

# Undelete project (within 30 days)
gcloud projects undelete PROJECT_ID

# Get IAM policy
gcloud projects get-iam-policy PROJECT_ID

# Add IAM binding
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/editor"

# Remove IAM binding
gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/editor"

# Set IAM policy from file
gcloud projects set-iam-policy PROJECT_ID policy.json
```

### gcloud services

API/service management.

```bash
# List all available services
gcloud services list --available

# List enabled services
gcloud services list --enabled

# Enable a service
gcloud services enable SERVICE_NAME
gcloud services enable aiplatform.googleapis.com

# Enable multiple services
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com

# Disable a service
gcloud services disable SERVICE_NAME

# Get service info
gcloud services describe SERVICE_NAME

# Filter services
gcloud services list --enabled --filter="name:aiplatform"
```

### gcloud iam

IAM management.

```bash
# List predefined roles
gcloud iam roles list

# List custom roles in project
gcloud iam roles list --project=PROJECT_ID

# Describe a role
gcloud iam roles describe roles/aiplatform.user

# Create custom role
gcloud iam roles create ROLE_ID \
  --project=PROJECT_ID \
  --title="Role Title" \
  --description="Role description" \
  --permissions=permission1,permission2

# Service accounts
gcloud iam service-accounts list
gcloud iam service-accounts create SA_ID \
  --display-name="Service Account Name" \
  --description="Description"
gcloud iam service-accounts describe SA_EMAIL
gcloud iam service-accounts delete SA_EMAIL

# Create service account key
gcloud iam service-accounts keys create key.json \
  --iam-account=SA_EMAIL

# List service account keys
gcloud iam service-accounts keys list \
  --iam-account=SA_EMAIL

# Delete service account key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=SA_EMAIL

# Grant role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/aiplatform.user"

# Add IAM binding to service account resource
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="user:user@example.com" \
  --role="roles/iam.serviceAccountUser"
```

## Vertex AI Commands (gcloud ai)

### Endpoints

```bash
# List endpoints
gcloud ai endpoints list --region=REGION

# Create endpoint
gcloud ai endpoints create \
  --display-name=NAME \
  --region=REGION

# Describe endpoint
gcloud ai endpoints describe ENDPOINT_ID --region=REGION

# Deploy model to endpoint
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --model=MODEL_ID \
  --display-name=DEPLOYED_MODEL_NAME \
  --machine-type=MACHINE_TYPE \
  --min-replica-count=MIN \
  --max-replica-count=MAX \
  --region=REGION

# Undeploy model from endpoint
gcloud ai endpoints undeploy-model ENDPOINT_ID \
  --deployed-model-id=DEPLOYED_MODEL_ID \
  --region=REGION

# Delete endpoint
gcloud ai endpoints delete ENDPOINT_ID --region=REGION

# Make prediction
gcloud ai endpoints predict ENDPOINT_ID \
  --json-request=request.json \
  --region=REGION

# Raw prediction
gcloud ai endpoints raw-predict ENDPOINT_ID \
  --http-headers=Content-Type=application/json \
  --request=request.json \
  --region=REGION
```

### Models

```bash
# List models
gcloud ai models list --region=REGION

# Describe model
gcloud ai models describe MODEL_ID --region=REGION

# Upload model
gcloud ai models upload \
  --display-name=NAME \
  --container-image-uri=IMAGE_URI \
  --artifact-uri=GCS_URI \
  --region=REGION

# Delete model
gcloud ai models delete MODEL_ID --region=REGION

# List model evaluations
gcloud ai models list-evaluations MODEL_ID --region=REGION
```

### Batch Prediction Jobs

```bash
# List batch jobs
gcloud ai batch-prediction-jobs list --region=REGION

# Create batch job
gcloud ai batch-prediction-jobs create \
  --display-name=NAME \
  --model=MODEL_ID \
  --input-paths=gs://bucket/input.jsonl \
  --input-format=jsonl \
  --output-path=gs://bucket/output/ \
  --output-format=jsonl \
  --machine-type=MACHINE_TYPE \
  --region=REGION

# Describe batch job
gcloud ai batch-prediction-jobs describe JOB_ID --region=REGION

# Cancel batch job
gcloud ai batch-prediction-jobs cancel JOB_ID --region=REGION
```

### Custom Training Jobs

```bash
# List training jobs
gcloud ai custom-jobs list --region=REGION

# Create custom training job
gcloud ai custom-jobs create \
  --display-name=NAME \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=IMAGE_URI \
  --region=REGION

# Describe training job
gcloud ai custom-jobs describe JOB_ID --region=REGION

# Cancel training job
gcloud ai custom-jobs cancel JOB_ID --region=REGION

# Stream logs
gcloud ai custom-jobs stream-logs JOB_ID --region=REGION
```

### Pipeline Jobs

```bash
# List pipeline jobs
gcloud ai pipeline-jobs list --region=REGION

# Create pipeline job
gcloud ai pipeline-jobs create \
  --display-name=NAME \
  --pipeline-spec-uri=GCS_URI \
  --region=REGION

# Describe pipeline job
gcloud ai pipeline-jobs describe JOB_ID --region=REGION

# Cancel pipeline job
gcloud ai pipeline-jobs cancel JOB_ID --region=REGION
```

### Indexes (Vector Search)

```bash
# List indexes
gcloud ai indexes list --region=REGION

# Create index
gcloud ai indexes create \
  --display-name=NAME \
  --metadata-file=metadata.json \
  --region=REGION

# Describe index
gcloud ai indexes describe INDEX_ID --region=REGION

# Delete index
gcloud ai indexes delete INDEX_ID --region=REGION

# List index endpoints
gcloud ai index-endpoints list --region=REGION
```

## Cloud Storage Commands

### gcloud storage (Newer)

```bash
# List buckets
gcloud storage ls

# List objects
gcloud storage ls gs://my-bucket/
gcloud storage ls gs://my-bucket/path/

# Copy files
gcloud storage cp local-file.txt gs://my-bucket/
gcloud storage cp gs://my-bucket/file.txt local-file.txt
gcloud storage cp -r local-dir/ gs://my-bucket/dir/  # Recursive

# Move/rename
gcloud storage mv gs://bucket/old.txt gs://bucket/new.txt

# Delete
gcloud storage rm gs://my-bucket/file.txt
gcloud storage rm -r gs://my-bucket/dir/  # Recursive

# Create bucket
gcloud storage buckets create gs://my-bucket \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe bucket
gcloud storage buckets describe gs://my-bucket

# List bucket IAM
gcloud storage buckets get-iam-policy gs://my-bucket

# Add bucket IAM
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### gsutil (Legacy, Still Works)

```bash
# List
gsutil ls gs://my-bucket/

# Copy
gsutil cp local.txt gs://bucket/
gsutil -m cp -r local-dir/ gs://bucket/  # Parallel recursive

# Move
gsutil mv gs://bucket/old.txt gs://bucket/new.txt

# Delete
gsutil rm gs://bucket/file.txt
gsutil rm -r gs://bucket/dir/  # Recursive

# Create bucket
gsutil mb -l us-central1 gs://my-bucket

# Sync directories
gsutil -m rsync -r local-dir/ gs://bucket/path/

# Set bucket ACL
gsutil iam ch \
  serviceAccount:sa@project.iam.gserviceaccount.com:objectAdmin \
  gs://my-bucket
```

## BigQuery Commands

```bash
# List datasets
bq ls --project_id=PROJECT_ID

# Create dataset
bq mk --dataset PROJECT_ID:DATASET_ID

# Create table
bq mk --table PROJECT_ID:DATASET_ID.TABLE_ID SCHEMA

# Show table
bq show PROJECT_ID:DATASET_ID.TABLE_ID

# Query
bq query --nouse_legacy_sql 'SELECT * FROM `project.dataset.table` LIMIT 10'

# Load data
bq load --source_format=CSV DATASET_ID.TABLE_ID gs://bucket/file.csv SCHEMA

# Extract to GCS
bq extract DATASET_ID.TABLE_ID gs://bucket/output-*.csv
```

## Compute Engine Commands

```bash
# List instances
gcloud compute instances list

# Create instance
gcloud compute instances create INSTANCE_NAME \
  --machine-type=n1-standard-4 \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --zone=us-central1-a

# SSH into instance
gcloud compute ssh INSTANCE_NAME --zone=ZONE

# Stop/start instance
gcloud compute instances stop INSTANCE_NAME --zone=ZONE
gcloud compute instances start INSTANCE_NAME --zone=ZONE

# Delete instance
gcloud compute instances delete INSTANCE_NAME --zone=ZONE
```

## Kubernetes Engine Commands

```bash
# List clusters
gcloud container clusters list

# Create cluster
gcloud container clusters create CLUSTER_NAME \
  --region=us-central1 \
  --num-nodes=3 \
  --machine-type=n1-standard-4

# Get credentials (configure kubectl)
gcloud container clusters get-credentials CLUSTER_NAME --region=us-central1

# Delete cluster
gcloud container clusters delete CLUSTER_NAME --region=us-central1

# Resize cluster
gcloud container clusters resize CLUSTER_NAME \
  --num-nodes=5 \
  --region=us-central1
```

## Billing Commands

```bash
# List billing accounts
gcloud billing accounts list

# Describe billing account
gcloud billing accounts describe BILLING_ACCOUNT_ID

# List projects linked to billing account
gcloud billing projects list \
  --billing-account=BILLING_ACCOUNT_ID

# Link project to billing account
gcloud billing projects link PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID

# Unlink project from billing
gcloud billing projects unlink PROJECT_ID
```

## Networking Commands

```bash
# List VPC networks
gcloud compute networks list

# Create VPC
gcloud compute networks create NETWORK_NAME --subnet-mode=auto

# List subnets
gcloud compute networks subnets list

# List firewall rules
gcloud compute firewall-rules list

# Create firewall rule
gcloud compute firewall-rules create RULE_NAME \
  --direction=INGRESS \
  --priority=1000 \
  --network=NETWORK_NAME \
  --action=ALLOW \
  --rules=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0
```

## Logging and Monitoring

```bash
# Read logs
gcloud logging read "resource.type=aiplatform.googleapis.com" --limit=10

# Read logs with filter
gcloud logging read \
  'resource.type="aiplatform.googleapis.com" AND severity=ERROR' \
  --format=json \
  --limit=50

# List log sinks
gcloud logging sinks list

# Create log export sink
gcloud logging sinks create SINK_NAME \
  storage.googleapis.com/BUCKET_NAME \
  --log-filter='resource.type="aiplatform.googleapis.com"'

# List monitoring policies
gcloud alpha monitoring policies list
```

## Useful Output Formatting Examples

```bash
# Get project number
gcloud projects describe PROJECT_ID --format="value(projectNumber)"

# Get all active project IDs as list
gcloud projects list --filter="lifecycleState=ACTIVE" --format="value(projectId)"

# Get endpoint resource name
gcloud ai endpoints list --region=us-central1 \
  --filter="displayName=my-endpoint" \
  --format="value(name)"

# JSON output piped to jq
gcloud projects list --format=json | jq '.[].projectId'

# Loop through projects
gcloud projects list --format="value(projectId)" | while read proj; do
  echo "Processing: $proj"
done
```

## Related Resources

- Full gcloud reference: https://cloud.google.com/sdk/gcloud/reference
- gcloud cheat sheet: https://cloud.google.com/sdk/docs/cheatsheet
- gcloud installation: https://cloud.google.com/sdk/docs/install
- gcloud release notes: https://cloud.google.com/sdk/docs/release-notes
