# OpenAI Assistants API
> Source: https://platform.openai.com/docs/assistants/overview
> Fetched: 2026-06-20

## Overview

The Assistants API allows building AI assistants within your applications. It manages conversation history (threads), supports tool use (code interpreter, file search, function calling), and handles stateful interactions.

**Note**: The Responses API is now the recommended approach for new projects needing stateful interactions. The Assistants API remains stable and supported but the Responses API offers improved performance and simpler primitives.

## Core Objects

### Assistant
An AI model configured with tools and a set of files. Persists across conversations.

### Thread
A conversation session between an assistant and a user. Stores messages and handles context window management automatically (truncates old messages when needed).
- Maximum: 100,000 messages per Thread
- Threads handle context overflow automatically

### Message
Content added to a thread. Can be from `user` or `assistant` role.

### Run
An execution of an Assistant on a Thread. Represents a single call to the AI model.
- Runs go through several statuses: `queued` → `in_progress` → `completed` (or `failed`, `cancelled`, `expired`)
- If a run uses tools, it may enter `requires_action` status

### Run Step
Granular steps within a Run. Can be `message_creation` or `tool_calls`.

---

## Setup and Authentication

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env
```

---

## Creating an Assistant

```python
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Help students understand and solve math problems step-by-step.",
    model="gpt-4o",
    tools=[
        {"type": "code_interpreter"},  # runs code
        {"type": "file_search"}        # searches uploaded documents
    ]
)

print(assistant.id)  # asst_abc123
```

### Assistant Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Friendly name for the assistant |
| `instructions` | string | System-level instructions (equivalent to system prompt) |
| `model` | string | Model ID to use |
| `tools` | array | List of tools: `code_interpreter`, `file_search`, or function tools |
| `tool_resources` | object | Files/vector stores attached to tools |
| `response_format` | string/object | `"auto"`, `{"type": "json_object"}`, or JSON schema |
| `temperature` | float | Sampling temperature 0-2 |
| `top_p` | float | Nucleus sampling |
| `metadata` | object | Key-value pairs for your own use (max 16 pairs) |

---

## Threads

```python
# Create a thread
thread = client.beta.threads.create()
print(thread.id)  # thread_abc123

# Create thread with initial messages
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Can you help me understand calculus?"
        }
    ]
)
```

### Thread Parameters

```python
# Add a message to existing thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What's the derivative of x^2?"
)

# Add message with file attachment
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze this dataset",
    attachments=[
        {
            "file_id": "file-abc123",
            "tools": [{"type": "code_interpreter"}]
        }
    ]
)
```

---

## Runs

### Create and Poll a Run

```python
# Simple: create run and wait for completion
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages.data:
        print(f"{msg.role}: {msg.content[0].text.value}")
```

### Manual Run Creation and Polling

```python
import time

# Create run
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please be concise in your responses."  # override assistant instructions
)

# Poll until done
while run.status not in ["completed", "failed", "cancelled", "expired"]:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

print(f"Run status: {run.status}")
```

### Run Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `thread_id` | string | Thread to run on |
| `assistant_id` | string | Assistant to use |
| `model` | string | Override the assistant's model for this run |
| `instructions` | string | Override/append assistant instructions |
| `additional_instructions` | string | Append to (not replace) assistant instructions |
| `tools` | array | Override assistant's tools for this run |
| `temperature` | float | Override temperature |
| `max_prompt_tokens` | int | Limit tokens in the prompt |
| `max_completion_tokens` | int | Limit tokens in the completion |
| `response_format` | object | Output format |
| `stream` | bool | Enable streaming |
| `metadata` | object | Key-value pairs |

### Run Statuses

| Status | Description |
|--------|-------------|
| `queued` | Run is waiting to start |
| `in_progress` | Run is active |
| `requires_action` | Tool calls need results from you |
| `cancelling` | Cancellation requested |
| `cancelled` | Run was cancelled |
| `failed` | Run encountered an error |
| `completed` | Run finished successfully |
| `expired` | Run expired (10 minute timeout) |
| `incomplete` | Hit max token limits |

---

## Tool: Code Interpreter

Executes Python code in a sandboxed environment. Can create charts, process files, do math.

```python
assistant = client.beta.assistants.create(
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
        "code_interpreter": {
            "file_ids": ["file-abc123"]  # files available to the interpreter
        }
    }
)
```

### Handling Code Interpreter Outputs

```python
run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
)

