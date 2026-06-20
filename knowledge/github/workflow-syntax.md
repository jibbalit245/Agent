# GitHub Actions — Complete Workflow Syntax Reference
> Source: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
> Fetched: 2026-06-20

## Overview

GitHub Actions workflows are YAML files in `.github/workflows/`. Each workflow file can define one or more jobs that run in response to events.

---

## Top-Level Keys

```yaml
name: string          # Workflow display name (optional)
run-name: string      # Run name displayed in GitHub UI (can use expressions)
on: event-config      # REQUIRED: what triggers this workflow
env:                  # Workflow-level environment variables
  KEY: value
defaults:             # Workflow-level defaults for run steps
  run:
    shell: bash
    working-directory: src
concurrency:          # Concurrency group settings
  group: string
  cancel-in-progress: bool
jobs:                 # REQUIRED: job definitions
  job-id:
    ...
permissions:          # GITHUB_TOKEN permissions (workflow level)
  contents: read
```

---

## `on:` — Workflow Triggers

### Push and Pull Request

```yaml
on:
  push:
    branches:
      - main
      - 'feature/**'   # glob patterns
    branches-ignore:
      - '**-wip'
    tags:
      - 'v*'
    tags-ignore:
      - 'v*-beta'
    paths:
      - 'src/**'
      - '**.py'
    paths-ignore:
      - 'docs/**'
      - '**.md'
  
  pull_request:
    types:             # default: [opened, synchronize, reopened]
      - opened
      - synchronize
      - reopened
      - labeled
      - unlabeled
      - ready_for_review
    branches:
      - main
    paths:
      - 'src/**'
  
  pull_request_target:   # like pull_request but with access to secrets
    types: [opened, synchronize]
```

### Manual and Scheduled

```yaml
on:
  workflow_dispatch:          # Manual trigger from GitHub UI or API
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options: ['staging', 'production']
      debug:
        type: boolean
        default: false
      tag:
        type: string
  
  schedule:
    - cron: '0 2 * * 1'      # Every Monday at 2am UTC
    - cron: '0 0 1 * *'      # First of every month
```

### Repository Events

```yaml
on:
  create:               # branch or tag created
  delete:               # branch or tag deleted
  fork:                 # repository forked
  watch:                # repository starred
  
  release:
    types: [published, created, edited, deleted, prereleased, released]
  
  issues:
    types: [opened, closed, reopened, edited, labeled, unlabeled, assigned]
  
  issue_comment:
    types: [created, edited, deleted]
  
  pull_request_review:
    types: [submitted, edited, dismissed]
  
  pull_request_review_comment:
    types: [created, edited, deleted]
  
  discussion:
    types: [created, answered, labeled]
  
  label:
    types: [created, edited, deleted]
  
  milestone:
    types: [created, closed, opened, edited, deleted]
  
  project:
    types: [created, updated, closed, reopened, edited, deleted]
  
  commit_comment:
    types: [created]
  
  status:               # git commit status changed
  
  check_run:
    types: [created, rerequested, completed, requested_action]
  
  check_suite:
    types: [completed]
  
  deployment:
  deployment_status:
  
  page_build:           # GitHub Pages build
  
  public:               # repo changed to public
  
  registry_package:
    types: [published, updated]
  
  repository_dispatch:  # custom event via REST API
    types: [custom-event-type]
  
  workflow_call:         # called from another workflow
    inputs:
      config-path:
        required: true
        type: string
    secrets:
      token:
        required: true
    outputs:
      result:
        description: "Job result"
        value: ${{ jobs.my-job.outputs.result }}
  
  workflow_run:          # trigger when another workflow runs
    workflows: ["CI"]
    types: [completed, requested, in_progress]
    branches: [main]
  
  merge_group:           # merge queue events
    types: [checks_requested]
```

---

## `jobs.<job_id>` — Job Configuration

```yaml
jobs:
  my-job:
    name: "Human-readable name"            # displayed in UI
    runs-on: ubuntu-latest                 # REQUIRED: runner
    needs: [other-job, another-job]        # job dependencies
    if: ${{ github.event_name == 'push' }} # conditional execution
    environment: production                # deployment environment
    concurrency:
      group: deploy-${{ github.ref }}
      cancel-in-progress: false
    outputs:
      result: ${{ steps.my-step.outputs.value }}
    env:
      JOB_VAR: value
    defaults:
      run:
        shell: bash
        working-directory: ./src
    timeout-minutes: 60                    # default 360, max 6 hours
    continue-on-error: false               # default false
    permissions:
      contents: read
      packages: write
    
    strategy:                              # matrix builds
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: [18, 20]
      fail-fast: false                     # default true
      max-parallel: 4
    
    container:                             # run job inside a container
      image: node:18
      credentials:
        username: ${{ secrets.DOCKER_USER }}
        password: ${{ secrets.DOCKER_PASS }}
      env:
        NODE_ENV: test
      ports:
        - 80
      volumes:
        - /tmp:/tmp
      options: --cpus 1
    
    services:                              # sidecar containers
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps: [...]
```

