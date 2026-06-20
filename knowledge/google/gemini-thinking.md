# Google Gemini API: Thinking / Reasoning Mode

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Gemini 2.5+ models perform internal reasoning before providing final answers. This "thinking" mode improves accuracy on complex tasks by allocating token budget for the model's internal deliberation.

## Setup

```python
%pip install -U -q 'google-genai>=1.51.0'
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
```

## Available Thinking Models

| Model | Thinking Budget Range | Notes |
|-------|----------------------|-------|
| `gemini-2.5-flash` | 0 to 24,576 tokens | Budget 0 disables thinking |
| `gemini-2.5-flash-lite` | 0 to 24,576 tokens | Budget 0 disables thinking |
| `gemini-2.5-pro` | 128 to 32,768 tokens | Cannot disable thinking |
| `gemini-3-pro` | 128 to 32,768 tokens | Highest thinking capacity |

## Default Adaptive Thinking

Without specifying a budget, the model dynamically adjusts reasoning based on task complexity:

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is 2 + 2?'
)
# Simple query — model uses minimal thinking
print(response.text)
```

## Fixed Thinking Budget

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Solve this logic puzzle: ...',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=4096  # Fixed token budget
        )
    )
)
print(response.text)
```

## Disable Thinking (Flash/Lite Models Only)

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the capital of France?',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0  # Disable thinking for simple queries
        )
    )
)
print(response.text)
```

**Note**: Cannot set `thinking_budget=0` for Pro models.

## Include Thought Summaries

Expose internal reasoning pathways:

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Prove that the square root of 2 is irrational.',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,   # Include thought summaries
            thinking_budget=8192,   # Budget for reasoning
        )
    )
)

# Extract thoughts and answer
for part in response.candidates[0].content.parts:
    if hasattr(part, 'thought') and part.thought:
        print(f"THOUGHT: {part.text}")
    else:
        print(f"ANSWER: {part.text}")
```

## Token Tracking

Monitor reasoning investment:

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Complex math problem...',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=8192)
    )
)

meta = response.usage_metadata
print(f"Prompt tokens:    {meta.prompt_token_count}")
print(f"Thoughts tokens:  {meta.thoughts_token_count}")   # Internal reasoning
print(f"Output tokens:    {meta.candidates_token_count}")
print(f"Total tokens:     {meta.total_token_count}")
```

## Practical Applications

### Complex Problem-Solving

```python
response = client.models.generate_content(
    model='gemini-2.5-pro',
    contents="""
    A train leaves station A at 9:00 AM traveling at 60 mph.
    Another train leaves station B (300 miles away) at 10:00 AM traveling at 80 mph.
    At what time will they meet, and how far from station A?
    """,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=4096)
    )
)
print(response.text)
```

### Logic Puzzles

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='A farmer has 17 sheep. All but 9 die. How many are left?',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=24576  # Max budget for tricky problems
        )
    )
)
print(response.text)
```

### Multimodal Reasoning

```python
from PIL import Image

img = Image.open('geometry_problem.png')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        img,
        'Find the area of the shaded region and show your work step by step.'
    ],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=8192,
            include_thoughts=True,
        )
    )
)
```

### Code Debugging

```python
buggy_code = """
def fibonacci(n):
    if n == 0: return 0
    if n == 1: return 1
    return fibonacci(n-1) + fibonacci(n-3)  # Bug here
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"Debug this code:\n{buggy_code}",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=4096)
    )
)
print(response.text)
```

## Chat with Thinking

```python
chat = client.chats.create(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=4096
        )
    )
)

response = chat.send_message('Explain the halting problem')
print(response.text)

response = chat.send_message('Give me a practical example in Python')
print(response.text)
```

## Key Observations

- **Higher budgets ≠ better answers**: More budget enables more thorough exploration but doesn't guarantee improvement
- **Simple queries**: Use budget=0 (if supported) or low budget for cost efficiency
- **Complex reasoning**: Use higher budgets (4096-24576) for math, logic, code
- **Transparency**: With `include_thoughts=True`, you can inspect the model's reasoning process
- **Improved consistency**: Thinking models demonstrate better accuracy on challenging problems

## Thinking Budget Guidelines

| Task Complexity | Recommended Budget |
|----------------|-------------------|
| Simple Q&A, chat | 0 (disabled) or 1024 |
| General reasoning | 2048-4096 |
| Complex math/logic | 8192-16384 |
| Hard puzzles, proofs | 16384-24576 (Flash) |
| Deepest reasoning | 32768 (Pro only) |
