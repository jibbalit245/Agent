# Google Cloud SDK (gcloud CLI) Installation

> Source: https://cloud.google.com/sdk/docs/install
> Note: The Google Cloud documentation URL redirects to docs.cloud.google.com which returned HTTP 403. Content compiled from official Google Cloud documentation knowledge base.
> Fetched: 2026-06-20

## Overview

The Google Cloud CLI (`gcloud`) is a command-line tool for managing Google Cloud resources. It includes:
- `gcloud` - Main CLI for Google Cloud services
- `gsutil` - Cloud Storage operations (being replaced by `gcloud storage`)
- `bq` - BigQuery operations
- `kubectl` - Kubernetes cluster management (optional component)

## System Requirements

| OS | Python | Notes |
|----|--------|-------|
| Linux (64-bit) | Python 3.8+ | x86_64 or ARM |
| macOS 10.15+ | Python 3.8+ | Intel or Apple Silicon |
| Windows 10/11 | Python 3.8+ | 64-bit |

Python 3 is bundled with the SDK installer (no separate Python installation needed).

## Installation

### Linux / macOS - Interactive Installer

```bash
# Download and run the installation script
curl https://sdk.cloud.google.com | bash

# Or for a specific version
curl https://sdk.cloud.google.com | bash -s -- --version=VERSION

# Restart shell or source the completion script
exec -l $SHELL

# Initialize
gcloud init
```

### macOS - Homebrew

```bash
# Install Google Cloud SDK
brew install --cask google-cloud-sdk

# Or just the CLI
brew install google-cloud-sdk

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"
source "$(brew --prefix)/share/google-cloud-sdk/completion.zsh.inc"
```

### Linux - Package Manager (Debian/Ubuntu)

```bash
# Add the Cloud SDK distribution URI as a package source
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install
sudo apt-get update && sudo apt-get install google-cloud-cli

# Initialize
gcloud init
```

### Linux - Package Manager (RPM-based: Fedora/RHEL/CentOS)

```bash
# Add the Cloud SDK repo
sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el8-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM

# Install
sudo dnf install google-cloud-cli

# Initialize
gcloud init
```

### Windows - Installer

1. Download the installer from: https://cloud.google.com/sdk/docs/install#windows
2. Run `GoogleCloudSDKInstaller.exe`
3. Follow the installation wizard
4. The installer automatically runs `gcloud init`

**Or using PowerShell:**
```powershell
# Download installer
(New-Object Net.WebClient).DownloadFile(
  "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe",
  "$env:Temp\GoogleCloudSDKInstaller.exe"
)

# Run installer
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### Windows - Chocolatey

```powershell
choco install gcloudsdk
```

### Docker

```bash
# Use the official Google Cloud SDK Docker image
docker pull gcr.io/google.com/cloudsdktool/google-cloud-cli:latest

# Run interactively
docker run -it gcr.io/google.com/cloudsdktool/google-cloud-cli:latest gcloud auth login

# Or mount credentials
docker run \
  -v ~/.config/gcloud:/root/.config/gcloud \
  gcr.io/google.com/cloudsdktool/google-cloud-cli:latest \
  gcloud projects list
```

## Initialization

### First-Time Setup

```bash
gcloud init
```

This interactive command:
1. Authenticates your account
2. Sets default project
3. Sets default region/zone

### Non-Interactive Initialization

```bash
# Set project directly
gcloud config set project PROJECT_ID

# Set default region and zone
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Authenticate
gcloud auth login
gcloud auth application-default login
```

## Authentication

### User Account Authentication

```bash
# Login with user account (opens browser)
gcloud auth login

# Login with service account
gcloud auth activate-service-account \
  --key-file=/path/to/service-account-key.json

# List authenticated accounts
gcloud auth list

# Show current active account
gcloud config get-value account

# Revoke credentials
gcloud auth revoke USER_EMAIL
```

### Application Default Credentials (ADC)

```bash
# Set up ADC for local development
gcloud auth application-default login

# Set quota project for ADC
gcloud auth application-default set-quota-project PROJECT_ID

# Print ADC access token
gcloud auth application-default print-access-token

# Revoke ADC
gcloud auth application-default revoke
```

## Configuration Management

### Manage Configurations (Profiles)

```bash
# Create a new configuration
gcloud config configurations create my-dev-config

# List configurations
gcloud config configurations list

# Activate a configuration
gcloud config configurations activate my-dev-config

# Describe current configuration
gcloud config configurations describe

# Delete a configuration
gcloud config configurations delete my-old-config
```

### Set Configuration Properties

```bash
# View all properties
gcloud config list

# Set properties
gcloud config set project PROJECT_ID
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
gcloud config set core/account user@example.com

# Unset property
gcloud config unset compute/zone

# Get specific property
gcloud config get-value project
gcloud config get-value compute/region
```

## Updating the SDK

```bash
# Check current version
gcloud version

# Update to latest
gcloud components update

# Install specific version
gcloud components update --version VERSION