for step in run_steps.data:
    if step.type == "tool_calls":
        for tool_call in step.step_details.tool_calls:
            if tool_call.type == "code_interpreter":
                print("Code:", tool_call.code_interpreter.input)
                for output in tool_call.code_interpreter.outputs:
                    if output.type == "logs":
                        print("Output:", output.logs)
                    elif output.type == "image":
                        print("Image file ID:", output.image.file_id)
```

---

## Tool: File Search

Searches uploaded documents using vector similarity and keyword search. Automatically parses, chunks, embeds, and indexes files.

### Setting Up File Search

```python
# 1. Create a vector store
vector_store = client.beta.vector_stores.create(
    name="Research Papers"
)

# 2. Upload files to vector store
with open("paper.pdf", "rb") as f:
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[f]
    )

# 3. Attach vector store to assistant
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id]
        }
    }
)
```

### Vector Store Limits

| Property | Limit |
|----------|-------|
| Max file size | 512 MB |
| Max tokens per file | 5,000,000 |
| Total project storage | 2.5 TB default |
| Max files per vector store | 100,000,000 (stores created Nov 2025+) |
| Storage pricing | $0.10/GB/day (first 1GB free) |

### Supported File Types for File Search

- PDF, MD, DOCX, TXT, HTML, JSON, PPTX, CSV, and more
- Code files: `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.h`, etc.

---

## Tool: Function Calling (Custom Tools)

Same as Chat Completions function calling, but integrated into the assistant's run loop.

```python
assistant = client.beta.assistants.create(
    model="gpt-4o",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Get current stock price",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            }
        }
    ]
)

# Handle requires_action status
while run.status == "requires_action":
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []
    
    for tc in tool_calls:
        import json
        args = json.loads(tc.function.arguments)
        result = get_stock_price(args["symbol"])  # your function
        tool_outputs.append({
            "tool_call_id": tc.id,
            "output": str(result)
        })
    
    # Submit results
    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )
```

---

## Streaming Runs

```python
from openai import AssistantEventHandler

class EventHandler(AssistantEventHandler):
    def on_text_created(self, text):
        print("\nassistant: ", end="", flush=True)
    
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
    
    def on_tool_call_created(self, tool_call):
        print(f"\n{tool_call.type}: ", end="", flush=True)

with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    event_handler=EventHandler()
) as stream:
    stream.until_done()
```

---

## File Management

```python
# Upload a file
with open("data.csv", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="assistants"
    )
print(file.id)  # file-abc123

# List files
files = client.files.list(purpose="assistants")

# Delete a file
client.files.delete("file-abc123")

# Retrieve file content
content = client.files.content("file-abc123")
```

### File Purposes

| Purpose | Use Case |
|---------|---------|
| `assistants` | Files for Assistants API (code interpreter, file search) |
| `fine-tune` | Training data for fine-tuning |
| `vision` | Not needed — pass image URLs directly |
| `batch` | Input files for Batch API |

---

## Complete Example: Document Q&A Assistant

```python
from openai import OpenAI
import time

client = OpenAI()

# Create assistant with file search
assistant = client.beta.assistants.create(
    name="Document Analyst",
    instructions="You answer questions about uploaded documents accurately and concisely.",
    model="gpt-4o",
    tools=[{"type": "file_search"}]
)

# Create vector store and upload file
vector_store = client.beta.vector_stores.create(name="Documents")
with open("report.pdf", "rb") as f:
    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[f]
    )

# Attach to assistant
client.beta.assistants.update(
    assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

# Create thread and run
thread = client.beta.threads.create(
    messages=[{"role": "user", "content": "What are the key findings?"}]
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages.data[0].content[0].text.value)
```

---

## Cleanup

```python
# Delete a thread when done
client.beta.threads.delete(thread_id)

# Delete an assistant when done
client.beta.assistants.delete(assistant.id)

# Delete vector stores
client.beta.vector_stores.delete(vector_store.id)
```

---

## Pricing

| Resource | Cost |
|----------|------|
| Model usage | Same as Chat Completions (per token) |
| Code Interpreter | $0.03/session (per 1-hour session) |
| File Search (storage) | $0.10/GB/day (first 1GB free) |
| File upload | Free |

---

## Sources
- [Assistants API Overview | OpenAI API](https://platform.openai.com/docs/assistants/overview)
- [Assistants deep dive | OpenAI API](https://developers.openai.com/api/docs/assistants/deep-dive)
- [File Search tool | OpenAI API](https://developers.openai.com/api/docs/assistants/tools/file-search)
- [Assistants API v2 FAQ | OpenAI Help Center](https://help.openai.com/en/articles/8550641-assistants-api-v2-faq)
