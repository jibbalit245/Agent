# GitHub Actions Secrets Management
> Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
> Fetched: 2026-06-20

## Overview

GitHub Actions secrets store sensitive information (API keys, tokens, passwords) that workflows need. Secrets are **encrypted** and never appear in plain text in logs. They are not passed to workflows triggered by forked repositories (except `GITHUB_TOKEN`).

## Secret Scopes

There are three levels of secrets with different visibility:

### 1. Repository Secrets

Scoped to a single repository. Only workflows in that repo can access them.

**Create via UI**: Repository > Settings > Secrets and variables > Actions > New repository secret

**Create via gh CLI**:
```bash
gh secret set OPENAI_API_KEY
# You'll be prompted to enter the value securely

# Or provide value directly (avoid for sensitive data in shell history)
gh secret set OPENAI_API_KEY --body "sk-proj-..."

# From a file
gh secret set CERT_PEM < certificate.pem

# Pipe from another command
cat secret.txt | gh secret set MY_SECRET
```

### 2. Environment Secrets

Scoped to a specific deployment environment (e.g., `staging`, `production`). Only jobs that target that environment can access them.

```bash
# Create an environment secret
gh secret set PROD_DB_PASSWORD --env production

# List secrets in an environment
gh secret list --env production
```

Environment secrets are useful for:
- Separate production vs. staging credentials
- Required approvals before deployment (environment protection rules)
- Environment-specific API keys

### 3. Organization Secrets

Shared across multiple repositories in an organization. Reduces duplication.

```bash
# Create org secret (requires org admin)
gh secret set SHARED_API_KEY --org my-organization

# Restrict to specific repos
gh secret set SHARED_API_KEY --org my-organization \
  --visibility selected \
  --repos "repo1,repo2,repo3"

# Allow all repos
gh secret set SHARED_API_KEY --org my-organization --visibility all

# List org secrets
gh secret list --org my-organization
```

Organization secret visibility options:
- `all` — all repositories in the org
- `private` — only private repositories
- `selected` — specific named repositories

## Accessing Secrets in Workflows

### As Environment Variables

```yaml
steps:
  - name: Call OpenAI API
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      HF_TOKEN: ${{ secrets.HF_TOKEN }}
    run: python generate.py
```

### As Step Input

```yaml
steps:
  - name: Deploy to production
    uses: some/action@v1
    with:
      api_token: ${{ secrets.DEPLOY_TOKEN }}
```

### In Multi-Line Run Steps

```yaml
steps:
  - name: Configure and run
    env:
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    run: |
      echo "Starting with config..."
      python app.py --db-password "$DB_PASSWORD"
      # Never echo the secret directly: echo $DB_PASSWORD ← UNSAFE
```

## Using Environments in Workflows

```yaml
jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production  # triggers environment protection rules
    # environment secrets for 'production' are now available
    steps:
      - name: Deploy
        env:
          PROD_SECRET: ${{ secrets.PROD_SECRET }}  # environment secret
          SHARED_SECRET: ${{ secrets.SHARED_SECRET }}  # repo or org secret
        run: ./deploy.sh
```

## Precedence (when secrets share names)

1. **Environment secrets** (highest priority)
2. **Repository secrets**
3. **Organization secrets** (lowest priority)

## Secret Limits and Constraints

| Property | Limit |
|----------|-------|
| Max secret size | 48KB |
| Max secrets per repository | 100 |
| Max secrets per environment | 100 |
| Max secrets per organization | 1,000 |
| Secret name max length | 250 characters |

**Name constraints**:
- Alphanumeric characters and underscores only
- Must not start with `GITHUB_` prefix (reserved)
- Must not start with a number
- Case-insensitive (stored as uppercase)

## GITHUB_TOKEN vs Repository Secrets

```yaml
# GITHUB_TOKEN — auto-created, short-lived, repo-scoped
- name: Create PR comment
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: gh pr comment ${{ github.event.pull_request.number }} --body "Done!"

# PAT stored as secret — long-lived, broader scope
- name: Trigger another repo's workflow
  env:
    PAT: ${{ secrets.MY_PAT }}
  run: |
    gh api \
      --method POST \
      -H "Authorization: Bearer $PAT" \
      /repos/other-org/other-repo/dispatches \
      --field event_type=trigger-from-ci
```

