# OpenAI Fine-Tuning API
> Source: https://platform.openai.com/docs/guides/fine-tuning
> Fetched: 2026-06-20

## Overview

Fine-tuning allows you to train a custom version of an OpenAI model on your own data. The resulting model:
- Follows your style, tone, and format more consistently
- Is shorter prompt-able (fewer examples needed in context)
- Has lower latency than prompting with many examples
- Performs better on tasks where prompt engineering isn't sufficient

## Supported Models for Fine-Tuning

- `gpt-4o-mini-2024-07-18` — recommended for most cases
- `gpt-4o-2024-08-06`
- `gpt-4.1` (check availability)
- `gpt-3.5-turbo-0125`
- `gpt-3.5-turbo-1106`
- `gpt-3.5-turbo-0613` (legacy)

Fine-tuned model ID format: `ft:gpt-4o-mini:org-name:model-suffix:id`

---

## When to Fine-Tune

Fine-tuning is most effective for:
- **Style and format consistency** (always respond in JSON, use a specific writing style)
- **Task-specific behavior** that prompt engineering alone can't achieve
- **Edge case handling** that you can demonstrate with examples
- **Tone and persona** customization
- **Reducing prompt length** by learning from examples in weights

Fine-tuning is NOT needed for:
- Adding new knowledge (use RAG instead)
- Recent events (training data has a cutoff)
- Tasks solvable with good prompting

---

## Training Data Format

### Chat Format (Recommended)

JSONL file where each line is a training example:

```jsonl
{"messages": [{"role": "system", "content": "You are a helpful customer support agent."}, {"role": "user", "content": "My order hasn't arrived."}, {"role": "assistant", "content": "I'm sorry to hear that. Let me look into your order right away. Could you please provide your order number?"}]}
{"messages": [{"role": "system", "content": "You are a helpful customer support agent."}, {"role": "user", "content": "I want a refund."}, {"role": "assistant", "content": "I understand you'd like a refund. I'll be happy to help process that for you. Can you tell me the reason for the return?"}]}
```

### With Tool Calls

```jsonl
{"messages": [{"role": "user", "content": "What's the weather in Boston?"}, {"role": "assistant", "tool_calls": [{"id": "call_abc", "type": "function", "function": {"name": "get_weather", "arguments": "{\"location\": \"Boston, MA\"}"}}]}, {"role": "tool", "tool_call_id": "call_abc", "content": "72°F, sunny"}, {"role": "assistant", "content": "The weather in Boston is 72°F and sunny."}], "tools": [{"type": "function", "function": {"name": "get_weather", "description": "Get weather", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}}]}
```

### Preference Data Format (DPO)

```jsonl
{"input": {"messages": [{"role": "user", "content": "Explain ML"}]}, "preferred_output": [{"role": "assistant", "content": "Machine learning is..."}], "non_preferred_output": [{"role": "assistant", "content": "ML is math."}]}
```

---

## Training Data Requirements

| Property | Value |
|----------|-------|
| File format | JSONL (one JSON object per line) |
| Minimum training examples | 10 examples |
| Recommended minimum | 50–100 examples |
| Best results | 500–1000+ examples |
| Max file size | 1GB |
| File purpose | `fine-tune` |

**Quality over quantity**: 100 high-quality examples outperform 1000 low-quality ones.

---

## Step-by-Step Fine-Tuning Process

### Step 1: Prepare and Upload Training Data

```python
from openai import OpenAI

client = OpenAI()

# Upload training file
with open("training_data.jsonl", "rb") as f:
    training_file = client.files.create(
        file=f,
        purpose="fine-tune"
    )

print(f"File ID: {training_file.id}")  # file-abc123

# Optional: upload validation file
with open("validation_data.jsonl", "rb") as f:
    validation_file = client.files.create(
        file=f,
        purpose="fine-tune"
    )
```

### Step 2: Create Fine-Tuning Job

```python
fine_tune_job = client.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-4o-mini-2024-07-18",
    
    # Optional parameters:
    validation_file=validation_file.id,
    
    hyperparameters={
        "n_epochs": 3,                   # "auto" or int
        "learning_rate_multiplier": 1.0, # "auto" or float
        "batch_size": "auto"             # "auto" or int
    },
    
    suffix="my-model",  # appended to fine-tuned model name
    
    seed=42  # for reproducibility
)

print(f"Job ID: {fine_tune_job.id}")  # ftjob-abc123
print(f"Status: {fine_tune_job.status}")
```

### Step 3: Monitor Progress

```python
import time

# Poll for status
while True:
    job = client.fine_tuning.jobs.retrieve(fine_tune_job.id)
    print(f"Status: {job.status}")
    
    if job.status in ["succeeded", "failed", "cancelled"]:
        break
    
    # List recent events
    events = client.fine_tuning.jobs.list_events(
        fine_tuning_job_id=fine_tune_job.id,
        limit=5
    )
    for event in reversed(events.data):
        print(f"  [{event.created_at}] {event.message}")
    
    time.sleep(30)

if job.status == "succeeded":
    print(f"Fine-tuned model: {job.fine_tuned_model}")
    # e.g., ft:gpt-4o-mini:myorg:my-model:abc123
```

