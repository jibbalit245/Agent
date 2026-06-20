# Replit Workspace Configuration

> Source: https://docs.replit.com/replit-workspace/configuring-repl
> Updated URL: https://docs.replit.com/replit-app/configuration
> Last updated: 2026-06

## Overview

Replit Apps are configured with two primary files at the project root:

1. **`.replit`** — Controls runtime behavior (run command, ports, env vars, deployment settings)
2. **`replit.nix`** — Defines system-level packages and environment (Nix configuration)

Both files are automatically created when you create a Repl, and can be edited directly.

## The `.replit` File

The `.replit` file is a TOML configuration file that controls how your app runs.

### Basic Structure

```toml
# Main run command (executes when you click Run)
run = "python main.py"

# Entry point file for the editor to open
entrypoint = "main.py"

# Hidden files from editor (optional)
hidden = [".pythonlibs"]
```

### Environment Variables

```toml
# Non-sensitive environment variables for development
[env]
NODE_ENV = "development"
PORT = "8080"
DEBUG = "true"

# Alternative: set env vars for run command specifically
[run.env]
MY_VAR = "my_value"
```

### Port Configuration

```toml
# Map internal ports to external ports
[[ports]]
localPort = 8080
externalPort = 80
description = "Main web server"

[[ports]]
localPort = 3001
externalPort = 3001
description = "API server"
```

- **`localPort`**: Port your app listens on internally
- **`externalPort`**: Port exposed externally (80 for HTTP default)
- Port 80 maps to the default web URL

### Language and Module Configuration

```toml
# Set the module/language runtime
modules = ["python-3.11:v18-20231227-a8952b2"]

# Or for Node.js
modules = ["nodejs-20:v8-20231227-a8952b2"]
```

### Deployment Configuration

```toml
[deployment]
# Deployment run command (can differ from dev run)
run = ["gunicorn", "main:app"]

# Deployment type
deploymentTarget = "autoscale"
# Options: "autoscale", "static", "reserved_vm", "scheduled", "background_worker"

# For static deployments
publicDir = "dist"
build = ["npm", "run", "build"]
```

### Interpreter Configuration

```toml
[interpreter]
command = ["prybar-python311", "-q", "--ps1", "[33m[00m ", "-i"]

[interpreter.env]
LD_LIBRARY_PATH = "${REPL_HOME}/.pythonlibs/lib/python3.11/site-packages/numpy.libs:${REPL_HOME}/.pythonlibs/lib"
```

### Nix Channel

```toml
[nix]
channel = "stable-23_11"
```

### Git Configuration

```toml
[gitHubImport]
requiredFiles = [".replit", "replit.nix", "pyproject.toml"]
```

### Debugger Configuration

```toml
[debugger]
support = true

[debugger.interactive]
transport = "localhost:0"
startCommand = ["dap-python", "main.py"]

[debugger.interactive.integratedAdapter]
dapTcpAddress = "localhost:0"

[debugger.interactive.initializeMessage]
command = "initialize"
type = "request"

[debugger.interactive.initializeMessage.arguments]
adapterID = "debugpy"
clientID = "replit"
clientName = "replit.com"
columnsStartAt1 = true
linesStartAt1 = true
locale = "en-us"
pathFormat = "path"
supportsInvalidatedEvent = true
supportsProgressReporting = true
supportsRunInTerminalRequest = true
supportsVariableType = true
```

## The `replit.nix` File

The `replit.nix` file defines system-level packages using the Nix package manager.

### Basic Structure

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
  ];
}
```

### Common Package Examples

```nix
{ pkgs }: {
  deps = [
    # Python
    pkgs.python311
    pkgs.python311Packages.pip
    
    # Node.js
    pkgs.nodejs-20_x
    pkgs.nodePackages.npm
    pkgs.yarn
    
    # System tools
    pkgs.git
    pkgs.curl
    pkgs.wget
    pkgs.ffmpeg
    pkgs.imagemagick
    
    # Database clients
    pkgs.postgresql
    pkgs.sqlite
    pkgs.redis
    
    # Build tools
    pkgs.gcc
    pkgs.gnumake
    
    # Language servers (for IDE support)
    pkgs.nodePackages.typescript-language-server
    pkgs.pyright
  ];
}
```

### Finding Packages

Search for Nix packages at: https://search.nixos.org/packages

Package naming conventions:
- `pkgs.python311` — Python 3.11
- `pkgs.nodejs-20_x` — Node.js 20
- `pkgs.postgresql` — PostgreSQL
- `pkgs.python311Packages.PKGNAME` — Python package in nixpkgs

### Applying Changes

After editing `replit.nix`:
1. Open the Shell tab
2. Type `exit` and press Enter to restart the shell
3. Nix will detect changes and install new packages

Or use the **System Dependencies** UI panel for easier package management.

## Full Example Configuration

### Python Flask App

**`.replit`:**
```toml
run = "python main.py"
entrypoint = "main.py"

[env]
FLASK_ENV = "development"
PORT = "8080"

[[ports]]
localPort = 8080
externalPort = 80

[deployment]
run = ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
```

**`replit.nix`:**
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.postgresql
  ];
}
```

### Node.js Express App

**`.replit`:**
```toml
run = "node index.js"
entrypoint = "index.js"

[env]
NODE_ENV = "development"

[[ports]]
localPort = 3000
externalPort = 80

[deployment]
run = ["node", "index.js"]
```

**`replit.nix`:**
```nix
{ pkgs }: {
  deps = [
    pkgs.nodejs-20_x
    pkgs.nodePackages.npm
  ];
}
```

## System Dependencies UI

Instead of manually editing `replit.nix`, use the System Dependencies panel:
1. Click the **Tools** icon in the sidebar
2. Select **System Dependencies** (or search for it)
3. Search for packages
4. Click Install

Changes are reflected in `replit.nix` automatically.