## Security Best Practices

### 1. Never Echo Secrets Directly

```yaml
# UNSAFE — secret appears in logs
run: echo ${{ secrets.MY_SECRET }}

# SAFE — assign to env var first
env:
  MY_SECRET: ${{ secrets.MY_SECRET }}
run: use_secret.py  # access via os.environ["MY_SECRET"]
```

### 2. Secrets Are Masked in Logs

GitHub automatically redacts secret values from workflow logs. If a secret value appears in logs, it's replaced with `***`. However, never deliberately print secrets.

### 3. Secrets in Forked Repositories

By default, secrets are **not** passed to workflows triggered by forks. If you need to share limited secrets with forks, use environment secrets with explicit approval requirements.

```yaml
# This won't have access to secrets when triggered from a fork:
on:
  pull_request:
    types: [opened, synchronize]
```

Use `pull_request_target` (carefully — has security implications) or require maintainer approval via environments.

### 4. Limit Secret Scope

- Use fine-grained PATs with minimum required permissions
- Use environment secrets for deployment credentials
- Rotate secrets regularly
- Remove secrets that are no longer needed

### 5. Don't Put Secrets in Workflow Files

```yaml
# NEVER DO THIS — hardcoded credentials in source code
env:
  API_KEY: "sk-actual-key-here"  # WRONG

# ALWAYS USE secrets context
env:
  API_KEY: ${{ secrets.OPENAI_API_KEY }}  # CORRECT
```

## Reusable Workflows and Secrets

Secrets are **not** automatically passed to reusable workflows. You must explicitly pass them:

```yaml
# Calling workflow
jobs:
  call-reusable:
    uses: ./.github/workflows/reusable.yml
    secrets:
      openai_key: ${{ secrets.OPENAI_API_KEY }}
    # or pass all secrets:
    secrets: inherit
```

```yaml
# Reusable workflow (.github/workflows/reusable.yml)
on:
  workflow_call:
    secrets:
      openai_key:
        required: true

jobs:
  run:
    steps:
      - env:
          OPENAI_API_KEY: ${{ secrets.openai_key }}
        run: python main.py
```

## Updating and Deleting Secrets

```bash
# Update a secret (same command as create — overwrites)
gh secret set OPENAI_API_KEY --body "sk-new-key..."

# Delete a secret
gh secret delete OLD_API_KEY
gh secret delete OLD_API_KEY --env production
gh secret delete OLD_SECRET --org my-organization

# List all secrets (names only, not values)
gh secret list
gh secret list --env production
gh secret list --org my-organization
```

## Secrets for Codespaces

Separate from Actions secrets — set Codespace secrets via:

```bash
gh secret set OPENAI_API_KEY --app codespaces
```

Or: GitHub profile > Settings > Codespaces > Secrets

## Common Secret Names (Conventions)

```
OPENAI_API_KEY          # OpenAI API
ANTHROPIC_API_KEY       # Anthropic/Claude API
HF_TOKEN                # Hugging Face token
WANDB_API_KEY           # Weights & Biases
AWS_ACCESS_KEY_ID       # AWS credentials
AWS_SECRET_ACCESS_KEY   # AWS credentials
DOCKER_PASSWORD         # Docker Hub
GH_PAT                  # GitHub Personal Access Token
DEPLOY_KEY              # SSH deploy key
```

## Sources
- [Using secrets in GitHub Actions - GitHub Docs](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
- [Secrets - GitHub Docs](https://docs.github.com/en/actions/concepts/security/secrets)
- [Understanding GitHub secret types - GitHub Docs](https://docs.github.com/en/code-security/getting-started/understanding-github-secret-types)
- [Reuse workflows - GitHub Docs](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
- [GITHUB_TOKEN - GitHub Docs](https://docs.github.com/en/actions/concepts/security/github_token)
