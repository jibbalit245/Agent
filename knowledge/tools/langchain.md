# LangChain + LangGraph  
> Source: https://docs.langchain.com, https://www.langchain.com/langgraph  
> Fetched: 2026-06-20

## What Are They?

**LangChain** is a framework for building applications powered by LLMs. It provides abstractions for:
- Calling LLMs and chat models (with a unified interface)
- Prompt templates and management
- Chains (sequences of LLM calls)
- Retrieval-augmented generation (RAG) with vector stores
- Tool/function calling
- Memory and conversation history

**LangGraph** is a separate library built on top of LangChain for building **stateful, multi-step agent workflows** as directed graphs (nodes + edges). It provides:
- Durable execution (persists state across crashes)
- Conditional branching and loops
- Parallel subgraph execution
- Human-in-the-loop interrupts
- Complete tracing and observability
- Multi-agent coordination

Both reached v1.0 milestones, signaling API stability.

## When to Use What

| Scenario | Use |
|----------|-----|
| Simple LLM call | Raw API (no framework needed) |
| Prompt templates, output parsing | LangChain basics |
| RAG pipeline (retrieve + generate) | LangChain |
| Linear chain of LLM calls | LangChain LCEL |
| Agent with tools, no complex branching | LangChain AgentExecutor |
| Agent with branching, loops, retries | LangGraph |
| Multi-agent system | LangGraph |
| Human-in-the-loop approval | LangGraph |
| Production with checkpointing | LangGraph |
| Simple prototype | Raw API (avoid over-engineering) |

**Key decision driver**: Control flow complexity. Simple linear flows → LangChain. Complex branching/state → LangGraph.

## Over-Engineering Warning

LangChain adds overhead and abstraction layers. For simple use cases (a single LLM call, a basic prompt template), use the provider SDK directly. LangChain is most valuable when you need:
- Provider-agnostic code (switch models easily)
- Complex retrieval pipelines
- Standardized tool calling across providers
- Production agent infrastructure (then use LangGraph)

## Installation

```bash
# Core
pip install langchain

# Provider integrations (install what you need)
pip install langchain-openai        # OpenAI / Azure
pip install langchain-anthropic     # Claude
pip install langchain-google-genai  # Gemini API
pip install langchain-google-vertexai  # Vertex AI
pip install langchain-community     # Many community integrations

# For LangGraph
pip install langgraph

# For RAG
pip install langchain-chroma        # Chroma vector store
pip install langchain-openai        # OpenAI embeddings
```

## Environment Variables

```bash
# LLM providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"  # For Vertex AI

# LangSmith (tracing, optional but recommended)
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="ls__..."
export LANGCHAIN_PROJECT="my-project"
```

## Basic LangChain Usage

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# All providers share the same interface
llm = ChatOpenAI(model="gpt-4o")
# or
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
# or
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Invoke
response = llm.invoke([
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is 2+2?")
])
print(response.content)
```

## Prompt Templates

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}."),
    ("human", "{question}")
])

chain = prompt | llm

response = chain.invoke({
    "domain": "Python",
    "question": "How do I use list comprehensions?"
})
```

## Basic LangGraph Agent

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing import TypedDict, Annotated
import operator

# Define tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

# Define state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# Build graph
llm = ChatOpenAI(model="gpt-4o").bind_tools([search_web])

def call_model(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode([search_web]))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

app = graph.compile()

result = app.invoke({"messages": [("human", "Search for today's news")]})
```

## LangGraph Key Features

### Checkpointing (Durable Execution)

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# State persists across invocations with same thread_id
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": [("human", "Hello")]}, config=config)
```

### Human-in-the-Loop

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]  # pause before tool execution
)

# Run until interrupt
result = app.invoke(input, config)
# ... show tool call to human, get approval ...
# Resume
result = app.invoke(None, config)
```

## Production Use Cases (2025-2026)

LangGraph powers production agents including:
- Uber's dev-QA bot
- LinkedIn's AI Hiring Agent
- Replit's coding assistant

## References

- [LangChain Docs](https://python.langchain.com/docs/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph vs LangChain Comparison](https://www.spheron.network/blog/langgraph-vs-langchain/)
- [LangChain v1.0 Blog Post](https://blog.langchain.com/langchain-langgraph-1dot0/)