---

## `runs-on:` — Runners

### GitHub-Hosted Runners

```yaml
runs-on: ubuntu-latest      # Ubuntu 22.04 (2 CPU, 7GB RAM, 14GB disk)
runs-on: ubuntu-22.04
runs-on: ubuntu-20.04
runs-on: ubuntu-24.04       # (check availability)
runs-on: macos-latest       # macOS 14 (3 CPU, 14GB RAM)
runs-on: macos-14
runs-on: macos-13
runs-on: windows-latest     # Windows Server 2022 (2 CPU, 7GB RAM)
runs-on: windows-2022
runs-on: windows-2019
```

### Larger Runners (GitHub Team & Enterprise Cloud)

```yaml
# Ubuntu
runs-on: ubuntu-latest-4-cores    # 4 CPU, 16GB RAM
runs-on: ubuntu-latest-8-cores    # 8 CPU, 32GB RAM
runs-on: ubuntu-latest-16-cores   # 16 CPU, 64GB RAM
runs-on: ubuntu-latest-32-cores   # 32 CPU, 128GB RAM

# ARM
runs-on: ubuntu-latest-arm64-4-cores
runs-on: ubuntu-latest-arm64-8-cores

# GPU (available to select plans)
runs-on: ubuntu-latest-gpu
```

### Self-Hosted Runners

```yaml
runs-on: self-hosted
runs-on: [self-hosted, linux, x64, gpu]
runs-on: [self-hosted, windows, arm64]
```

### Dynamic Runner Selection

```yaml
runs-on: ${{ matrix.runner }}

strategy:
  matrix:
    runner: [ubuntu-latest, macos-latest, windows-latest]
```

---

## `steps:` — Step Configuration

```yaml
steps:
  - name: "Step name"                # optional display name
    id: my-step                      # optional ID for output references
    
    # Option A: Use an action
    uses: actions/checkout@v4
    with:
      ref: main
      token: ${{ secrets.GITHUB_TOKEN }}
    
    # Option B: Run a command
    run: |
      echo "Hello World"
      python script.py
    
    # Common options for both:
    if: ${{ success() }}             # conditional
    env:
      MY_VAR: value
    continue-on-error: false
    timeout-minutes: 5
    working-directory: ./subdir      # override for run steps
    shell: bash                      # bash, sh, pwsh, python, cmd, etc.
```

### Shell Options

| Shell | Description |
|-------|-------------|
| `bash` | Bash (default on Linux/macOS) |
| `sh` | Posix sh |
| `pwsh` | PowerShell Core |
| `powershell` | Windows PowerShell |
| `cmd` | Windows CMD |
| `python` | Python inline script |

---

## `strategy.matrix` — Matrix Builds

```yaml
strategy:
  matrix:
    # Simple matrix — creates OS × node combinations
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [16, 18, 20]
    
    # Include: add specific combinations
    include:
      - os: ubuntu-latest
        node-version: 20
        extra-flag: "--experimental"
    
    # Exclude: remove specific combinations
    exclude:
      - os: windows-latest
        node-version: 16
  
  fail-fast: false    # don't cancel all on first failure
  max-parallel: 3     # limit concurrent jobs

# Access matrix values
steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ matrix.node-version }}
  - run: npm test -- --platform=${{ matrix.os }}
```

---

## `concurrency:` — Concurrency Control

```yaml
# Workflow level
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true    # cancel previous run in same group

# Job level
jobs:
  deploy:
    concurrency:
      group: production-deploy
      cancel-in-progress: false  # queue instead of cancel
```

**Common patterns:**
```yaml
# Cancel old PR runs on new push
group: PR-${{ github.event.pull_request.number }}
cancel-in-progress: true

# Queue deploys, don't cancel
group: deploy-production
cancel-in-progress: false
```

---

## `permissions:` — GITHUB_TOKEN Scopes

```yaml
permissions:
  actions: read | write | none
  checks: read | write | none
  contents: read | write | none
  deployments: read | write | none
  id-token: read | write | none   # for OIDC
  issues: read | write | none
  discussions: read | write | none
  packages: read | write | none
  pages: read | write | none
  pull-requests: read | write | none
  repository-projects: read | write | none
  security-events: read | write | none
  statuses: read | write | none
```

