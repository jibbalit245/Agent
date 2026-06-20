# Replit Overview

> Source: https://docs.replit.com/ (403 Forbidden — content compiled from search results and related sources)
> Last updated: 2026-06

## What is Replit?

Replit is an AI-powered cloud development platform that allows developers to build, run, and deploy applications entirely in the browser without any local setup. It provides an integrated development environment (IDE) with AI assistance, collaboration features, cloud storage, and one-click deployment.

## Core Concepts

### Repls / Replit Apps
A **Repl** (or Replit App) is your project workspace that includes your code, files, packages, and everything you need to build and run apps — all bundled together in the cloud. Each Repl comes with:
- A file system
- Terminal/Shell access
- Package manager
- Web preview
- Database access
- Object storage

### Key Features

- **Browser-based IDE**: No local installation required. Full development environment in the browser.
- **AI Agent**: Replit Agent can plan, implement, run, test, and deploy apps in a conversational loop inside Replit's workspace.
- **Multiplayer Collaboration**: Real-time collaboration with multiple users working on the same Repl simultaneously.
- **One-click Deployments**: Deploy apps with a single click to Autoscale, Reserved VM, Static, Scheduled, or Background Worker deployments.
- **Built-in Database**: Every Repl includes a Key-Value Store (Replit DB) and access to PostgreSQL.
- **Object Storage**: Store and manage unstructured data like media files and documents.
- **GitHub Integration**: Clone repositories directly, make changes, and push back to GitHub.
- **Nix-based Environments**: All Repls are powered by Nix for reproducible, declarative environments.

## Platform Architecture

Replit Apps are configured with two primary files:
- **`.replit`** — Controls how the app runs (run command, entrypoint, ports, env vars, deployment settings)
- **`replit.nix`** — Defines system-level packages and environment using Nix

## Deployment Options

| Type | Use Case | Pricing |
|------|----------|---------|
| Autoscale | Web apps with variable traffic | Pay-per-use (Compute Units) |
| Reserved VM | Always-on apps with steady traffic | Fixed monthly |
| Static | HTML/CSS/JS sites | Pay for data transfer |
| Scheduled | Cron/periodic tasks | Pay per run |
| Background Worker | Long-running processes | Compute Units |

## AI Features

- **Replit Agent**: End-to-end app builder that can plan, write, run, test, and deploy apps
- **Replit Assistant**: AI coding assistant for inline suggestions and completions
- **Fast Mode**: Quicker AI generations for rapid prototyping
- **Figma Import**: Convert Figma designs directly into working code at replit.com/import
- **ChatGPT Integration**: Build apps directly from ChatGPT conversations (launched Dec 2025)

## Plans Overview

| Plan | Price | Target |
|------|-------|--------|
| Starter | Free | Individuals/learning |
| Core | $25/month ($20/yr) | Individual developers |
| Pro | $100/month (up to 15 builders) | Teams |
| Enterprise | Custom pricing | Organizations |

## Recent Updates (2025-2026)

- **December 2025**: New free Starter Plan launched; ChatGPT integration; Fast Mode
- **February 2026**: Pro plan launched (replaces Teams); Core plan updated; pricing overhaul
- **2025**: Figma import; Agent v2 with near-instant interactions; PostgreSQL database preview
- **2025**: Object Storage introduced for unstructured data

## Resources

- Documentation: https://docs.replit.com/
- Pricing: https://replit.com/pricing
- Blog: https://blog.replit.com/
- Enterprise: https://replit.com/enterprise
