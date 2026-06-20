# Together AI Fine-Tuning

> **Fetch status:** HTTP 403 Forbidden from https://docs.together.ai/docs/fine-tuning-overview — content below is from model training data (knowledge cutoff August 2025).

## Overview

Together AI supports full fine-tuning and LoRA (Low-Rank Adaptation) fine-tuning for customizing open-source models on your data. Fine-tuned models can be deployed for serverless or dedicated inference.

---

## Fine-Tuning Methods

| Method | Description | VRAM | Cost |
|---|---|---|---|
| **Full fine-tuning** | Update all model weights | High | Higher |
| **LoRA** | Train low-rank adapters only | Lower | Lower |
| **QLoRA** | Quantized LoRA | Lowest | Lowest |

Together AI primarily offers full fine-tuning for best results.

---

## Supported Base Models for Fine-Tuning

```
meta-llama/Llama-3.3-70B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
mistralai/Mistral-7B-Instruct-v0.3
Qwen/Qwen2.5-7B-Instruct-Turbo
Qwen/Qwen2.5-72B-Instruct-Turbo
```

---

## Fine-Tuning Workflow

### Step 1: Prepare Training Data

Training data must be in JSONL format (one JSON object per line).

**Chat format (recommended):**

```jsonl
{"messages": [{"role": "system", "content": "You are a helpful customer service agent."}, {"role": "user", "content": "How do I reset my password?"}, {"role": "assistant", "content": "To reset your password, go to Settings > Security > Reset Password and follow the instructions."}]}
{"messages": [{"role": "user", "content": "What are your business hours?"}, {"role": "assistant", "content": "We are open Monday through Friday, 9 AM to 6 PM Eastern Time."}]}
```

**Instruction format (legacy):**

```jsonl
{"prompt": "What is quantum computing?", "completion": "Quantum computing is a type of computation that uses quantum mechanical phenomena..."}
{"prompt": "Explain machine learning.", "completion": "Machine learning is a subset of artificial intelligence..."}
```

**Requirements:**
- Minimum: ~100 examples (more is better)
- Recommended: 500–5,000+ examples
- File format: `.jsonl`
- Max file size: 5 GB

---

### Step 2: Upload Training File

```python
from together import Together

client = Together(api_key="your_api_key")

# Upload file
with open("training_data.jsonl", "rb") as f:
    file_response = client.files.upload(
        file=("training_data.jsonl", f, "application/octet-stream"),
        purpose="fine-tune",
    )

file_id = file_response.id
print(f"File uploaded: {file_id}")
```

```bash
curl -X POST https://api.together.xyz/v1/files \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -F "file=@training_data.jsonl" \
  -F "purpose=fine-tune"
```

---

### Step 3: Create Fine-Tune Job

```python
fine_tune = client.fine_tuning.create(
    training_file=file_id,
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    n_epochs=3,
    n_checkpoints=1,
    batch_size=16,
    learning_rate=1e-5,
    warmup_ratio=0.1,
    suffix="my-custom-model",  # Added to model name
    wandb_api_key=None,        # Optional Weights & Biases
)

print(f"Fine-tune job created: {fine_tune.id}")
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `training_file` | string | required | File ID from upload |
| `model` | string | required | Base model to fine-tune |
| `n_epochs` | integer | 1 | Number of training epochs |
| `n_checkpoints` | integer | 1 | Number of checkpoints to save |
| `batch_size` | integer | 32 | Training batch size |
| `learning_rate` | float | 1e-5 | Learning rate |
| `warmup_ratio` | float | 0.0 | Warmup ratio |
| `suffix` | string | null | Suffix for model name |
| `validation_file` | string | null | Validation data file |
| `wandb_api_key` | string | null | W&B integration |
| `lora` | boolean | false | Use LoRA instead of full FT |
| `lora_r` | integer | 8 | LoRA rank |

---

### Step 4: Monitor Training

```python
# Check status
import time

while True:
    job = client.fine_tuning.retrieve(fine_tune.id)
    print(f"Status: {job.status}")
    
    if job.status in ["succeeded", "failed", "cancelled"]:
        break
    
    time.sleep(30)  # Poll every 30 seconds

if job.status == "succeeded":
    print(f"Model ready: {job.output_name}")
```

**Job Statuses:**

| Status | Description |
|---|---|
| `pending` | Queued, not yet started |
| `running` | Training in progress |
| `succeeded` | Training complete |
| `failed` | Training failed |
| `cancelled` | Job cancelled |

```python
# List all fine-tune jobs
jobs = client.fine_tuning.list()
for job in jobs.data:
    print(f"{job.id}: {job.status} - {job.model}")
```

```python
# Cancel a job
client.fine_tuning.cancel(fine_tune.id)
```

---

### Step 5: Use Fine-Tuned Model

```python
response = client.chat.completions.create(
    model=job.output_name,  # Your fine-tuned model ID
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

---

## File Management

```python
# List uploaded files
files = client.files.list()
for f in files.data:
    print(f"{f.id}: {f.filename} ({f.size} bytes)")

# Get file info
file_info = client.files.retrieve(file_id)

# Delete file
client.files.delete(file_id)
```

---

## Pricing

Fine-tuning pricing (approximate):

| Model Size | Training Cost |
|---|---|
| 7B–8B models | ~$0.20/M tokens |
| 13B models | ~$0.40/M tokens |
| 34B models | ~$0.80/M tokens |
| 70B models | ~$1.00/M tokens |

Inference of fine-tuned models is billed at the same rate as base models (or slightly higher for dedicated endpoints).

---

## Best Practices

### Data Quality
1. **Quality over quantity:** 500 high-quality examples beat 5,000 poor ones.
2. **Consistent format:** Use the same prompt/response format as the base model expects.
3. **Diverse examples:** Cover all use cases you want the model to handle.
4. **Balance classes:** If doing classification, balance positive/negative examples.

### Hyperparameters
1. **Start with defaults:** `n_epochs=1-3`, `lr=1e-5`
2. **Batch size:** Larger batches are more stable but need more memory
3. **Learning rate:** Too high causes forgetting; too low is slow
4. **Validation set:** Use 10-20% of data for validation

### Evaluation
```python
# Test fine-tuned model vs base model
test_prompts = [
    "How do I reset my password?",
    "What are your business hours?",
]

for prompt in test_prompts:
    base = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    fine_tuned = client.chat.completions.create(
        model=job.output_name,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"Prompt: {prompt}")
    print(f"Base: {base.choices[0].message.content}")
    print(f"Fine-tuned: {fine_tuned.choices[0].message.content}")
    print()
```

---

## LoRA Fine-Tuning

```python
fine_tune = client.fine_tuning.create(
    training_file=file_id,
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    lora=True,
    lora_r=16,          # Rank (higher = more capacity)
    lora_alpha=32,      # Alpha scaling
    lora_dropout=0.1,   # Dropout
    n_epochs=3,
    learning_rate=3e-4, # Higher LR for LoRA
)
```
