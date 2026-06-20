# Anthropic CLI (`ant`)
> Source: https://platform.claude.com/docs/en/managed-agents/anthropic-cli.md
> Fetched: 2026-06-20
---

## Overview

The Anthropic CLI (`ant`) is a command-line tool for managing Managed Agents resources from the terminal or CI/CD pipelines. Use it to create agents, environments, sessions, and vaults without writing API code.

## Installation

```bash
pip install anthropic-cli
```

Or with Homebrew (macOS/Linux):
```bash
brew install anthropic/tap/ant
```

## Authentication

```bash
# Interactive login (browser OAuth)
ant auth login

# Or set API key
export ANTHROPIC_API_KEY=sk-ant-...
ant whoami  # verify authentication
```

## Agent Management

### Create an Agent

```bash
ant agents create \
  --name "Coding Assistant" \
  --model claude-opus-4-8 \
  --system "You are a helpful coding agent." \
  --output json
```

### From YAML Config (Recommended for Version Control)

```yaml
# agent.yaml
name: Coding Assistant
model: claude-opus-4-8
system: |
  You are a helpful coding agent. You have access to bash, file editing,
  and web search tools. Always verify your work with tests.
tools:
  - type: agent_toolset_20260401
mcp_servers: []
skills: []
description: "General-purpose coding assistant"
metadata:
  team: engineering
  environment: production
```

```bash
ant agents create --file agent.yaml
# Output: agent_abc123 (v1)
```

### List Agents

```bash
ant agents list
ant agents list --output json
```

### Get Agent Details

```bash
ant agents get agent_abc123
ant agents get agent_abc123 --version 2
```

### Update an Agent (Creates New Version)

```bash
ant agents update agent_abc123 \
  --system "Updated system prompt." \
  --output json
```

### Archive an Agent

```bash
ant agents archive agent_abc123
```

**Warning:** Archiving is permanent and irreversible. Do NOT archive as routine cleanup.

## Environment Management

### Create an Environment

```bash
ant environments create --name "Default"
```

### From YAML

```yaml
# environment.yaml
name: Production Environment
resources: []
```

```bash
ant environments create --file environment.yaml
# Output: env_xyz789
```

### List Environments

```bash
ant environments list
```

## Session Management

### Create a Session

```bash
ant sessions create \
  --agent agent_abc123 \
  --environment env_xyz789 \
  --title "My Task" \
  --message "Summarize the README file"
```

### Create and Stream Output

```bash
ant sessions create \
  --agent agent_abc123 \
  --environment env_xyz789 \
  --message "Write a Python web scraper" \
  --stream
```

### Send a Message to a Running Session

```bash
ant sessions send session_123 "What did you find?"
```

### List Sessions

```bash
ant sessions list
ant sessions list --agent agent_abc123
```

### Get Session Details and Events

```bash
ant sessions get session_123
ant sessions events session_123
```

## Vault Management (MCP Credentials)

### Create a Vault

```bash
ant vaults create --name "GitHub Vault"
```

### Add OAuth Credentials

```bash
ant vaults credentials create vault_abc123 \
  --type mcp_oauth \
  --mcp-server-name github
```

### Add API Key Credential

```bash
ant vaults credentials create vault_abc123 \
  --type api_key \
  --name "My API Key" \
  --value "sk-..."
```

### List Vaults

```bash
ant vaults list
```

## Deployment Management (Cron Schedules)

### Create a Scheduled Deployment

```bash
ant deployments create \
  --agent agent_abc123 \
  --environment env_xyz789 \
  --schedule "0 * * * *" \
  --title "Hourly Report" \
  --message "Generate the hourly status report."
```

### List Deployments

```bash
ant deployments list
```

### Disable a Deployment

```bash
ant deployments disable deployment_abc123
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/agent-deploy.yml
name: Deploy Agent

on:
  push:
    branches: [main]
    paths:
      - 'agent.yaml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Anthropic CLI
        run: pip install anthropic-cli
      
      - name: Update Agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          AGENT_ID: ${{ vars.AGENT_ID }}
        run: |
          ant agents update $AGENT_ID --file agent.yaml
```

### Store Agent ID in CI

On first creation:
```bash
AGENT_ID=$(ant agents create --file agent.yaml --output json | jq -r '.id')
echo "Store this: $AGENT_ID"
```

Then set `AGENT_ID` as a GitHub Actions variable (not secret — it's not sensitive).

## Output Formats

```bash
ant agents list --output table     # default
ant agents list --output json      # machine-readable
ant agents list --output yaml      # YAML format
```

## Common Patterns

### Agent Creation Script

```bash
#!/bin/bash
set -euo pipefail

# Create environment (once)
ENV_ID=$(ant environments create --name "Production" --output json | jq -r '.id')
echo "Environment: $ENV_ID"

# Create agent (once)
AGENT_ID=$(ant agents create --file agent.yaml --output json | jq -r '.id')
echo "Agent: $AGENT_ID"

# Store IDs
echo "AGENT_ID=$AGENT_ID" >> .env
echo "ENVIRONMENT_ID=$ENV_ID" >> .env
```

### Run a One-Off Task

```bash
#!/bin/bash
source .env

SESSION_ID=$(ant sessions create \
  --agent "$AGENT_ID" \
  --environment "$ENVIRONMENT_ID" \
  --message "$1" \
  --output json | jq -r '.id')

echo "Session: $SESSION_ID"
ant sessions events "$SESSION_ID" --stream
```
