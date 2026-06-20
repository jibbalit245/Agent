# GitHub API & gh CLI
> Source: https://docs.github.com/en/rest/quickstart
> Fetched: 2026-06-20

## Overview

GitHub provides two primary interfaces for programmatic access:

1. **`gh` CLI** — Official command-line tool with convenient wrappers around the API
2. **GitHub REST API** — Full HTTP API at `https://api.github.com`

There is also a **GraphQL API** at `https://api.github.com/graphql` for more efficient queries.

## gh CLI

### Installation

```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh
# or
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# Windows (winget)
winget install --id GitHub.cli
```

### Authentication

```bash
# Interactive login (opens browser)
gh auth login

# Login with a specific token
echo $GITHUB_TOKEN | gh auth login --with-token

# Check current auth status
gh auth status

# Use a token for a single command
GH_TOKEN=my-token gh issue list
```

### Essential gh CLI Commands

#### Repository Operations

```bash
# Clone a repo
gh repo clone owner/repo

# Create a new repo
gh repo create my-new-repo --public --clone
gh repo create my-ml-project --private --description "ML training code"

# View repo info
gh repo view owner/repo
```

#### Issues

```bash
# List issues
gh issue list
gh issue list --label "bug" --state open

# View a specific issue
gh issue view 42

# Create an issue
gh issue create --title "Bug: model diverges" --body "Details here..."
gh issue create \
  --title "Feature request" \
  --body "$(cat issue_body.md)" \
  --label "enhancement" \
  --assignee "@me"

# Close an issue
gh issue close 42

# Comment on an issue
gh issue comment 42 --body "Fixed in PR #55"
```

#### Pull Requests

```bash
# List PRs
gh pr list
gh pr list --state merged --limit 20

# View a PR
gh pr view 55
gh pr view 55 --web  # open in browser

# Create a PR
gh pr create --title "Add training pipeline" --body "## Changes\n- Added training script"
gh pr create \
  --title "Fix learning rate scheduler" \
  --body "$(cat pr_body.md)" \
  --base main \
  --head feat/lr-fix \
  --reviewer "@teammate" \
  --label "model"

# Merge a PR
gh pr merge 55 --squash --delete-branch

# Check PR status
gh pr checks 55

# Review a PR
gh pr review 55 --approve
gh pr review 55 --request-changes --body "Please add tests"
```

#### Workflows / Actions

```bash
# List workflows
gh workflow list

# Run a workflow manually
gh workflow run train.yml --field epochs=20

# View workflow runs
gh run list
gh run view 12345

# Watch a run in progress
gh run watch 12345

# Download artifacts
gh run download 12345 --name trained-model
```

#### Secrets

```bash
# Set a secret
gh secret set OPENAI_API_KEY
gh secret set HF_TOKEN --body "hf_xxx..."

# List secrets
gh secret list

# Delete a secret
gh secret delete OLD_SECRET
```

#### Raw API Calls

The `gh api` subcommand lets you call any GitHub REST API endpoint:

```bash
# GET request
gh api /repos/owner/repo

# POST request
gh api --method POST /repos/owner/repo/issues \
  --field title="My Issue" \
  --field body="Issue body"

# Paginate through all results
gh api --paginate /repos/owner/repo/issues

# Using jq to extract fields
gh api /repos/owner/repo --jq '.stargazers_count'
gh api /user --jq '.login'

# List pull requests
gh api /repos/owner/repo/pulls --jq '.[].title'
```

## GitHub REST API

### Authentication

#### Personal Access Token (Fine-Grained — Recommended)

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     -H "X-GitHub-Api-Version: 2022-11-28" \
     https://api.github.com/user
```

Create at: GitHub > Settings > Developer settings > Personal access tokens > Fine-grained tokens

**Fine-grained PAT scopes**: Grant access per-repository or per-organization, with specific permission sets (read/write issues, PRs, contents, etc.)

#### In GitHub Actions

```yaml
steps:
  - name: Call GitHub API
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      gh api /repos/${{ github.repository }}/issues \
        --method POST \
        --field title="Automated issue" \
        --field body="Created by workflow"
