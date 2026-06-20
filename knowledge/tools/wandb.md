# Weights & Biases (wandb)  
> Source: https://docs.wandb.ai/quickstart  
> Fetched: 2026-06-20

## What Is Weights & Biases?

Weights & Biases (W&B, `wandb`) is the **AI developer platform** for experiment tracking, model management, and team collaboration. Key capabilities:
- **Experiment tracking**: Log metrics, hyperparameters, code, and artifacts per training run
- **Visualizations**: Real-time charts, comparison tables, custom plots
- **Artifact versioning**: Track datasets, models, and other files
- **Sweeps**: Automated hyperparameter optimization
- **Model Registry**: Centralized model versioning and deployment tracking
- **Reports**: Shareable ML reports with inline visualizations
- **Integrations**: Works with PyTorch, TensorFlow, Keras, HuggingFace, Lightning, etc.

## Free Tier

- Unlimited experiments for individuals
- 100 GB artifact storage
- Personal projects are private by default
- Team/enterprise plans available for collaboration features

## Installation

```bash
pip install wandb
```

## API Key Setup

### Method 1: Environment Variable (recommended for CI/CD and production)

```bash
export WANDB_API_KEY="your-api-key-here"
```

### Method 2: CLI Login (recommended for local dev)

```bash
wandb login
# Opens browser or prompts for key
# Saves to ~/.netrc
```

### Method 3: Login in Code

```python
import wandb
wandb.login(key="your-api-key-here")
```

### Getting Your API Key

1. Log in to [wandb.ai](https://wandb.ai)
2. Click your profile → User Settings
3. Click "Create new API key" under the API Keys section
4. Copy the key immediately (you can't see it again)

For CI/CD: Set `WANDB_API_KEY` as a secret environment variable.

## Basic Usage

### Initialize a Run

```python
import wandb

# Start a run
run = wandb.init(
    project="my-ml-project",    # project name (created if doesn't exist)
    name="experiment-1",         # run name (auto-generated if omitted)
    config={                     # hyperparameters to track
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32,
        "model": "resnet50",
        "optimizer": "adam",
    },
    tags=["baseline", "v1"],
    notes="First baseline experiment",
)
```

### Log Metrics During Training

```python
for epoch in range(config.epochs):
    # Training loop...
    train_loss = train_one_epoch(model, train_loader)
    val_loss, val_acc = evaluate(model, val_loader)

    # Log metrics
    wandb.log({
        "epoch": epoch,
        "train/loss": train_loss,
        "val/loss": val_loss,
        "val/accuracy": val_acc,
        "learning_rate": optimizer.param_groups[0]["lr"],
    })
```

### Finish the Run

```python
wandb.finish()

# Or use as context manager
with wandb.init(project="my-project", config=config) as run:
    for epoch in range(10):
        wandb.log({"loss": train()})
```

## Logging Different Data Types

```python
import wandb
import numpy as np

run = wandb.init(project="demo")

# Scalars
wandb.log({"accuracy": 0.95, "loss": 0.23})

# Images
wandb.log({"predictions": [wandb.Image(img, caption="label") for img, label in samples]})

# Audio
wandb.log({"audio": wandb.Audio(waveform, sample_rate=44100)})

# Video
wandb.log({"video": wandb.Video(frames, fps=4)})

# Tables (structured data)
table = wandb.Table(columns=["input", "output", "label"])
table.add_data("cat photo", "cat", "cat")
wandb.log({"predictions": table})

# Histograms
wandb.log({"gradients": wandb.Histogram(np.array(grads))})

# Matplotlib figures
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
wandb.log({"my_plot": wandb.Image(fig)})
plt.close()
```

## Tracking Artifacts (Datasets and Models)

```python
# Log a dataset
artifact = wandb.Artifact("my-dataset", type="dataset")
artifact.add_file("data/train.csv")
artifact.add_dir("data/images/")
run.log_artifact(artifact)

# Log a model
model_artifact = wandb.Artifact("my-model", type="model")
model_artifact.add_file("checkpoints/best.pt")
run.log_artifact(model_artifact)

# Download an artifact
artifact = run.use_artifact("my-dataset:latest")
artifact_dir = artifact.download()
```

## Integrations

### PyTorch

```python
import wandb
from wandb.integration.torch import WandbTracer

run = wandb.init(project="pytorch-demo")

# Watch model — logs gradients and parameters
wandb.watch(model, log="all", log_freq=100)

# Training loop
for epoch in range(epochs):
    loss = train(model, loader)
    wandb.log({"loss": loss})
```

### HuggingFace Transformers

```python
from transformers import TrainingArguments

# Set env var to enable W&B logging
import os
os.environ["WANDB_PROJECT"] = "my-hf-project"

training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",   # enables W&B logging
    ...
)
```

### PyTorch Lightning

```python
from lightning.pytorch.loggers import WandbLogger

logger = WandbLogger(project="my-lightning-project")
trainer = pl.Trainer(logger=logger)
```

### Keras

```python
from wandb.integration.keras import WandbMetricsLogger

model.fit(
    X_train, y_train,
    callbacks=[WandbMetricsLogger()]
)
```

## Hyperparameter Sweeps

```python
# Define sweep config
sweep_config = {
    "method": "bayes",   # "grid", "random", or "bayes"
    "metric": {"goal": "minimize", "name": "val_loss"},
    "parameters": {
        "learning_rate": {"min": 0.0001, "max": 0.1},
        "batch_size": {"values": [16, 32, 64]},
        "layers": {"values": [2, 4, 8]},
    }
}

# Create sweep
sweep_id = wandb.sweep(sweep_config, project="my-project")

# Run agents
def train():
    with wandb.init() as run:
        config = run.config
        # ... train with config ...

wandb.agent(sweep_id, function=train, count=20)
```

## Key Environment Variables

```bash
WANDB_API_KEY="your-key"          # Authentication
WANDB_PROJECT="project-name"       # Default project
WANDB_ENTITY="team-name"           # Default entity/team
WANDB_MODE="offline"               # Run offline, sync later
WANDB_MODE="disabled"              # Disable W&B entirely
WANDB_DIR="/path/to/logs"          # Custom log directory
WANDB_SILENT="true"                # Suppress output
WANDB_NOTEBOOK_NAME="notebook"     # Jupyter notebook name
```

## Offline Mode

```bash
export WANDB_MODE="offline"
python train.py

# Sync later
wandb sync ./wandb/offline-run-*
```

## Useful CLI Commands

```bash
# Login
wandb login

# Check current status
wandb status

# List runs in a project
wandb runs project-name

# Sync offline runs
wandb sync ./wandb/

# Disable W&B for a single script
WANDB_MODE=disabled python train.py
```

## References

- [W&B Quickstart](https://docs.wandb.ai/quickstart)
- [W&B Documentation](https://docs.wandb.ai)
- [GitHub](https://github.com/wandb/wandb)
- [W&B Integrations](https://docs.wandb.ai/guides/integrations)
- [Sweeps Guide](https://docs.wandb.ai/guides/sweeps)
