# GitHub Actions for ML/AI Workflows
> Source: https://docs.github.com/en/actions/writing-workflows/quickstart
> Fetched: 2026-06-20

## Overview

GitHub Actions automates software workflows directly in your GitHub repository. For ML/AI projects it handles: model training, evaluation pipelines, dataset preprocessing, Docker builds, and deployment.

## Workflow File Basics

Workflows are **YAML files** stored in `.github/workflows/`. They are triggered by events and execute jobs on runners.

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Training Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:  # allow manual trigger
  schedule:
    - cron: '0 2 * * 0'  # every Sunday at 2am UTC
```

## Triggers (`on:`)

```yaml
on:
  push:
    branches: [main, develop]
    paths:               # only trigger if these paths change
      - 'src/**'
      - 'requirements.txt'
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:     # manual trigger from GitHub UI
    inputs:
      epochs:
        description: 'Number of training epochs'
        default: '10'
        type: string
  schedule:
    - cron: '0 0 * * 1'  # weekly
  release:
    types: [published]
```

## Runners

### Standard GitHub-Hosted Runners

| Runner label | OS | CPU | RAM | Storage |
|-------------|-----|-----|-----|---------|
| `ubuntu-latest` | Ubuntu 22.04 | 2 | 7GB | 14GB |
| `ubuntu-22.04` | Ubuntu 22.04 | 2 | 7GB | 14GB |
| `ubuntu-20.04` | Ubuntu 20.04 | 2 | 7GB | 14GB |
| `macos-latest` | macOS 14 | 3 | 14GB | 14GB |
| `windows-latest` | Windows 2022 | 2 | 7GB | 14GB |

### Larger Runners (Team & Enterprise Cloud Plans)

Available to GitHub Team and Enterprise Cloud customers:

| Runner type | CPU | RAM | Notes |
|------------|-----|-----|-------|
| Ubuntu 4-core | 4 | 16GB | Good for parallel testing |
| Ubuntu 8-core | 8 | 32GB | Medium ML workloads |
| Ubuntu 16-core | 16 | 64GB | Large ML workloads |
| Ubuntu 32-core | 32 | 128GB | Heavy training |
| **GPU runners** | varies | varies | For deep learning training |
| ARM-based | varies | varies | Apple Silicon-compatible |

GPU runners are available on Team and Enterprise Cloud plans. Select under the "GPU-powered" tab when creating a runner group.

### Self-Hosted Runners

```yaml
jobs:
  train:
    runs-on: self-hosted  # your own machine with GPU
    # or with labels:
    runs-on: [self-hosted, linux, gpu]
```

## Running Python Scripts

```yaml
jobs:
  train:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'  # built-in pip caching

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run training script
        run: python src/train.py --epochs 10 --batch-size 32

      - name: Run evaluation
        run: python src/evaluate.py --model-path outputs/model.pt
```

## Caching pip Dependencies

### Using `actions/cache` directly

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Install dependencies
  run: pip install -r requirements.txt
```

### Using `setup-python` built-in cache (simpler)

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'         # automatically caches pip packages
    cache-dependency-path: requirements.txt
```

### Caching model weights / datasets

```yaml
- name: Cache model weights
  uses: actions/cache@v4
  with:
    path: ~/.cache/huggingface
    key: ${{ runner.os }}-hf-${{ hashFiles('model_config.json') }}
    restore-keys: |
      ${{ runner.os }}-hf-
```

## Matrix Builds

Run the same job across multiple configurations:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']
        model: ['small', 'large']
      fail-fast: false  # don't cancel all on first failure
      max-parallel: 4   # run at most 4 in parallel
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python test.py --model ${{ matrix.model }}
```

## Using Secrets in Workflows

### GITHUB_TOKEN

A temporary token automatically created for each workflow run. Scoped to the repository.

```yaml
steps:
  - name: Use GITHUB_TOKEN
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      gh pr comment ${{ github.event.pull_request.number }} --body "Tests passed!"
```

**GITHUB_TOKEN permissions** (configurable at job or workflow level):
```yaml
permissions:
  contents: read
  packages: write
  pull-requests: write
  issues: write
```

### Personal Access Token (PAT)

Use a PAT when you need to:
- Trigger other workflows
- Push to other repositories
- Access resources outside the current repository

```yaml
steps:
  - uses: actions/checkout@v4
    with:
      token: ${{ secrets.MY_PAT }}  # stored as a repo secret

  - name: Call external API
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    run: python src/generate.py
```

### Secrets vs GITHUB_TOKEN

| Feature | GITHUB_TOKEN | PAT |
|---------|-------------|-----|
| Created automatically | Yes | No |
| Expires | After workflow run | Configurable |
| Cross-repo access | No | Yes |
| Can trigger other workflows | No | Yes |
| Recommended for | Most Actions tasks | Cross-repo or elevated access |

## Full ML Pipeline Example

```yaml
name: ML Training and Evaluation

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      epochs:
        description: 'Training epochs'
        default: '20'

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest tests/unit/

  train:
    needs: lint-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
      
      - name: Cache dataset
        uses: actions/cache@v4
        with:
          path: data/
          key: dataset-v1
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Train model
        env:
          WANDB_API_KEY: ${{ secrets.WANDB_API_KEY }}
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: python train.py --epochs ${{ github.event.inputs.epochs || '20' }}
      
      - name: Upload model artifact
        uses: actions/upload-artifact@v4
        with:
          name: trained-model
          path: outputs/model/
          retention-days: 7

  evaluate:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
      - run: pip install -r requirements.txt
      - name: Download model
        uses: actions/download-artifact@v4
        with:
          name: trained-model
          path: outputs/model/
      - name: Evaluate
        run: python evaluate.py
      - name: Comment results on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = fs.readFileSync('eval_results.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Eval Results\n\`\`\`\n${results}\n\`\`\``
            });
```

## Environment Variables

```yaml
env:
  PYTHONPATH: src/  # workflow-level env var
  LOG_LEVEL: INFO

jobs:
  train:
    env:
      BATCH_SIZE: 32  # job-level
    steps:
      - run: python train.py
        env:
          EPOCHS: 10  # step-level (most specific)
```

## Artifacts

Share data between jobs or retain outputs:

```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: results
    path: results/
    retention-days: 30

# Download
- uses: actions/download-artifact@v4
  with:
    name: results
    path: results/
```

## Sources
- [Workflow syntax for GitHub Actions - GitHub Docs](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub-hosted runners reference - GitHub Docs](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Larger runners - GitHub Docs](https://docs.github.com/actions/using-github-hosted-runners/about-larger-runners/about-larger-runners)
- [Use GITHUB_TOKEN for authentication in workflows - GitHub Docs](https://docs.github.com/actions/security-guides/automatic-token-authentication)
- [Managing your personal access tokens - GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