### Step 4: Use the Fine-Tuned Model

```python
response = client.chat.completions.create(
    model=job.fine_tuned_model,  # ft:gpt-4o-mini:myorg:my-model:abc123
    messages=[
        {"role": "system", "content": "You are a helpful customer support agent."},
        {"role": "user", "content": "My package is late."}
    ]
)

print(response.choices[0].message.content)
```

---

## Hyperparameters

### n_epochs
- How many complete passes through training data
- Default (`"auto"`): 3–5 epochs depending on dataset size
- Fewer epochs = less overfitting, may underfit
- More epochs = better fit to training data, may overfit
- Typically: 3–10 for small datasets, 1–3 for large datasets

### learning_rate_multiplier
- Scales the learning rate relative to OpenAI's default
- Default (`"auto"`): Typically 0.05–0.2 depending on batch size
- Lower (0.1) → slower, more stable training
- Higher (2.0) → faster, potentially unstable
- Reduce if training loss oscillates; increase if training is too slow

### batch_size
- Number of examples per gradient update
- Default (`"auto"`): Scales with dataset size
- Larger batches → more stable gradient estimates, less frequent updates
- Smaller batches → more frequent updates, higher variance

---

## Fine-Tuning Job Parameters (Complete)

```python
client.fine_tuning.jobs.create(
    training_file="file-abc123",          # required
    model="gpt-4o-mini-2024-07-18",       # required
    validation_file="file-def456",         # optional
    hyperparameters={
        "n_epochs": "auto",               # "auto" or int
        "batch_size": "auto",             # "auto" or int
        "learning_rate_multiplier": "auto" # "auto" or float
    },
    suffix="my-model",                     # optional: suffix for model name
    seed=42,                               # optional: for reproducibility
    method={
        "type": "supervised"               # "supervised" (default) or "dpo"
    }
)
```

---

## Fine-Tuning Methods

### Supervised Fine-Tuning (SFT) — Default

Standard fine-tuning on labeled examples.

```python
method={"type": "supervised"}
```

### Direct Preference Optimization (DPO)

Train using preferred vs. non-preferred response pairs (for alignment/RLHF-like training).

```python
method={
    "type": "dpo",
    "dpo": {
        "beta": 0.1  # KL divergence penalty strength
    }
}
```

---

## Managing Fine-Tuning Jobs

```python
# List all fine-tuning jobs
jobs = client.fine_tuning.jobs.list(limit=10)

# Retrieve a specific job
job = client.fine_tuning.jobs.retrieve("ftjob-abc123")

# Cancel a running job
client.fine_tuning.jobs.cancel("ftjob-abc123")

# List events for a job
events = client.fine_tuning.jobs.list_events("ftjob-abc123")
```

---

## Fine-Tuned Model Management

```python
# List fine-tuned models
models = client.models.list()
fine_tuned = [m for m in models.data if m.id.startswith("ft:")]

# Delete a fine-tuned model
client.models.delete("ft:gpt-4o-mini:myorg:my-model:abc123")
```

---

## Pricing

| Stage | Cost |
|-------|------|
| Training | Per token processed (varies by model) |
| gpt-4o-mini fine-tuning | ~$0.30/1M training tokens |
| gpt-4o fine-tuning | ~$3.00/1M training tokens |
| Inference (fine-tuned models) | Higher than base models (typically 2–4x) |

Training tokens = number of tokens in training data × n_epochs

---

## Best Practices

1. **Start with prompting**: Try few-shot prompting first. Fine-tune only if needed.
2. **High-quality data**: 50 excellent examples beat 1000 mediocre ones.
3. **Representative distribution**: Include edge cases and diverse examples.
4. **Consistent format**: Use the same system prompt format as production.
5. **Validate with holdout set**: Reserve 10-20% of data for validation.
6. **Watch for overfitting**: Training loss should decrease; validation loss shouldn't increase.
7. **Iterate**: Start with a small dataset, evaluate, add more data for weak areas.
8. **Version your models**: Use meaningful suffixes and track which model corresponds to which training run.

---

## Interpreting Training Metrics

Events include metrics you can track:
- `train_loss` — should decrease over time
- `valid_loss` — should also decrease (if too high relative to train_loss, overfitting)
- `train_mean_token_accuracy` — model's accuracy on training set
- `valid_mean_token_accuracy` — model's accuracy on validation set

---

## Sources
- [Fine-tuning | OpenAI API](https://platform.openai.com/docs/guides/fine-tuning)
- [Fine-tuning best practices | OpenAI API](https://developers.openai.com/api/docs/guides/fine-tuning-best-practices)
- [Supervised fine-tuning | OpenAI API](https://developers.openai.com/api/docs/guides/supervised-fine-tuning)
- [Fine Tuning | OpenAI API Reference](https://developers.openai.com/api/reference/typescript/resources/fine_tuning)
