# Tool Use Concepts
> Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md
> Fetched: 2026-06-20
---

## User-Defined Tools

### Tool Definition Structure

Each tool requires a name, description, and JSON Schema for its inputs:

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and state, e.g., San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Temperature unit"
      }
    },
    "required": ["location"]
  }
}
```

**Best practices for tool definitions:**
- Use clear, descriptive names (e.g., `get_weather`, `search_database`, `send_email`)
- Write detailed descriptions — Claude uses these to decide when to use the tool. Be **prescriptive about *when* to call it**.
- Include descriptions for each property
- Use `enum` for parameters with a fixed set of values
- Mark truly required parameters in `required`; make others optional with defaults

### Tool Choice Options

| Value | Behavior |
| --- | --- |
| `{"type": "auto"}` | Claude decides whether to use tools (default) |
| `{"type": "any"}` | Claude must use at least one tool |
| `{"type": "tool", "name": "..."}` | Claude must use the specified tool |
| `{"type": "none"}` | Claude cannot use tools |

Any `tool_choice` value can include `"disable_parallel_tool_use": true` to force Claude to use at most one tool per response.

## Tool Runner vs Manual Loop

**Tool Runner (Recommended):** The SDK's tool runner handles the agentic loop automatically. Available in Python, TypeScript, Java, Go, Ruby, and PHP SDKs (beta).

**Manual Agentic Loop:** Use when you need fine-grained control (custom logging, conditional tool execution, human-in-the-loop approval). Loop until `stop_reason == "end_turn"`, always append the full `response.content`.

**Stop reasons for server-side tools:** When `stop_reason == "pause_turn"`, the server-side tool loop hit its default limit of 10 iterations. Re-send the user message and assistant response to continue.

```python
if response.stop_reason == "pause_turn":
    messages = [
        {"role": "user", "content": user_query},
        {"role": "assistant", "content": response.content},
    ]
    response = client.messages.create(
        model="claude-opus-4-8", messages=messages, tools=tools
    )
```

## Handling Tool Results

**Error handling in tool results:** Set `"is_error": true` and provide an informative error message.

**Multiple tool calls:** Handle them all before continuing — send all results back in a single `user` message.

## Server-Side Tools: Code Execution

```json
{
  "type": "code_execution_20260120",
  "name": "code_execution"
}
```

**Key Facts:**
- Runs in an isolated container (1 CPU, 5 GiB RAM, 5 GiB disk)
- No internet access (fully sandboxed)
- Python 3.11 with data science libraries pre-installed
- Containers persist for 30 days and can be reused
- Free when used with web search/web fetch; otherwise $0.05/hour after 1,550 free hours/month

**Pre-installed Python Libraries:** pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib, seaborn, openpyxl, xlsxwriter, pillow, pypdf, pdfplumber, python-docx, python-pptx, sympy, tqdm, sqlite3

## Server-Side Tools: Web Search and Web Fetch

```json
[
  { "type": "web_search_20260209", "name": "web_search" },
  { "type": "web_fetch_20260209", "name": "web_fetch" }
]
```

The `web_search_20260209` and `web_fetch_20260209` versions support **dynamic filtering** — Claude writes and executes code to filter search results before they reach the context window.

**Available on:** 1P, P-AWS, Vertex (web_search basic variant only).

## Structured Outputs

Two features are available:
- **JSON outputs** (`output_config.format`): Control Claude's response format
- **Strict tool use** (`strict: true`): Guarantee valid tool parameter schemas

**Supported models:** Claude Fable 5, Claude Opus 4.8, Claude Sonnet 4.6, Claude Haiku 4.5.

```python
response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=16000,
    messages=[...],
    output_format=ContactInfo,  # Pydantic model
)
contact = response.parsed_output  # validated instance
```

### JSON Schema Limitations

**Supported:** Basic types (object, array, string, integer, number, boolean, null), `enum`, `const`, `anyOf`, `allOf`, `$ref`/`$def`, String formats (date-time, time, date, duration, email, hostname, uri, ipv4, ipv6, uuid), `additionalProperties: false`

**Not supported:** Recursive schemas, Numerical constraints (`minimum`, `maximum`, `multipleOf`), String constraints (`minLength`, `maxLength`), Complex array constraints

## Client-Side Tools: Bash and Text Editor

### Bash tool declaration

```json
{"type": "bash_20250124", "name": "bash"}
```

Claude's `tool_use.input` contains either `{"command": "<string>"}` or `{"restart": true}`.

**Security:** Run in an isolated environment; apply an allowlist of permitted executables; set timeouts and resource limits; log every command.

### Text editor tool declaration

```json
{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}
```

`tool_use.input.command` is one of:

| `command` | Action |
|---|---|
| `view` | Return file contents or directory listing |
| `create` | Create/overwrite file with `file_text` |
| `str_replace` | Replace exactly one occurrence |
| `insert` | Insert text after line number |

**Security:** Confine every file operation to a fixed project root. Resolve model-supplied `path` to its canonical form and verify it remains within your project root.

## MCP Connector (Beta)

The MCP connector lets Claude call tools hosted on a remote MCP server directly from the Messages API. Requires beta flag `mcp-client-2025-11-20`.

```python
client.beta.messages.create(
    model="claude-opus-4-8", max_tokens=1024,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[{"type": "url", "url": "https://example/sse", "name": "example-mcp"}],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "example-mcp"}],
    messages=[...],
)
```

## Tool Runner (Python Example)

```python
from anthropic import beta_tool

@beta_tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get current weather for a location.

    Args:
        location: City and state, e.g., San Francisco, CA.
        unit: Temperature unit, either "celsius" or "fahrenheit".
    """
    return f"72°F and sunny in {location}"

runner = client.beta.messages.tool_runner(
    model="claude-opus-4-8",
    max_tokens=16000,
    tools=[get_weather],
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
)

for message in runner:
    print(message)
```

## Manual Agentic Loop (Python)

```python
messages = [{"role": "user", "content": user_input}]

while True:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "end_turn":
        break

    if response.stop_reason == "pause_turn":
        messages = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response.content},
        ]
        continue

    tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
    messages.append({"role": "assistant", "content": response.content})

    tool_results = []
    for tool in tool_use_blocks:
        result = execute_tool(tool.name, tool.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool.id,
            "content": result
        })

    messages.append({"role": "user", "content": tool_results})

final_text = next(b.text for b in response.content if b.type == "text")
```
