# GitHub Codespaces
> Source: https://docs.github.com/en/codespaces/overview
> Fetched: 2026-06-20

## What Are GitHub Codespaces?

GitHub Codespaces are **cloud-hosted development environments** that run in containers. You get a full VS Code (or JupyterLab) environment in your browser or connected to your local VS Code, without any local setup.

Each codespace is a Docker container running on GitHub's cloud infrastructure, configured via `devcontainer.json`. You can start coding within seconds of opening a repository.

## Key Benefits for ML/AI Development

- Pre-installed ML libraries (NumPy, pandas, PyTorch, scikit-learn, etc.)
- JupyterLab available out of the box in the default image
- No local GPU required — use cloud machines
- Consistent environment across the team
- Port forwarding for ML experiment dashboards (TensorBoard, Weights & Biases, etc.)

## Machine Types

Codespaces offer a range of hardware configurations:

| Machine Type | CPUs | RAM | Storage | Notes |
|-------------|------|-----|---------|-------|
| 2-core | 2 | 8GB | 32GB | Free tier included; basic tasks |
| 4-core | 4 | 16GB | 32GB | Standard dev work |
| 8-core | 8 | 32GB | 64GB | Data processing, larger models |
| 16-core | 16 | 64GB | 128GB | Heavy ML workloads |
| 32-core | 32 | 128GB | 128GB | Large-scale training |

**Billing**: Compute cost is proportional to number of CPU cores. A 16-core machine costs **8x more** than a 2-core machine per hour.

### GPU Machine Types

GPU machines are available to **selected customers** (limited trial/preview). To request access, contact GitHub. GPU machines allow running deep learning training workloads directly in a Codespace.

Machine type identifiers (for `devcontainer.json`): `basicLinux32gb`, `standardLinux32gb`, etc.

## devcontainer.json

The `devcontainer.json` file (in `.devcontainer/` or root) configures your Codespace environment.

### Minimal Example

```json
{
  "name": "ML Development",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {}
  },
  "postCreateCommand": "pip install -r requirements.txt",
  "forwardPorts": [8888, 6006],  // Jupyter, TensorBoard
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "GitHub.copilot"
      ]
    }
  }
}
```

### Full ML Example

```json
{
  "name": "ML Training Environment",
  "build": {
    "dockerfile": "Dockerfile",  // custom Docker image
    "context": ".."
  },
  "hostRequirements": {
    "cpus": 8,
    "memory": "32gb",
    "storage": "64gb"
  },
  "postCreateCommand": "pip install -e '.[dev]' && pre-commit install",
  "postStartCommand": "echo 'Codespace ready!'",
  "forwardPorts": [8888, 6006, 8080],
  "portsAttributes": {
    "8888": {"label": "JupyterLab", "onAutoForward": "openBrowser"},
    "6006": {"label": "TensorBoard"}
  },
  "remoteEnv": {
    "PYTHONPATH": "${containerWorkspaceFolder}/src"
  },
  "mounts": [
    "source=ml-cache,target=/home/vscode/.cache,type=volume"
  ],
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python"
      },
      "extensions": [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "ms-python.black-formatter"
      ]
    }
  }
}
```

### `hostRequirements` for Machine Type Control

```json
{
  "hostRequirements": {
    "cpus": 4,       // minimum cores required
    "memory": "8gb", // minimum RAM
    "storage": "32gb"
  }
}
```

This ensures users can't accidentally create an underpowered Codespace for your project.

## Default Container Image

GitHub's default Codespace image includes these ML libraries pre-installed:
- NumPy, pandas, SciPy
- Matplotlib, seaborn, Plotly
- scikit-learn
- Keras, PyTorch
- Requests
- JupyterLab

This means most data science workflows work without any custom image.

## Prebuilds

Prebuilds speed up Codespace creation by pre-running setup commands. If your Codespace takes more than 2 minutes to create, prebuilds help significantly.

### How Prebuilds Work

1. GitHub runs your `postCreateCommand` (and other setup) in advance
2. The result is cached as a prebuild image
3. New Codespaces start from this snapshot — much faster

