# HuggingFace Hub — Datasets, Models, and Python API
> Sources: https://huggingface.co/docs/huggingface_hub/quick-start, https://huggingface.co/docs/huggingface_hub/guides/download, https://huggingface.co/docs/huggingface_hub/en/guides/upload, https://github.com/huggingface/huggingface_hub, https://huggingface.co/docs/hub/en/models-gated, https://huggingface.co/docs/hub/en/datasets-gated, https://github.com/huggingface/hub-docs/blob/main/docs/hub/storage-limits.md, WebSearch results 2026-06-20
> Fetched: 2026-06-20

---

## Overview

The HuggingFace Hub hosts 700,000+ models, 150,000+ datasets, and 300,000+ Spaces. The `huggingface_hub` Python library provides the primary client for interacting with the Hub programmatically.

```bash
pip install huggingface_hub
```

---

## Authentication

```python
from huggingface_hub import login
login(token="hf_xxxxxxxxxxxxxxxx")
# Or set HF_TOKEN env var before running
```

---

## Downloading Files

### Single File: `hf_hub_download`

```python
from huggingface_hub import hf_hub_download

# Download a single file from a model
path = hf_hub_download(
    repo_id="lysandre/arxiv-nlp",
    filename="config.json",
)
print(path)  # Local cache path

# From a dataset
path = hf_hub_download(
    repo_id="stanfordnlp/imdb",
    filename="data/train-00000-of-00001.parquet",
    repo_type="dataset",
)

# Gated model (requires token)
path = hf_hub_download(
    repo_id="meta-llama/Llama-3.1-8B",
    filename="config.json",
    token="hf_xxxxxxxxxxxxxxxx",
)

# Specific revision/branch/tag
path = hf_hub_download(
    repo_id="gpt2",
    filename="pytorch_model.bin",
    revision="main",  # branch, tag, or commit hash
)

# Download to specific local directory
path = hf_hub_download(
    repo_id="gpt2",
    filename="config.json",
    local_dir="./my_models/gpt2",
)
```

**Cache behavior:** Files are cached at `~/.cache/huggingface/hub/` by default. Set `HF_HOME` or `HUGGINGFACE_HUB_CACHE` to change location.

### Entire Repository: `snapshot_download`

```python
from huggingface_hub import snapshot_download

# Download entire model
local_dir = snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B",
    token="hf_xxxxxxxxxxxxxxxx",
)

# To a specific local directory
local_dir = snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B",
    local_dir="./models/llama-3.1-8b",
)

# Only download specific file patterns
local_dir = snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B",
    allow_patterns=["*.json", "*.safetensors"],
    ignore_patterns=["*.bin"],  # Skip PyTorch bins if you want safetensors
)

# Dataset download
local_dir = snapshot_download(
    repo_id="stanfordnlp/imdb",
    repo_type="dataset",
    local_dir="./data/imdb",
)
```

### CLI Download

```bash
# Download single file
huggingface-cli download meta-llama/Llama-3.1-8B config.json

# Download whole repo
huggingface-cli download meta-llama/Llama-3.1-8B --local-dir ./llama

# Download dataset
huggingface-cli download --repo-type dataset stanfordnlp/imdb
```

---

## Uploading Files

### Single File: `upload_file`

```python
from huggingface_hub import HfApi

api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Upload a single file to a model repo
api.upload_file(
    path_or_fileobj="/local/path/to/model.bin",
    path_in_repo="model.bin",
    repo_id="username/my-model",
)

# Upload to a dataset
api.upload_file(
    path_or_fileobj="/local/path/to/data.csv",
    path_in_repo="data/train.csv",
    repo_id="username/my-dataset",
    repo_type="dataset",
)

# Upload from bytes/file object
import io
content = b"Hello World"
api.upload_file(
    path_or_fileobj=io.BytesIO(content),
    path_in_repo="README.md",
    repo_id="username/my-model",
)

# Upload with commit message
api.upload_file(
    path_or_fileobj="/path/to/weights.safetensors",
    path_in_repo="model.safetensors",
    repo_id="username/my-model",
    commit_message="Add safetensors weights",
)
```

### Entire Folder: `upload_folder`

```python
# Upload a local folder (great for model checkpoints)
api.upload_folder(
    folder_path="./local_model_dir",
    repo_id="username/my-model",
    repo_type="model",
)

# Upload with filters
api.upload_folder(
    folder_path="./local_model_dir",
    repo_id="username/my-model",
    allow_patterns=["*.safetensors", "*.json"],
    ignore_patterns=["*.ckpt", "*.bin"],
)

# Upload to a subdirectory in the repo
api.upload_folder(
    folder_path="./results",
    repo_id="username/my-model",
    path_in_repo="evaluation_results/",
)
```

### CLI Upload

```bash
# Upload single file
huggingface-cli upload username/my-model ./local/file.bin file.bin

# Upload folder
huggingface-cli upload username/my-model ./local/folder/ --repo-type model

# Upload dataset
huggingface-cli upload --repo-type dataset username/my-dataset ./data/
```

---

## Creating Repositories

```python
from huggingface_hub import create_repo, HfApi

# Create a model repo
repo_url = create_repo(
    repo_id="username/my-new-model",
    repo_type="model",    # "model" | "dataset" | "space"
    private=True,         # Private repo
    token="hf_xxxxxxxxxxxxxxxx",
)

# Create via HfApi
api = HfApi(token="hf_xxxxxxxxxxxxxxxx")
repo_url = api.create_repo(
    repo_id="username/my-dataset",
    repo_type="dataset",
    private=False,
    exist_ok=True,  # Don't error if already exists
)
print(repo_url)
```

