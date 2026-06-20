# Replit AI Features

> Source: https://docs.replit.com/ai/replit-ai (403 Forbidden — content compiled from search results)
> Last updated: 2026-06

## Overview

Replit offers comprehensive AI features integrated directly into the development workflow, from code generation to full app deployment.

## Replit Agent

### What is Replit Agent?

Replit Agent is an **end-to-end AI app builder** that turns natural language descriptions into working, deployed applications. Unlike simple code completion tools, Agent handles the entire development lifecycle:

- **Planning**: Breaks down requirements into tasks
- **Implementation**: Writes code across multiple files
- **Dependency management**: Installs required packages
- **Testing**: Runs and verifies the app
- **Deployment**: Can deploy the finished app

### Key Capabilities

**Autonomous Operation:**
- Multi-step task execution without human intervention for each step
- Reads and modifies existing files
- Installs npm/pip packages as needed
- Runs shell commands
- Debugs errors automatically

**Intelligence Features:**
- **Dynamic Intelligence**: Adapts approach based on context
- **Web Search**: Can search the internet for documentation/examples
- **Checkpoint/Rollback**: Creates checkpoints you can revert to
- **Plan Mode**: Brainstorm and outline without changing code

**Integrations:**
- **Figma Import**: Convert Figma designs to working code
- **Replit Auth**: Add authentication in a single prompt
- **Database integration**: Set up PostgreSQL automatically
- **GitHub Integration**: Import and work with GitHub repos

### Agent v2 (2025)

Agent v2 introduced significant improvements:
- Near-instant interactions for both Agent and Assistant
- Better multi-file understanding
- Improved debugging capabilities
- Fast Mode for quicker generation

### How to Use Agent

1. Open a Replit App (or create new)
2. Click on the **Agent** tab or use the AI chat panel
3. Describe what you want to build:
   ```
   "Build a todo app with a PostgreSQL database and user authentication"
   
   "Create a REST API for managing blog posts with Express and SQLite"
   
   "Make a Discord bot that responds to /hello with a greeting"
   ```
4. Agent plans the tasks and starts building
5. Review changes, provide feedback, iterate

### Plan Mode

Before Agent starts coding, it can outline the plan:
1. Enter your request
2. Click "Plan" (not "Build")
3. Review the plan Agent proposes
4. Approve or modify before implementation begins

### Checkpoints and Rollback

Agent creates checkpoints during development:
- Revert to previous state if something breaks
- Compare different approaches
- Safe experimentation

## Replit Assistant

### What is Replit Assistant?

Replit Assistant is an **AI coding assistant** (think GitHub Copilot) integrated into the editor:
- Inline code suggestions as you type
- Code completion
- Docstring generation
- Explain code
- Fix errors
- Answer questions about your code

### Using the Assistant

**Inline suggestions:**
- Just start typing — Assistant suggests completions
- Press Tab to accept
- Press Escape to dismiss

**Chat mode:**
- Open the AI chat panel
- Ask questions about your code
- Get explanations, fixes, and suggestions

**Example prompts:**
```
"Explain what this function does"
"Fix the bug in the selected code"
"Write a docstring for this function"
"How do I add error handling here?"
"Convert this to async/await"
```

## AI-Powered Features

### Automatic Error Fixing

When your app throws an error:
1. Error appears in Console
2. AI icon appears next to the error
3. Click to get AI explanation and suggested fix
4. Apply the fix automatically

### Import Resolution

When you import a package that's not installed:
1. Replit detects the missing import
2. Automatically searches for the package
3. Offers to install it
4. Can also use AI to suggest the correct package name

### Natural Language Scheduling

For Scheduled Deployments:
- Enter schedule in plain English: "Every Monday at 9 AM"
- AI converts to cron expression: `0 9 * * 1`

### Replit Auth (AI-Configured)

Add authentication to your app with a single Agent prompt:
```
"Add user authentication to this app"
```

Agent implements:
- Secure login/logout
- User sessions
- Database integration for user storage
- Password reset emails (if applicable)
- Built-in security best practices

### Figma Import

Convert Figma designs to code:
1. Go to replit.com/import
2. Select Figma
3. Connect your Figma account
4. Select a design/frame
5. Agent converts it to working code while preserving visual integrity

## ChatGPT Integration

Launched **December 2025**:
- Build Replit apps directly from ChatGPT conversations
- Describe your app in ChatGPT
- Click to open in Replit and continue building
- Seamless transition from planning to development

## AI Models

Replit uses multiple AI models, including:
- Access to **latest AI models** (on Core/Pro/Enterprise)
- Smarter Agent capabilities on paid plans
- Starter plan has access to basic models with limitations

## Fast Mode

Introduced December 2025:
- **Fast Mode** generates code more quickly
- Trade-off: May be slightly less thorough than standard mode
- Toggle in Agent settings
- Useful for quick prototypes and iterations

## Credit Usage

AI features consume **usage credits**:

| Feature | Credit Usage |
|---------|-------------|
| Assistant inline suggestions | Low |
| Assistant chat messages | Low-Medium |
| Agent simple tasks | Medium |
| Agent complex app builds | High |
| Agent with web search | Medium-High |

Core plan includes $25/month in credits covering AI and compute. Heavy Agent use for complex apps can exhaust monthly credits quickly.

**Tips to conserve credits:**
- Use Plan Mode to review before building
- Be specific in prompts (fewer iterations needed)
- Use Assistant for small tasks, Agent for big builds
- Break large projects into phases

## Limitations

- Agent works best with standard web technologies (Node.js, Python, React)
- Very complex enterprise architectures may need manual intervention
- AI suggestions may not always be optimal — review before accepting
- Long builds may time out on smaller plans
- Generated code should be reviewed for security before production use
