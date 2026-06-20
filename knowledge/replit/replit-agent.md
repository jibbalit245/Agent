# Replit Agent — Detailed Guide

> Source: https://docs.replit.com/replit-workspace/replit-agent
> References: search results from multiple sources
> Last updated: 2026-06

## What is Replit Agent?

Replit Agent is an **autonomous AI software engineer** that can build entire applications from natural language descriptions. Unlike code completion tools (like Copilot), Agent handles the complete software development lifecycle:

```
Your description → Planning → Code → Testing → Deployment
```

Agent operates directly on your actual project files, configuration, and runtime — not just generating code snippets, but building and running real apps.

## Core Capabilities

### 1. End-to-End App Building
- Plans the architecture
- Creates all necessary files
- Installs dependencies (npm, pip, etc.)
- Writes complete, working code
- Runs and tests the app
- Debugs errors automatically
- Can deploy the finished app

### 2. Multi-File Understanding
- Reads and understands your entire codebase
- Makes coordinated changes across multiple files
- Understands project structure and conventions

### 3. Tool Use
Agent can use various tools during development:
- **Shell**: Run commands, install packages
- **File system**: Create, read, edit, delete files
- **Web search**: Look up documentation and examples
- **Browser**: Test web interfaces
- **Database**: Set up and query databases

### 4. Autonomous Decision Making
- Decides which packages to use
- Chooses appropriate architecture patterns
- Handles errors without manual intervention
- Iterates until the solution works

## How Agent Works

### Workflow

```
1. User describes what to build
2. Agent enters Plan Mode (optional)
3. Agent creates implementation plan
4. Agent executes: code → run → test → debug
5. User reviews and provides feedback
6. Agent iterates until done
7. App is ready to deploy
```

### Behind the Scenes

When you give Agent a task, it:
1. **Analyzes** your existing codebase
2. **Searches** the web for relevant documentation if needed
3. **Plans** which files to create/modify
4. **Creates checkpoints** before making changes
5. **Implements** changes step by step
6. **Runs** the code to verify it works
7. **Debugs** any errors that occur
8. **Reports** back with results

## Using Agent

### Starting a Task

**Method 1: Chat Panel**
1. Open the AI/Agent panel (usually on the right side)
2. Type your request
3. Press Enter or click Send

**Method 2: From Scratch**
1. Create a new Repl
2. Describe your app to Agent
3. Agent builds everything from scratch

### Effective Prompts

**Be specific about requirements:**
```
"Build a REST API with Express.js that:
- Has endpoints for creating, reading, updating, deleting users
- Uses PostgreSQL for storage with a users table (id, name, email, created_at)
- Includes input validation
- Returns proper HTTP status codes"
```

**Mention technologies if you have preferences:**
```
"Create a React + TypeScript frontend with Tailwind CSS for a todo app"
```

**Describe the user experience:**
```
"Build a simple web app where users can:
1. Enter a URL to shorten
2. Get a short link back
3. Short links redirect to the original URL
Use SQLite to store the mappings"
```

**Iterate with follow-ups:**
```
"Add pagination to the list endpoint"
"Fix the bug where the form doesn't reset after submission"
"Add authentication using Replit Auth"
```

### Plan Mode

Before Agent starts coding, review the plan:

1. Enable Plan Mode toggle (or type "plan" prefix)
2. Agent outlines what it will do:
   ```
   Plan:
   1. Create Express.js server with basic structure
   2. Set up PostgreSQL connection using pg package
   3. Create users table migration
   4. Implement CRUD endpoints
   5. Add input validation with express-validator
   6. Test all endpoints
   ```
3. Review and approve (or request changes)
4. Agent executes the plan

### Checkpoints

Agent creates checkpoints during development:
- Automatically created before significant changes
- Can be created manually: "Create a checkpoint"
- **Rollback**: "Go back to the checkpoint before the database changes"
- Useful for safe experimentation

## Agent v2 Features (2025)

The major Agent v2 update brought:
- **Near-instant interactions**: Much faster response times
- **Better context understanding**: Reads more of your codebase
- **Improved debugging**: Better error resolution
- **Smarter planning**: More accurate implementation plans
- **Fast Mode**: Optional faster-but-simpler generation

## Integrations Built Into Agent

### Replit Auth
Add authentication with a single prompt:
```
"Add user authentication to this app"
```

Agent implements:
- Secure session management
- Login/logout flows
- User database table
- Protected routes
- Password handling (or OAuth via Replit Auth)

### PostgreSQL Database
```
"Add a PostgreSQL database for storing blog posts"
```

Agent:
- Creates the database connection
- Defines the schema
- Generates migration SQL
- Updates code to use the database
- Handles connection pooling

### Object Storage
```
"Add file upload support using Replit Object Storage"
```

Agent:
- Installs the Object Storage SDK
- Creates upload endpoint
- Handles multipart form data
- Stores files and returns URLs

### Figma Import

At replit.com/import → Figma:
1. Connect Figma account
2. Select your design
3. Agent converts design to working React components
4. Preserves visual design while adding interactivity

## Agent for Different Project Types

### Web Apps
```
"Build a weather dashboard that shows forecasts for multiple cities using the OpenWeatherMap API"
```

### REST APIs
```
"Create a Node.js REST API for a blog with authentication, posts, and comments"
```

### Bots
```
"Build a Discord bot that moderates messages and welcomes new members"
```

### Data Apps
```
"Create a Python script that fetches data from an API, processes it, and saves to a CSV file"
```

### Full-Stack Apps
```
"Build a full-stack task management app with React frontend and Python Flask backend with a PostgreSQL database"
```

## Limitations

### What Agent Does Well:
- ✅ CRUD applications
- ✅ REST APIs
- ✅ Simple to medium web apps
- ✅ Bot development
- ✅ Data processing scripts
- ✅ Integrating external APIs
- ✅ Adding features to existing apps

### What May Need Manual Help:
- ⚠️ Very complex enterprise architectures
- ⚠️ Highly specialized domains
- ⚠️ Performance-critical optimizations
- ⚠️ Complex security requirements
- ⚠️ Very large existing codebases

### Important Notes:
- Review Agent's code before deploying to production
- Generated code may not always follow best practices
- Long builds may time out on Starter plan
- Credit usage can be high for complex tasks

## Credit Usage

Agent tasks consume **usage credits** from your plan:

| Task Complexity | Approximate Credits |
|----------------|-------------------|
| Small fix/addition | Low |
| New feature | Medium |
| New API endpoint | Medium |
| Complete simple app | High |
| Complex full-stack app | Very High |

**Conserve credits:**
- Use Plan Mode to verify approach before building
- Be specific in prompts to reduce back-and-forth
- Use Assistant for small edits, Agent for major work
- Start with smaller tasks and expand

## Agent vs. Assistant

| Feature | Agent | Assistant |
|---------|-------|-----------|
| Scope | Full app building | Code assistance |
| Autonomy | High (multi-step) | Low (single responses) |
| Tool use | Yes (shell, files, etc.) | No |
| Context | Entire project | Selected code |
| Credit cost | Higher | Lower |
| Best for | Building new features | Getting help with code |
| Interaction | Conversational loop | Single Q&A |
