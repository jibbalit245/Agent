# Google Gemini API: Structured Output

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

The Gemini API enables structured output through JSON mode, schema enforcement, and enum constraints. This forces the model to produce output in a specified format, making it easier to parse programmatically.

## Setup

```python
%pip install -U -q "google-genai>=1.0.0"
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
MODEL_ID = "gemini-2.5-flash"
```

## Method 1: JSON Mode with Schema in Prompt

```python
import json

prompt = """
List a few popular cookie recipes using this JSON schema:

Recipe = {'recipe_name': str}
Return: list[Recipe]
"""

raw_response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config={
        'response_mime_type': 'application/json'
    },
)

response = json.loads(raw_response.text)
print(json.dumps(response, indent=4))
```

Output:
```json
[
    {"recipe_name": "Chocolate Chip Cookies"},
    {"recipe_name": "Oatmeal Raisin Cookies"},
    {"recipe_name": "Peanut Butter Cookies"}
]
```

## Method 2: Direct Schema Supply (Recommended)

### Using TypedDict

```python
import typing_extensions as typing

class Recipe(typing.TypedDict):
    recipe_name: str
    recipe_description: str
    recipe_ingredients: list[str]

result = client.models.generate_content(
    model=MODEL_ID,
    contents="List a few imaginative cookie recipes.",
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Recipe],
    },
)

recipes = json.loads(result.text)
for recipe in recipes:
    print(f"Name: {recipe['recipe_name']}")
    print(f"Description: {recipe['recipe_description']}")
    print(f"Ingredients: {', '.join(recipe['recipe_ingredients'])}\n")
```

### Using Pydantic Models

```python
from pydantic import BaseModel

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

response = client.models.generate_content(
    model=MODEL_ID,
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_json_schema=CountryInfo.model_json_schema(),
    ),
)

country = json.loads(response.text)
print(country)
```

### Using Raw JSON Schema

```python
user_profile_schema = {
    'properties': {
        'age': {
            'anyOf': [
                {'maximum': 120, 'minimum': 0, 'type': 'integer'},
                {'type': 'null'},
            ],
            'title': 'Age',
        },
        'username': {
            'description': "User's unique name",
            'title': 'Username',
            'type': 'string',
        },
        'email': {
            'type': 'string',
            'format': 'email',
        }
    },
    'required': ['username', 'age', 'email'],
    'title': 'User Schema',
    'type': 'object',
}

response = client.models.generate_content(
    model=MODEL_ID,
    contents='Generate a random user profile.',
    config={
        'response_mime_type': 'application/json',
        'response_json_schema': user_profile_schema
    },
)
print(json.loads(response.text))
```

## Method 3: Enum Constraints

### Single-Value Enum (text/x.enum)

```python
import enum

class Sentiment(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

response = client.models.generate_content(
    model=MODEL_ID,
    contents='The weather today is sunny and warm!',
    config=types.GenerateContentConfig(
        response_mime_type="text/x.enum",
        response_schema=Sentiment
    )
)

print(response.text)  # Returns: positive (unquoted)
```

### Enum within JSON Schema

```python
class Priority(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class Task(typing.TypedDict):
    title: str
    description: str
    priority: Priority
    estimated_hours: float

result = client.models.generate_content(
    model=MODEL_ID,
    contents="Create 5 software development tasks for a new login feature",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[Task],
    )
)

tasks = json.loads(result.text)
for task in tasks:
    print(f"[{task['priority'].upper()}] {task['title']} ({task['estimated_hours']}h)")
```

## Complex Nested Schemas

```python
class Address(typing.TypedDict):
    street: str
    city: str
    country: str
    postal_code: str

class Person(typing.TypedDict):
    name: str
    age: int
    email: str
    address: Address
    skills: list[str]

result = client.models.generate_content(
    model=MODEL_ID,
    contents="Generate 3 fictional software engineer profiles",
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Person],
    }
)

people = json.loads(result.text)
for person in people:
    print(f"{person['name']}, {person['age']}: {', '.join(person['skills'][:3])}")
```

## Key Parameters

| Parameter | Values | Purpose |
|-----------|--------|---------|
| `response_mime_type` | `'application/json'`, `'text/x.enum'` | Output format |
| `response_schema` | TypedDict, enum class, or list thereof | Schema constraint |
| `response_json_schema` | Dict (JSON Schema) or Pydantic `.model_json_schema()` | Raw schema constraint |

## JSON Schema Type Values

When using raw JSON schema, use these type values:
- `'STRING'`
- `'INTEGER'`
- `'NUMBER'` (float)
- `'BOOLEAN'`
- `'ARRAY'`
- `'OBJECT'`
- `'NULL'`

## Important Notes

- **Don't duplicate schema in prompt**: "However you define your schema, don't duplicate it in your input prompt, including by giving examples of expected JSON output. If you do, the generated output might be lower in quality."
- Schema enforcement works across all supported Gemini models
- For enum-only responses, use `text/x.enum` (returns unquoted value)
- For JSON-formatted enums, use `application/json` (returns quoted value)

## Use Cases

| Use Case | Schema Approach |
|----------|----------------|
| API response parsing | Pydantic model |
| Classification | Enum with `text/x.enum` |
| Data extraction | TypedDict or JSON Schema |
| Entity recognition | Nested TypedDict |
| Multi-label classification | `list[EnumType]` |
| Database records | TypedDict matching DB schema |

## Available Models

- `gemini-2.5-flash` — Recommended
- `gemini-2.5-pro` — Most capable
- `gemini-2.5-flash-lite` — Lightweight
