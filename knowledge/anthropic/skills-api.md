# Skills API
> Source: https://platform.claude.com/docs/en/managed-agents/skills/overview.md
> Fetched: 2026-06-20
---

## Overview

Skills are task-specific instruction sets that Claude loads on demand. Instead of putting all instructions in the system prompt, Skills let you package specialized knowledge or behavior and attach it to an Agent — Claude loads the relevant Skill only when it's needed.

**Beta header required:** `skills-2025-10-02`

## Why Use Skills

- **Smaller context per turn:** Skills are loaded only when relevant, keeping the fixed context lean
- **Reusable across agents:** Write a Skill once, attach it to many agents
- **Version-controlled:** Skills are versioned independently of agents
- **Composable:** An agent can have up to 20 Skills

## Skill vs System Prompt

| | System Prompt | Skill |
|---|---|---|
| Always in context | Yes | No — loaded on demand |
| Versioned separately | No | Yes |
| Reusable | No | Yes |
| Max size | 100K chars | Larger (stored as files) |

## Creating a Skill

```python
import anthropic

client = anthropic.Anthropic()

skill = client.beta.skills.create(
    name="Python Code Review",
    description="Provides guidelines for reviewing Python code quality, style, and security.",
    content="""
# Python Code Review Guidelines

When reviewing Python code, check the following:

## Style
- Follow PEP 8 conventions
- Use type hints for function signatures
- Write docstrings for public functions

## Security
- Never hardcode credentials
- Validate all external inputs
- Use parameterized queries for SQL

## Performance
- Avoid N+1 database queries
- Use generators for large datasets
- Profile before optimizing

## Testing
- Write unit tests for all public functions
- Aim for >80% test coverage
- Test edge cases (None, empty, boundary values)
""",
    betas=["skills-2025-10-02"],
)

print(f"Skill ID: {skill.id}")
print(f"Version: {skill.version}")
```

## Skill Fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Human-readable name (1-256 chars) |
| `content` | Yes | Instruction content (markdown supported) |
| `description` | No | When/why Claude should use this skill |
| `metadata` | No | Arbitrary key-value pairs |

## Attaching Skills to an Agent

```python
agent = client.beta.agents.create(
    name="Code Review Agent",
    model="claude-opus-4-8",
    system="You are a helpful code review agent.",
    tools=[{"type": "agent_toolset_20260401"}],
    skills=[
        {"type": "skill", "id": skill.id},  # latest version
        # pin to a specific version:
        {"type": "skill", "id": another_skill.id, "version": 2},
    ],
    betas=["managed-agents-2026-04-01", "skills-2025-10-02"],
)
```

Maximum 20 skills per agent.

## Skill Endpoints

| Operation | Method | Path |
|---|---|---|
| Create | `POST` | `/v1/skills` |
| List | `GET` | `/v1/skills` |
| Get | `GET` | `/v1/skills/{id}` |
| Update (new version) | `POST` | `/v1/skills/{id}` |
| Archive | `POST` | `/v1/skills/{id}/archive` |

## Listing Skills

```python
skills = client.beta.skills.list(betas=["skills-2025-10-02"])
for skill in skills.data:
    print(f"{skill.id}: {skill.name} (v{skill.version})")
```

## Updating a Skill (Creates New Version)

```python
updated_skill = client.beta.skills.update(
    skill.id,
    content="Updated content...",
    betas=["skills-2025-10-02"],
)
print(f"New version: {updated_skill.version}")
```

Updates create a new immutable version. Existing agents pinned to older versions are unaffected.

## Skills for Tool Discovery

Skills integrate with **tool search** for dynamic capability loading:

```python
agent = client.beta.agents.create(
    name="Multi-Domain Agent",
    model="claude-opus-4-8",
    system="Use the appropriate skill for each task type.",
    tools=[
        {"type": "agent_toolset_20260401"},
        {"type": "tool_search_20261001"},  # enables tool search
    ],
    skills=[
        {"type": "skill", "id": python_skill.id},
        {"type": "skill", "id": sql_skill.id},
        {"type": "skill", "id": security_skill.id},
    ],
    betas=["managed-agents-2026-04-01", "skills-2025-10-02"],
)
```

Claude searches available skills and loads the most relevant one based on the current task.

## YAML Skill Definition (for `ant` CLI)

```yaml
# skills/python-review.yaml
name: Python Code Review
description: Guidelines for reviewing Python code quality, style, and security.
content: |
  # Python Code Review Guidelines
  
  When reviewing Python code, check the following:
  
  ## Style
  - Follow PEP 8 conventions
  ...
```

```bash
ant skills create --file skills/python-review.yaml
```

## TypeScript Example

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const skill = await client.beta.skills.create({
  name: "Data Analysis Guidelines",
  description: "Best practices for data analysis tasks",
  content: `
# Data Analysis Best Practices

1. Always validate data types before operations
2. Handle missing values explicitly  
3. Document your assumptions
4. Verify statistical significance before concluding
`,
}, { headers: { "anthropic-beta": "skills-2025-10-02" } });

console.log(`Skill created: ${skill.id} (v${skill.version})`);
```

## Best Practices

1. **Write descriptive names and descriptions** — Claude uses these to decide when to load the skill
2. **One skill per domain** — Don't bundle unrelated instructions into one skill
3. **Version skills in git** — Store skill YAML files alongside your codebase
4. **Pin versions in production** — Use `{"type": "skill", "id": "...", "version": N}` for stability
5. **Test skill loading** — Verify Claude loads the right skill for representative prompts