```

### Rate Limits

| Authentication | Requests/hour |
|---------------|--------------|
| Unauthenticated | 60/hour (by IP) |
| Authenticated (user token) | 5,000/hour |
| GitHub App (org-owned) | 15,000/hour |
| Enterprise Cloud | Higher limits |

**Rate limit headers** (in every response):
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1372700873  (Unix timestamp)
X-RateLimit-Used: 13
X-RateLimit-Resource: core
```

**Check current rate limit status:**
```bash
gh api /rate_limit
# or
curl -H "Authorization: Bearer $TOKEN" https://api.github.com/rate_limit
```

**Handling rate limits:**
```python
import requests
import time

def github_api_call(url, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 403 and "rate limit" in response.text.lower():
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        sleep_time = reset_time - int(time.time()) + 5
        print(f"Rate limited. Sleeping {sleep_time}s")
        time.sleep(sleep_time)
        return github_api_call(url, token)  # retry
    
    return response.json()
```

### Common REST API Endpoints

#### Issues

```bash
# Create issue
POST /repos/{owner}/{repo}/issues
{
  "title": "Issue title",
  "body": "Issue body",
  "labels": ["bug"],
  "assignees": ["username"]
}

# List issues
GET /repos/{owner}/{repo}/issues?state=open&labels=bug&per_page=100

# Update issue
PATCH /repos/{owner}/{repo}/issues/{issue_number}

# Add comment
POST /repos/{owner}/{repo}/issues/{issue_number}/comments
{"body": "Comment text"}
```

#### Pull Requests

```bash
# Create PR
POST /repos/{owner}/{repo}/pulls
{
  "title": "PR title",
  "body": "PR description",
  "head": "feature-branch",
  "base": "main"
}

# Merge PR
PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge
{"merge_method": "squash"}

# List PR files
GET /repos/{owner}/{repo}/pulls/{pull_number}/files
```

#### Repositories

```bash
# Get repo info
GET /repos/{owner}/{repo}

# List repo contents
GET /repos/{owner}/{repo}/contents/{path}

# Create/update file
PUT /repos/{owner}/{repo}/contents/{path}
{
  "message": "commit message",
  "content": "base64-encoded-content",
  "sha": "existing-file-sha-if-updating"
}
```

### Pagination

```bash
# REST API returns max 100 items per page
GET /repos/{owner}/{repo}/issues?per_page=100&page=2

# Check for next page via Link header:
# Link: <https://api.github.com/repos/.../issues?page=3>; rel="next"
```

```python
# Python pagination helper
def get_all_pages(url, token):
    results = []
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    while url:
        response = requests.get(url, headers=headers)
        results.extend(response.json())
        # Get next page from Link header
        links = response.headers.get("Link", "")
        next_url = None
        for part in links.split(","):
            if 'rel="next"' in part:
                next_url = part.split(";")[0].strip().strip("<>")
        url = next_url
    return results
```

## Python SDK (PyGithub)

```bash
pip install PyGithub
```

```python
from github import Github

g = Github("YOUR_TOKEN")
repo = g.get_repo("owner/repo")

# Create issue
issue = repo.create_issue(
    title="Automated issue",
    body="Created via PyGithub",
    labels=["bug"]
)

# Create PR
pr = repo.create_pull(
    title="Add feature",
    body="PR description",
    head="feature-branch",
    base="main"
)
```

## Sources
- [Getting started with the REST API - GitHub Docs](https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api)
- [Rate limits for the REST API - GitHub Docs](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [Authenticating to the REST API - GitHub Docs](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api)
- [Managing your personal access tokens - GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [REST API endpoints for GitHub Actions Secrets - GitHub Docs](https://docs.github.com/en/rest/actions/secrets)