**Minimum permissions (security best practice):**
```yaml
permissions:
  contents: read    # start with read-only
  # add only what's needed
```

**No permissions (most restrictive):**
```yaml
permissions: {}
```

---

## `environment:` — Deployment Environments

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://myapp.com  # optional deployment URL
    steps:
      - run: deploy.sh
        env:
          PROD_SECRET: ${{ secrets.PROD_SECRET }}  # env secrets available here
```

Environments support:
- **Protection rules**: Required reviewers before deployment
- **Wait timer**: Delay before deployment
- **Branch restrictions**: Only allow specific branches to deploy

---

## `outputs:` — Job Outputs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.get-version.outputs.version }}
    steps:
      - id: get-version
        run: |
          VERSION=$(cat version.txt)
          echo "version=$VERSION" >> $GITHUB_OUTPUT
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: deploy --version ${{ needs.build.outputs.version }}
```

---

## Expressions and Contexts

### Expression Syntax

```yaml
if: ${{ <expression> }}
name: ${{ vars.ENVIRONMENT }}-${{ github.run_number }}
```

### Available Contexts

| Context | Description |
|---------|-------------|
| `github` | Workflow run info, event payload, repo info |
| `env` | Environment variables |
| `vars` | Repository/org variables |
| `job` | Current job info (status, container) |
| `jobs` | (reusable workflows) Results of all jobs |
| `steps` | Results of previous steps |
| `runner` | Runner information |
| `secrets` | Secret values |
| `strategy` | Matrix strategy |
| `matrix` | Current matrix values |
| `needs` | Results of dependency jobs |
| `inputs` | Inputs from workflow_dispatch or workflow_call |

### Common github Context Properties

```yaml
${{ github.actor }}              # user who triggered
${{ github.event_name }}         # push, pull_request, etc.
${{ github.ref }}                # refs/heads/main
${{ github.ref_name }}           # main
${{ github.sha }}                # commit SHA
${{ github.repository }}         # owner/repo
${{ github.repository_owner }}   # owner
${{ github.workspace }}          # /home/runner/work/repo/repo
${{ github.run_id }}             # unique run ID
${{ github.run_number }}         # sequential run number
${{ github.job }}                # job ID
${{ github.event.pull_request.number }}
${{ github.event.release.tag_name }}
```

### Conditional Functions

```yaml
if: ${{ success() }}             # previous steps all succeeded
if: ${{ failure() }}             # any previous step failed
if: ${{ cancelled() }}           # workflow was cancelled
if: ${{ always() }}              # run regardless of status

# Combining conditions
if: ${{ success() && github.ref == 'refs/heads/main' }}
if: ${{ failure() || cancelled() }}

# Contains, startsWith, endsWith
if: ${{ contains(github.event.head_commit.message, '[skip ci]') }}
if: ${{ startsWith(github.ref, 'refs/tags/v') }}
if: ${{ endsWith(github.actor, '[bot]') }}
```

---

## Environment Variables

### Setting Variables

```yaml
# Workflow level
env:
  PYTHONPATH: src
  LOG_LEVEL: INFO

jobs:
  test:
    env:
      DATABASE_URL: postgres://localhost/test  # job level
    steps:
      - run: python test.py
        env:
          DEBUG: true  # step level (highest priority)
```

### Special Environment Files

```bash
# Set output value
echo "result=success" >> $GITHUB_OUTPUT

# Set environment variable for subsequent steps
echo "MY_VAR=hello" >> $GITHUB_ENV

# Set step summary (shown in GitHub UI)
echo "## Test Results" >> $GITHUB_STEP_SUMMARY
echo "All 42 tests passed!" >> $GITHUB_STEP_SUMMARY

# Add directory to PATH
echo "/path/to/tools" >> $GITHUB_PATH
```

---

## Reusable Workflows

### Calling a Reusable Workflow

```yaml
jobs:
  call-reusable:
    uses: ./.github/workflows/reusable.yml         # same repo
    uses: owner/repo/.github/workflows/ci.yml@main  # external repo
    
    with:
      config: "production"
      enable-debug: true
    
    secrets:
      api-key: ${{ secrets.API_KEY }}
    # or pass all secrets
    secrets: inherit
    
    permissions:
      contents: read
```

### Defining a Reusable Workflow

