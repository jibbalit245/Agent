# Replit Overview & Quickstart
> Source: https://docs.replit.com/getting-started/intro-replit
> Fetched: 2026-06-20

## What is Replit?

Replit is a browser-based collaborative development environment (IDE) and cloud platform that enables developers to write, run, and deploy code entirely in the browser — no local setup required. It serves more than 20 million users and supports virtually any programming language.

Key capabilities:
- **Browser-based IDE**: Full code editor with syntax highlighting, autocomplete, and debugging
- **Instant execution**: Run code immediately without local installation
- **Built-in deployment**: Deploy applications with one click
- **Collaboration**: Real-time multiplayer coding (like Google Docs for code)
- **AI-powered development**: Replit Agent builds, runs, and deploys apps from natural language prompts

Replit is particularly popular for:
- Rapid prototyping and demos
- Learning and teaching programming
- Building and deploying web applications and APIs
- AI-powered app development
- Full-stack applications in a single workspace

## Account Setup

1. Go to [https://replit.com](https://replit.com)
2. Sign up with Google, GitHub, or email
3. Free "Starter" account is created automatically
4. Optionally upgrade to **Core** ($20/month) or **Pro** for advanced features

## Workspace Concepts

### Repl
A **Repl** is a single project — it contains your code, a console/shell, file system, and a URL. Each Repl runs as a Linux container.

### Template
Start from pre-configured templates for common stacks: Python, Node.js, React, Next.js, Flask, Django, etc.

### Nix Environment
Replit uses Nix for package management. Each Repl has a `replit.nix` or `.nix` configuration file that specifies system-level dependencies.

## Creating a New Project

### Via UI
1. Click **"+ Create Repl"** (or the blue "+" button)
2. Choose a template or select "Blank Repl"
3. Name your project
4. Click **"Create Repl"**

### Via Replit Agent
1. Click **"+ Create Repl"**
2. Describe what you want to build in natural language (e.g., "Build a Flask API that returns weather data")
3. Replit Agent scaffolds the project, installs dependencies, and launches the app automatically

### Importing from GitHub
1. Click **"+ Create Repl"** → "Import from GitHub"
2. Paste a GitHub URL
3. Replit clones the repo and creates a Repl from it
4. Supports imports from Bolt, Lovable, and GitHub

## Replit AI Agent

Replit's AI Agent (2025 version: Agent v2) is a fully autonomous coding assistant that:

### What It Does
- Builds complete applications from a text prompt
- Writes, runs, and debugs code iteratively
- Installs required packages and configures the environment
- Deploys the finished app to a live URL
- Generates basic visuals and UI components (as of August 2025)

### Agent v2 Features (2025)
- More autonomous runtime — handles multi-step tasks without constant confirmation
- Real-time app design preview as the agent builds
- Supports importing and continuing projects from Bolt or Lovable (via GitHub)
- Integration with ChatGPT: tag `@replit` in ChatGPT to build Repls without leaving ChatGPT

### Using the Agent
1. Open a Repl or create a new one
2. In the chat panel (Replit AI), type a description of what you want
3. The agent plans, codes, tests, and runs the app
4. Review progress via checkpoints and the preview panel
5. Iterate by asking follow-up prompts

### Agent Credits
- Free (Starter) tier: daily AI credits; limited Agent checkpoints (~10/month)
- Core plan: more credits, higher checkpoint limits
- Pro/Enterprise: highest limits

## The Replit Workspace

```
┌─────────────────────────────────────────────────────┐
│  File Tree │  Code Editor      │  Preview / Output  │
│            │                   │                    │
│  📁 src/   │  app.py           │  [Live Preview]    │
│  📄 main.py│  ...code...       │                    │
│  📄 .env   │                   │  Console Output    │
│            │                   │                    │
├────────────┴───────────────────┴────────────────────┤
│  Shell / Console                                     │
│  $ python main.py                                    │
└─────────────────────────────────────────────────────┘
```

Key workspace panels:
- **Files**: File tree for the project
- **Editor**: Main code editor (Monaco-based)
- **Console**: Shell access and program output
- **Preview**: Live URL preview of web apps
- **Tools**: Secrets, Packages, Git, Deploy, etc.

## Supported Languages and Frameworks

Virtually any language that runs on Linux, including:
- Python (Flask, FastAPI, Django)
- JavaScript/TypeScript (Node.js, Express, Next.js, React)
- Java, C++, C#, Go, Ruby, Rust
- HTML/CSS (static sites)
- Bash, SQL

## Collaboration Features

- **Multiplayer**: Share a Repl link and collaborators can edit in real time
- **Comments**: Inline code comments
- **History**: Basic version history

## Package Management

- Python: pip/uv (packages installed to the Repl environment)
- Node.js: npm/yarn
- System packages: Nix (via `replit.nix`)

## References

- [Replit Docs](https://docs.replit.com)
- [Replit AI Agent](https://replit.com/ai)
- [Replit Blog: 2025 in Review](https://blog.replit.com/2025-replit-in-review)
- [Replit Agent Features](https://refine.dev/blog/replit-ai-agent/)
