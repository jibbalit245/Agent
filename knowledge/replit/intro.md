# Introduction to Replit

> Source: https://docs.replit.com/getting-started/intro-replit (403 Forbidden — content compiled from search results)
> Last updated: 2026-06

## What is Replit?

Replit is a cloud-based development platform that lets you code, collaborate, and deploy applications from your browser. It eliminates the need for local environment setup, making coding accessible and portable.

## Key Concepts

### Repls / Replit Apps

A **Repl** is your project workspace containing:
- All your code files
- Package configuration
- Environment settings
- Database access
- A runtime environment powered by Nix

When you open a Repl, you get a full development environment in the browser.

### The Workspace

The Replit workspace includes:

- **File Explorer** (left panel): Manage project files and folders
- **Code Editor**: Syntax highlighting, autocomplete, multi-cursor editing
- **Shell/Terminal**: Full terminal access with bash
- **Console**: Run output and error logs
- **Webview**: Live preview of your running app
- **AI Panel**: Access to Replit Agent and Assistant

### Configuration Files

Every Replit App has two key configuration files at the project root:

**`.replit`** — Controls app behavior:
```toml
run = "python main.py"
entrypoint = "main.py"

[env]
MY_VAR = "value"

[[ports]]
localPort = 8080
externalPort = 80
```

**`replit.nix`** — Defines system packages:
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs-19_x
    pkgs.postgresql
  ];
}
```

## Getting Started

### Creating a New Repl

1. Go to replit.com and sign in
2. Click "Create Repl" or "+"
3. Choose a template or programming language
4. Name your project
5. Click "Create Repl"

### Importing from GitHub

**Rapid import** (public repos):
- Open `https://replit.com/github.com/<owner>/<repo>`

**Guided import** (public and private repos):
1. Go to `replit.com/import`
2. Select GitHub
3. Connect your GitHub account
4. Choose a repository
5. Click Import

### Running Your App

Click the **Run** button (▶) to execute the command defined in `.replit`. The run command defaults to the appropriate runner for your language.

### Using Replit Agent

Replit Agent is an AI that can build your entire app from a description:
1. Open a Repl or create a new one
2. Describe what you want to build in natural language
3. Agent plans, writes code, installs dependencies, and runs your app
4. Iterate by chatting with Agent

## Collaboration

- **Multiplayer Mode**: Multiple users can edit the same Repl simultaneously in real-time
- **Sharing**: Share a Repl link for view or edit access
- **Teams**: Up to 5 collaborators on Core plan, up to 15 builders on Pro plan

## Package Management

Replit uses the **Universal Package Manager (UPM)** which supports:
- Python (Poetry, pip)
- Node.js (npm, yarn, pnpm)
- Ruby (Bundler)
- And more

Replit automatically detects missing imports when you click Run and installs them.

**Shell commands:**
```bash
# Python
upm add flask
poetry add requests

# Node.js
upm add express
npm install lodash
```

## Environment Variables and Secrets

- **Workspace Secrets**: Set via the Secrets pane (key-value pairs, injected as environment variables at runtime)
- **Deployment Secrets**: Separately configured in the Deployments pane
- **`.replit` env**: Non-sensitive env vars can go in `[env]` or `[run.env]` sections

## Networking and Ports

- Your app binds to a port (default 8080 or 3000 depending on template)
- Port 80 is the default HTTP port routed to your domain
- Multiple ports can run simultaneously; switch between them in the Webview
- For deployment, bind to `0.0.0.0` (not `localhost`)

## Deployment

After building your app, deploy with one click:
1. Click the **Deploy** button
2. Choose deployment type (Autoscale, Static, Reserved VM, etc.)
3. Configure settings and secrets
4. Click **Deploy**

Your app gets a `.replit.app` URL by default, or configure a custom domain.

## Resources

- Docs: https://docs.replit.com/
- Templates: https://replit.com/templates
- Community: https://ask.replit.com/