### Configuring Prebuilds

Via GitHub UI: Repository > Settings > Codespaces > Prebuilds > Set up prebuild

Prebuilds run using GitHub Actions minutes — they consume your Actions quota or incur additional charges.

```json
// devcontainer.json supports prebuild triggers
{
  "onCreateCommand": "pip install -r requirements.txt"  
  // postCreateCommand only runs for the user, not prebuilds
}
```

Prebuilds can be triggered on:
- Push to main branch
- Pull requests
- Scheduled (e.g., nightly)

## Lifecycle

```
Create → (prebuild restore) → postCreateCommand → postStartCommand
                    ↓
              Active / Running ← you work here
                    ↓
              Stopped (idle timeout) → persisted storage
                    ↓
              Deleted (retention period) → lost unless pushed
```

- **Idle timeout**: Default 30 minutes; configurable up to 4 hours
- **Retention**: Stopped Codespaces are retained for 30 days by default
- **Auto-deletion**: After retention period, Codespace is deleted (uncommitted changes lost)

## Billing

### Free Included Quota (per month per account)

| Plan | Core hours | Storage |
|------|-----------|---------|
| GitHub Free | 120 core-hours | 15GB |
| GitHub Pro | 180 core-hours | 20GB |
| GitHub Team | 300 core-hours/user | 20GB |
| Enterprise | Configurable | Configurable |

**Core-hours**: For a 2-core machine, 60 hours = 120 core-hours. For a 4-core machine, 60 hours = 240 core-hours.

### Billing Rate (beyond free quota)

| Cores | Price/hour |
|-------|-----------|
| 2-core | ~$0.18/hr |
| 4-core | ~$0.36/hr |
| 8-core | ~$0.72/hr |
| 16-core | ~$1.44/hr |
| 32-core | ~$2.88/hr |

Storage: ~$0.07/GB/month beyond free quota.

### Cost Optimization Tips

- Set **idle timeout** as low as practical
- Stop codespaces when not in use (they don't bill when stopped)
- Delete old codespaces you no longer need
- Use prebuilds to reduce active time spent on setup
- Use the minimum machine type your work requires

## Dotfiles

Personalize every Codespace with your dotfiles:

1. Create a public `dotfiles` repository on GitHub
2. Add setup scripts (`install.sh`, `bootstrap.sh`, etc.)
3. GitHub automatically applies them to new Codespaces

Settings > Codespaces > Dotfiles

## Secrets for Codespaces

```bash
# Via gh CLI
gh secret set OPENAI_API_KEY --app codespaces

# Or in GitHub UI:
# github.com/settings/codespaces → Secrets
```

Secrets are available as environment variables inside the Codespace.

## Port Forwarding

Access running services (Jupyter, TensorBoard, FastAPI servers):

```json
// devcontainer.json
{
  "forwardPorts": [8888, 6006, 8000],
  "portsAttributes": {
    "8888": {
      "label": "JupyterLab",
      "onAutoForward": "openBrowser"
    }
  }
}
```

In VS Code: Ports panel → Forward a Port

## JupyterLab in Codespaces

JupyterLab comes pre-installed in default images. To launch:

```bash
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
```

Then open the forwarded port 8888 in your browser. GitHub Codespaces handles authentication automatically.

## Sources
- [GitHub Codespaces billing - GitHub Docs](https://docs.github.com/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
- [About GitHub Codespaces prebuilds - GitHub Docs](https://docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds)
- [Getting started with GitHub Codespaces for machine learning - GitHub Docs](https://docs.github.com/en/codespaces/developing-in-a-codespace/getting-started-with-github-codespaces-for-machine-learning)
- [Setting a minimum specification for codespace machines - GitHub Docs](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/configuring-dev-containers/setting-a-minimum-specification-for-codespace-machines)
- [Changing the machine type for your codespace - GitHub Docs](https://docs.github.com/en/codespaces/customizing-your-codespace/changing-the-machine-type-for-your-codespace)