```yaml
# .github/workflows/reusable.yml
on:
  workflow_call:
    inputs:
      config:
        required: true
        type: string
      enable-debug:
        required: false
        type: boolean
        default: false
    secrets:
      api-key:
        required: true
    outputs:
      result:
        description: "Build result"
        value: ${{ jobs.build.outputs.result }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      result: ${{ steps.build.outputs.result }}
    steps:
      - uses: actions/checkout@v4
      - id: build
        run: |
          echo "Building with config: ${{ inputs.config }}"
          echo "result=success" >> $GITHUB_OUTPUT
        env:
          API_KEY: ${{ secrets.api-key }}
```

---

## Composite Actions

Create reusable action sequences (not full workflows):

```yaml
# .github/actions/setup-ml/action.yml
name: 'Setup ML Environment'
description: 'Install Python and ML dependencies'

inputs:
  python-version:
    description: 'Python version'
    required: true
    default: '3.11'

outputs:
  python-path:
    description: 'Path to Python executable'
    value: ${{ steps.setup-python.outputs.python-path }}

runs:
  using: 'composite'
  steps:
    - uses: actions/setup-python@v5
      id: setup-python
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
    
    - run: pip install -r requirements.txt
      shell: bash
```

Usage:
```yaml
steps:
  - uses: ./.github/actions/setup-ml
    with:
      python-version: '3.11'
```

---

## OIDC — Cloud Authentication without Secrets

OpenID Connect (OIDC) lets your Actions workflows authenticate to cloud providers without storing long-lived credentials.

### Setup: AWS

```yaml
permissions:
  id-token: write   # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/MyRole
          aws-region: us-east-1
      
      - run: aws s3 cp ./dist s3://my-bucket/ --recursive
```

### Setup: Azure

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - run: az webapp deploy ...
```

### Setup: GCP

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123/locations/global/workloadIdentityPools/my-pool/providers/my-provider'
          service_account: 'my-sa@my-project.iam.gserviceaccount.com'
      
      - run: gcloud deploy ...
```

### OIDC Token Claims

The OIDC token includes these claims that cloud providers can use for access control:

| Claim | Example | Description |
|-------|---------|-------------|
| `sub` | `repo:owner/repo:ref:refs/heads/main` | Subject |
| `iss` | `https://token.actions.githubusercontent.com` | Issuer |
| `aud` | Custom audience | Audience |
| `repository` | `owner/repo` | Repository |
| `ref` | `refs/heads/main` | Git ref |
| `job_workflow_ref` | `owner/repo/.github/workflows/ci.yml@main` | Reusable workflow ref |
| `actor` | `username` | GitHub user |
| `environment` | `production` | Deployment environment |

---

## Caching

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  id: cache-pip
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Install (only if cache miss)
  if: steps.cache-pip.outputs.cache-hit != 'true'
  run: pip install -r requirements.txt

# Cache npm
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}

# Cache Docker layers
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Cache limits**: 10 GB per repository; LRU eviction after 7 days of no access.

---

## Artifacts

```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-output        # artifact name
    path: dist/               # directory or file
    retention-days: 30        # 1-90 days (default 90)
    if-no-files-found: error  # error, warn, or ignore
    compression-level: 6      # 0-9 (0=no compression)

# Download in another job
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: ./dist

# Download all artifacts
- uses: actions/download-artifact@v4
  with:
    path: ./all-artifacts
    merge-multiple: false
```

---

## Common Actions Reference

| Action | Use Case |
|--------|---------|
| `actions/checkout@v4` | Clone repository |
| `actions/setup-python@v5` | Install Python |
| `actions/setup-node@v4` | Install Node.js |
| `actions/setup-java@v4` | Install Java |
| `actions/cache@v4` | Cache dependencies |
| `actions/upload-artifact@v4` | Save files between jobs |
| `actions/download-artifact@v4` | Restore saved files |
| `actions/github-script@v7` | Run JavaScript with GitHub API |
| `docker/login-action@v3` | Login to container registry |
| `docker/build-push-action@v5` | Build and push Docker images |
| `docker/metadata-action@v5` | Generate Docker tags/labels |
| `docker/setup-buildx-action@v3` | Set up BuildKit |
| `aws-actions/configure-aws-credentials@v4` | AWS OIDC auth |
| `azure/login@v2` | Azure OIDC auth |
| `google-github-actions/auth@v2` | GCP OIDC auth |
| `softprops/action-gh-release@v2` | Create GitHub release |

---

## Sources
- [Workflow syntax for GitHub Actions - GitHub Docs](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Events that trigger workflows - GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [Contexts reference - GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
- [Reusing workflow configurations - GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [Using OIDC with reusable workflows - GitHub Docs](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-hardening-your-deployments/using-openid-connect-with-reusable-workflows)