---

## Listing and Searching

```python
from huggingface_hub import HfApi, list_models, list_datasets

api = HfApi()

# List models with filters
models = list(api.list_models(
    filter="text-generation",     # Task filter
    language="en",
    library="transformers",
    sort="downloads",             # "downloads", "likes", "created_at"
    direction=-1,                 # -1 = descending
    limit=20,
))
for model in models:
    print(f"{model.id}: {model.downloads} downloads")

# Search by author/org
models = list(api.list_models(author="meta-llama"))

# List datasets
datasets = list(api.list_datasets(
    filter="text-classification",
    language="en",
    limit=10,
))

# Model info
info = api.model_info("meta-llama/Llama-3.1-8B-Instruct")
print(info.id)
print(info.downloads)
print(info.tags)
print(info.card_data)  # Model card metadata

# List files in a repo
files = api.list_repo_files("meta-llama/Llama-3.1-8B-Instruct")
for f in files:
    print(f)
```

---

## Gated Models

Some models require accepting terms before downloading:

**Common gated models:**
- All Meta Llama models
- Google Gemma models
- Black Forest Labs FLUX.1-dev
- Some Mistral models

**Requirements:**
1. Visit model page and accept terms
2. Your HF_TOKEN must be for an account with accepted access
3. For automatic approval: instant
4. For manual review: hours to days

**Using gated models:**
```python
# Must be logged in or pass token
from huggingface_hub import snapshot_download

# This will fail with 401/403 if you haven't accepted terms
local_dir = snapshot_download(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    token="hf_xxxxxxxxxxxxxxxx",  # Token for approved account
)

# With transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    token="hf_xxxxxxxxxxxxxxxx",
)
```

**Gated dataset access:**
```python
from datasets import load_dataset

# Private/gated dataset
dataset = load_dataset(
    "meta-llama/Llama-guard-3-8B-evals",
    token="hf_xxxxxxxxxxxxxxxx",
)
```

---

## Storage Limits by Account Type

| Account | Public Storage | Private Storage |
|---------|---------------|-----------------|
| Free | Best-effort (first few GB encouraged) | 100 GB |
| PRO ($9/mo) | Up to 10 TB | 1 TB |
| Team ($20/user/mo) | 12 TB base + 1 TB/seat | 1 TB/seat |
| Enterprise | 200 TB base + 1 TB/seat | 1 TB/seat |

**Extra storage:** $18/TB/month (volume discounts at 500TB+)

**Per-repo limits:**
- Individual file size: <200 GB recommended (500 GB hard limit)
- Files per repo: <100k recommended
- Entries per folder: <10k maximum
- Commit size: <100 files recommended

**Large files** automatically stored in Git LFS. Files > 10 MB should use LFS.

---

## Deleting and Managing Files

```python
api = HfApi(token="hf_xxxxxxxxxxxxxxxx")

# Delete a file
api.delete_file(
    path_in_repo="old_model.bin",
    repo_id="username/my-model",
    commit_message="Remove old checkpoint",
)

# Delete an entire folder
api.delete_folder(
    path_in_repo="old_checkpoints/",
    repo_id="username/my-model",
)

# Delete entire repo
api.delete_repo(repo_id="username/old-model")

# Rename/move a file
api.rename_discussion_comment(...)  # Via discussion API
```

---

## Dataset Loading with `datasets` library

```python
from datasets import load_dataset

# Load from Hub
dataset = load_dataset("stanfordnlp/imdb")
train = dataset["train"]
print(train[0])

# Load specific split
train = load_dataset("stanfordnlp/imdb", split="train")

# Load specific configuration
dataset = load_dataset("glue", "mrpc")

# Stream large datasets (don't download all at once)
dataset = load_dataset("bigcode/the-stack", streaming=True, split="train")
for example in dataset.take(5):
    print(example)

# Push dataset to Hub
dataset.push_to_hub("username/my-dataset", private=True, token="hf_xxx")
```

---

## Model Loading with `transformers`

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model (downloads and caches automatically)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype="auto",  # Auto-select appropriate dtype
    device_map="auto",   # Auto-distribute across GPUs
    token="hf_xxxxxxxxxxxxxxxx",
)

tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    token="hf_xxxxxxxxxxxxxxxx",
)

# Save model locally and push to Hub
model.save_pretrained("./local_model")
model.push_to_hub("username/my-fine-tuned-model", token="hf_xxx")
tokenizer.push_to_hub("username/my-fine-tuned-model", token="hf_xxx")
```

---

## References

- [HuggingFace Hub Quickstart](https://huggingface.co/docs/huggingface_hub/quick-start)
- [Download Files Guide](https://huggingface.co/docs/huggingface_hub/guides/download)
- [Upload Files Guide](https://huggingface.co/docs/huggingface_hub/en/guides/upload)
- [HfApi Reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api)
- [Storage Limits](https://huggingface.co/docs/hub/main/storage-limits)
- [Gated Models](https://huggingface.co/docs/hub/en/models-gated)
- [Gated Datasets](https://huggingface.co/docs/hub/en/datasets-gated)