# List available components
gcloud components list
```

## Installing Additional Components

```bash
# Install kubectl
gcloud components install kubectl

# Install beta commands
gcloud components install beta

# Install alpha commands
gcloud components install alpha

# Install gsutil (legacy, now bundled)
gcloud components install gsutil

# Install Cloud Datalab
gcloud components install datalab

# Uninstall a component
gcloud components remove COMPONENT_ID
```

## Common Commands Reference

### Project Management

```bash
gcloud projects list
gcloud projects create PROJECT_ID --name="Name"
gcloud projects describe PROJECT_ID
gcloud projects delete PROJECT_ID
gcloud config set project PROJECT_ID
```

### API Management

```bash
gcloud services list --enabled
gcloud services enable SERVICE_NAME
gcloud services disable SERVICE_NAME
```

### IAM

```bash
gcloud projects get-iam-policy PROJECT_ID
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/viewer"
gcloud iam roles list --project=PROJECT_ID
gcloud iam service-accounts list
```

### Vertex AI Specific

```bash
# List Vertex AI endpoints
gcloud ai endpoints list --region=us-central1

# Describe endpoint
gcloud ai endpoints describe ENDPOINT_ID --region=us-central1

# List models
gcloud ai models list --region=us-central1

# List batch prediction jobs
gcloud ai batch-prediction-jobs list --region=us-central1
```

### Cloud Storage

```bash
# Using gcloud storage (newer)
gcloud storage ls gs://my-bucket/
gcloud storage cp local-file.txt gs://my-bucket/
gcloud storage mv gs://bucket/old-name.txt gs://bucket/new-name.txt
gcloud storage rm gs://bucket/file.txt
gcloud storage buckets create gs://new-bucket --location=us-central1

# Using gsutil (older, still works)
gsutil ls gs://my-bucket/
gsutil cp local-file.txt gs://my-bucket/
gsutil mb gs://new-bucket
```

## Environment Variables

```bash
# Skip confirmations
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

# Set project
export GOOGLE_CLOUD_PROJECT=my-project

# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json

# Disable usage reporting
export CLOUDSDK_CORE_DISABLE_USAGE_REPORTING=true

# Set custom configuration directory
export CLOUDSDK_CONFIG=/path/to/config/dir
```

## Using gcloud in Scripts

```bash
#!/bin/bash
set -e

# Get auth token for API calls
TOKEN=$(gcloud auth print-access-token)

# Use with curl
curl -H "Authorization: Bearer ${TOKEN}" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/..."

# Get project number
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format='value(projectNumber)')

# Check if API is enabled
if gcloud services list --enabled --filter="name:aiplatform.googleapis.com" --format="value(name)" | grep -q aiplatform; then
  echo "Vertex AI API is enabled"
fi
```

## Troubleshooting

### Common Issues

```bash
# Reset credentials
gcloud auth revoke --all
gcloud auth login

# Reset ADC
gcloud auth application-default revoke
gcloud auth application-default login

# Check SDK version
gcloud version

# Run diagnostics
gcloud info

# Clear SDK cache
gcloud components update
```

### Check Installation

```bash
# Verify gcloud is in PATH
which gcloud

# Check version
gcloud version

# Run info to see configuration
gcloud info
```

### Behind a Proxy

```bash
# Set proxy in gcloud config
gcloud config set proxy/type http
gcloud config set proxy/address PROXY_HOST
gcloud config set proxy/port PROXY_PORT

# Or set environment variables
export HTTPS_PROXY=http://PROXY_HOST:PROXY_PORT
export HTTP_PROXY=http://PROXY_HOST:PROXY_PORT
```

## SDK Directory Structure

After installation, the SDK is typically located at:
- Linux/macOS: `~/google-cloud-sdk/`
- Windows: `C:\Users\USERNAME\AppData\Local\Google\Cloud SDK\`

Key subdirectories:
```
google-cloud-sdk/
├── bin/               # Executable scripts (gcloud, gsutil, bq)
├── lib/               # Python libraries
├── platform/          # Platform-specific files
├── completion.bash.inc  # Bash completion
├── completion.zsh.inc   # Zsh completion
└── path.bash.inc      # PATH setup for bash
```

## Shell Completion Setup

### Bash

```bash
# Add to ~/.bashrc or ~/.bash_profile
source /path/to/google-cloud-sdk/completion.bash.inc
source /path/to/google-cloud-sdk/path.bash.inc
```

### Zsh

```bash
# Add to ~/.zshrc
source /path/to/google-cloud-sdk/completion.zsh.inc
source /path/to/google-cloud-sdk/path.zsh.inc
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
source /path/to/google-cloud-sdk/path.fish.inc
```

## Related Resources

- gcloud CLI Reference: https://cloud.google.com/sdk/gcloud/reference
- Release Notes: https://cloud.google.com/sdk/docs/release-notes
- SDK Source Code: https://github.com/google-cloud/google-cloud-sdk
- gcloud Cheat Sheet: https://cloud.google.com/sdk/docs/cheatsheet
