# Replit Nix Configuration

> Source: https://docs.replit.com/programming-ide/nix
> Blog references: https://blog.replit.com/powered-by-nix, https://blog.replit.com/nix
> Last updated: 2026-06

## What is Nix on Replit?

Every Replit App is powered by **Nix** — a purely functional package manager and system configuration tool. Nix enables:
- **Reproducible environments**: Same packages, same versions, every time
- **Declarative configuration**: Describe what you want, Nix figures out how
- **Thousands of packages**: Access to the entire nixpkgs repository (80,000+ packages)
- **Multiple language support**: Run Python, Node.js, Ruby, Go, Rust, and more in the same environment

Replit uses Nix to replace the old Docker-based approach, enabling support for essentially any programming language.

## The `replit.nix` File

The `replit.nix` file is the primary configuration for your system environment.

### Basic Syntax

```nix
{ pkgs }: {
  deps = [
    pkgs.PACKAGE_NAME
  ];
}
```

The file is a Nix expression that:
- Takes `pkgs` as input (the nixpkgs package set)
- Returns an attribute set with a `deps` list
- Lists all system packages to install

### Example Configurations

#### Python Project

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.glibcLocales
  ];
}
```

#### Node.js Project

```nix
{ pkgs }: {
  deps = [
    pkgs.nodejs-20_x
    pkgs.nodePackages.npm
    pkgs.nodePackages.yarn
  ];
}
```

#### Full-Stack App (Python + Node.js)

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.nodejs-20_x
    pkgs.nodePackages.npm
    pkgs.postgresql
    pkgs.redis
  ];
}
```

#### TypeScript Project

```nix
{ pkgs }: {
  deps = [
    pkgs.nodejs-20_x
    pkgs.nodePackages.npm
    pkgs.nodePackages.typescript
    pkgs.nodePackages.typescript-language-server
    pkgs.yarn
    pkgs.replitPackages.jest
  ];
}
```

#### Media Processing

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.ffmpeg
    pkgs.imagemagick
    pkgs.ghostscript
  ];
}
```

#### Go Project

```nix
{ pkgs }: {
  deps = [
    pkgs.go
    pkgs.gopls
    pkgs.go-tools
  ];
}
```

#### Rust Project

```nix
{ pkgs }: {
  deps = [
    pkgs.rustc
    pkgs.cargo
    pkgs.rustfmt
    pkgs.clippy
    pkgs.rust-analyzer
  ];
}
```

## Finding Packages

### NixOS Package Search

Browse all available packages:
- **Web**: https://search.nixos.org/packages
- Search by name, description, or category
- Check "unstable" channel for newer packages

### Common Package Name Patterns

| Tool | Nix Package Name |
|------|-----------------|
| Python 3.11 | `pkgs.python311` |
| Python 3.12 | `pkgs.python312` |
| Node.js 20 | `pkgs.nodejs-20_x` |
| Node.js 18 | `pkgs.nodejs-18_x` |
| Go | `pkgs.go` |
| Rust | `pkgs.rustc` |
| Ruby | `pkgs.ruby` |
| Java 17 | `pkgs.jdk17` |
| PHP | `pkgs.php` |
| PostgreSQL | `pkgs.postgresql` |
| MySQL | `pkgs.mysql` |
| Redis | `pkgs.redis` |
| SQLite | `pkgs.sqlite` |
| MongoDB tools | `pkgs.mongodb-tools` |
| FFmpeg | `pkgs.ffmpeg` |
| ImageMagick | `pkgs.imagemagick` |
| Git | `pkgs.git` |
| curl | `pkgs.curl` |
| wget | `pkgs.wget` |
| jq | `pkgs.jq` |
| vim | `pkgs.vim` |
| htop | `pkgs.htop` |
| GCC | `pkgs.gcc` |
| Make | `pkgs.gnumake` |
| cmake | `pkgs.cmake` |
| OpenSSL | `pkgs.openssl` |
| Nginx | `pkgs.nginx` |

### Replit-Specific Packages

Replit provides some custom packages:

```nix
pkgs.replitPackages.jest
pkgs.replitPackages.vscode-langservers-extracted
```

## Nix Channels

Replit uses Nix channels to version the package set. Configure in `.replit`:

```toml
[nix]
channel = "stable-23_11"
```

Common channels:
- `stable-23_11` — NixOS 23.11 (stable, default for older Repls)
- `stable-24_05` — NixOS 24.05
- `unstable` — Latest packages (may be less stable)

## Applying Configuration Changes

After editing `replit.nix`:

### Method 1: Restart Shell
```bash
# In the Shell tab, type:
exit
# The shell will restart and apply Nix changes
```

### Method 2: Refresh Nix Environment
```bash
# Force Nix to re-evaluate
nix-env -iA nixpkgs.PACKAGE_NAME
```

## System Dependencies UI

Instead of editing `replit.nix` manually, use the GUI:

1. Click **Tools** in the sidebar
2. Select **System Dependencies** (or type it in the tools search)
3. Search for packages by name
4. Click **Install**

Changes are automatically written to `replit.nix`.

## Advanced: Environment Variables in Nix

You can set environment variables via Nix shell hooks:

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
  ];
  
  env = {
    PYTHONPATH = "$REPL_HOME/.pythonlibs/lib/python3.11/site-packages";
    LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc]}";
  };
}
```

## Performance Notes

- Replit has optimized Nix startup times significantly ("Super Colliding Nix Stores")
- Initial package installation may take a moment
- Subsequent startups use cached packages
- The Nix store is shared across Repls on the same machine

## Nix vs. Docker

Replit uses Nix instead of Dockerfiles:

| Feature | Nix (Replit) | Dockerfile |
|---------|-------------|------------|
| Configuration | `replit.nix` | `Dockerfile` |
| Reproducibility | High | Medium |
| Package availability | nixpkgs (80k+) | Varies |
| Build caching | Excellent | Good |
| Learning curve | Moderate | Low |

## Troubleshooting

### Package Not Found
```bash
# Search nixpkgs
nix search nixpkgs PACKAGE_NAME

# Or search on search.nixos.org
```

### Build Failures
```bash
# Clear Nix cache and rebuild
rm -rf /nix/var/nix/gcroots/
nix-collect-garbage
```

### Version Conflicts
Specify exact versions or use version ranges in nixpkgs — check search.nixos.org for the exact attribute name.
