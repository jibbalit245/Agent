# Replit Package Management

> Source: https://docs.replit.com/replit-workspace/package-management
> Updated URL: https://docs.replit.com/references/project-setup/dependency-management
> Last updated: 2026-06

## Overview

Replit uses a **Universal Package Manager (UPM)** to manage language-specific packages across multiple languages. For system-level dependencies, Replit uses **Nix** via the `replit.nix` file.

Two levels of dependencies:
1. **Language packages**: npm, pip, gem, etc. (managed by UPM or language tools)
2. **System packages**: ffmpeg, postgresql, etc. (managed by Nix in `replit.nix`)

## Universal Package Manager (UPM)

UPM is Replit's open-source tool (`github.com/replit/upm`) that provides a unified interface for managing packages across languages.

### Supported Languages

| Language | Backend | Specfile | Lockfile |
|----------|---------|----------|----------|
| Python | Poetry (default) | `pyproject.toml` | `poetry.lock` |
| Python (alt) | pip/uv | `requirements.txt` | — |
| Node.js | npm | `package.json` | `package-lock.json` |
| Node.js (alt) | yarn | `package.json` | `yarn.lock` |
| Node.js (alt) | pnpm | `package.json` | `pnpm-lock.yaml` |
| Ruby | Bundler | `Gemfile` | `Gemfile.lock` |
| Emacs Lisp | Cask | `Cask` | — |
| Dart | pub | `pubspec.yaml` | — |
| Java | Maven/Gradle | `pom.xml` | — |
| Rust | Cargo | `Cargo.toml` | `Cargo.lock` |
| .NET | NuGet | `*.csproj` | — |
| PHP | Composer | `composer.json` | — |

### UPM Commands

```bash
# Add a package
upm add flask
upm add express lodash

# Remove a package
upm remove flask

# List installed packages
upm list
upm list -a  # Include all transitive dependencies

# Search for packages
upm search requests
upm info requests

# Install from lockfile
upm install

# Guess dependencies from code
upm add --guess    # Auto-detect and install missing packages
upm guess -a       # List guessed dependencies without installing

# Lock without installing
upm lock

# Check which language UPM detected
upm which-language

# Specify language manually
upm -l python add numpy
upm -l nodejs-npm add express
```

## Python Package Management

### Default: Poetry

When you create a Python Repl, **Poetry** is the default package manager:

```bash
# Add packages
poetry add flask
poetry add requests numpy pandas

# Add dev dependencies
poetry add --dev pytest black

# Remove packages
poetry remove flask

# Install from pyproject.toml
poetry install

# Update all packages
poetry update

# Show installed packages
poetry show
```

**Important**: `pip install` does NOT update Poetry's dependency tracking. Use `poetry add` or `upm add` instead.

### pyproject.toml Structure

```toml
[tool.poetry]
name = "my-app"
version = "0.1.0"
description = ""

[tool.poetry.dependencies]
python = ">=3.11.0,<3.12"
flask = "^2.3.0"
requests = "^2.31.0"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
```

### Alternative: pip

If you prefer pip, you can still use it:
```bash
pip install flask
pip install -r requirements.txt
```

But note: pip installations may not persist across Repl restarts unless you update `pyproject.toml` or `requirements.txt`.

### requirements.txt

For pip-based projects:
```txt
flask==2.3.3
requests==2.31.0
sqlalchemy==2.0.21
python-dotenv==1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

## Node.js Package Management

### npm (default)

```bash
# Install a package
npm install express
npm install --save-dev nodemon

# Remove a package
npm uninstall express

# Install all from package.json
npm install

# Update packages
npm update

# List installed
npm list
```

### yarn

```bash
yarn add express
yarn add --dev nodemon
yarn remove express
yarn install
```

### pnpm

```bash
pnpm add express
pnpm add -D nodemon
pnpm remove express
pnpm install
```

### package.json Structure

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "build": "tsc"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "@types/express": "^4.17.18"
  }
}
```

## Automatic Dependency Detection

Replit automatically analyzes your code for missing dependencies each time you click **Run**:

1. Scans import statements in your code
2. Checks if imports are installed
3. Installs missing packages automatically

Example: If you add `import pandas as pd` to Python code and click Run, Replit detects `pandas` is missing and installs it.

## System Dependencies (Nix)

For system-level packages (not language packages), edit `replit.nix`:

```nix
{ pkgs }: {
  deps = [
    # Add system packages here
    pkgs.ffmpeg
    pkgs.imagemagick
    pkgs.postgresql
    pkgs.redis
    pkgs.git
  ];
}
```

Finding packages: https://search.nixos.org/packages

After editing `replit.nix`, restart the shell (`exit` in shell tab) to apply changes.

### System Dependencies UI

Use the graphical System Dependencies panel:
1. Tools → System Dependencies
2. Search for packages
3. Click to install

## UPM Environment Variables

```bash
# Custom project root
UPM_PROJECT=/path/to/project

# Custom Python executable
UPM_PYTHON3=/usr/bin/python3.11

# Silence subprocess output
UPM_SILENCE_SUBROUTINES=1

# Custom cache location
UPM_STORE=/path/to/.upm
```

## Caching

UPM maintains a cache in `.upm/` directory:
- Skip lockfile generation if specfile unchanged
- Skip reinstalling if lockfile unchanged
- Skip code analysis if imports unchanged

Delete `.upm/` to force full reinstall.

## Troubleshooting

### Package Not Found
```bash
# Search for the correct package name
upm search mypackage

# Or search on PyPI (Python) / npm registry
```

### Import Errors After Install
```bash
# Verify package is installed
upm list | grep packagename

# Try reinstalling
upm remove packagename
upm add packagename
```

### Poetry vs pip Conflicts
If you see conflicts between Poetry and pip:
```bash
# Clear and reinstall
rm -rf .venv poetry.lock
poetry install
```
