# GitHub Container Registry (GHCR)
> Source: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
> Fetched: 2026-06-20

## Overview

GitHub Container Registry (GHCR) hosts Docker and OCI container images at `ghcr.io`. It replaced the older Docker registry (`docker.pkg.github.com`) and is the recommended way to store and distribute container images on GitHub.

**Registry URL**: `ghcr.io`

**Image naming convention**: `ghcr.io/OWNER/IMAGE_NAME:TAG`

Examples:
- `ghcr.io/myorg/my-ml-image:latest`
- `ghcr.io/myuser/training-env:v1.2.3`
- `ghcr.io/myuser/training-env:sha-abc1234`

## Authentication

### In GitHub Actions (Recommended)

Use `GITHUB_TOKEN` — no setup required:

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

All workflows using GHCR should prefer `GITHUB_TOKEN` over a PAT — the package is automatically linked to the repository.

### Locally (CLI)

Using a Personal Access Token with `write:packages` and `read:packages` scopes:

```bash
# Login
echo $PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Or using gh CLI
echo $(gh auth token) | docker login ghcr.io -u $(gh api user --jq .login) --password-stdin
```

## Pushing Images

### Manual Push

```bash
# Build image
docker build -t ghcr.io/myorg/ml-training:latest .

# Push
docker push ghcr.io/myorg/ml-training:latest

# Tag with multiple tags
docker tag ghcr.io/myorg/ml-training:latest ghcr.io/myorg/ml-training:v1.0.0
docker push ghcr.io/myorg/ml-training:v1.0.0
```

### In GitHub Actions

#### Simple Build and Push

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/ml-image:latest
```

#### With Metadata and Multiple Tags

```yaml
- name: Extract metadata (tags, labels) for Docker
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository_owner }}/ml-image
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha,prefix=sha-

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

This generates tags like:
- `ghcr.io/myorg/ml-image:main` (branch push)
- `ghcr.io/myorg/ml-image:1.2.3` (release)
- `ghcr.io/myorg/ml-image:sha-abc1234` (commit SHA)

#### Build with Docker Layer Caching

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository_owner }}/ml-image:latest
    cache-from: type=gha          # GitHub Actions cache
    cache-to: type=gha,mode=max   # saves all layers
```

## Using GHCR Images in Actions

### As a Job Container

Run your entire job inside a container from GHCR:

```yaml
jobs:
  train:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/myorg/ml-training:latest
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
      env:
        PYTHONPATH: /workspace
    steps:
      - uses: actions/checkout@v4
      - run: python train.py  # runs inside the container
```

### As a Service Container

Spin up a sidecar service (e.g., database, model server):

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      model-server:
        image: ghcr.io/myorg/model-server:latest
        credentials:
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
        ports:
          - 8080:8080
    steps:
      - run: curl http://localhost:8080/health
```

## Storage and Pricing

### Free Limits (GitHub Packages)

| Account Type | Free Storage | Free Data Transfer |
|-------------|-------------|-------------------|
| Public packages | Unlimited | Unlimited |
| Private (GitHub Free) | 500MB | 1GB/month |
| Private (GitHub Pro) | 2GB | 10GB/month |
| Private (GitHub Team) | 2GB | 10GB/month |
| Private (Enterprise) | 50GB | 100GB/month |

**Public images are always free** — storage and bandwidth.

### Pricing Beyond Free Limits

- Storage: ~$0.008/GB/day (roughly $0.25/GB/month)
- Data transfer out: ~$0.50/GB

### Cost Optimization

- Make images public when possible (free storage + bandwidth)
- Use multi-stage builds to reduce final image size
- Use layer caching to speed up builds
- Periodically delete old/unused package versions

## Linking Packages to Repositories

When you publish a package from a workflow using `GITHUB_TOKEN`, the package is automatically linked to the repository. Otherwise link manually:

1. Go to package settings on GitHub
2. Under "Manage Actions access", add the repository

Linked packages inherit the repository's visibility and access control.

## Visibility and Access Control

- **Public packages**: Anyone can pull; push requires auth
- **Private packages**: Only authenticated users/orgs with access can pull or push

Change visibility: GitHub profile > Packages > Select package > Package Settings > Change visibility

```yaml
# Required permissions for pushing to GHCR
permissions:
  packages: write
  contents: read
```

## Pulling Images

```bash
# Public image (no auth needed)
docker pull ghcr.io/myorg/public-ml-image:latest

# Private image (requires auth)
docker pull ghcr.io/myorg/private-ml-image:latest
```

## Multi-Platform Builds (for ARM/GPU compatibility)

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push multi-platform
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository_owner }}/ml-image:latest
```

## Sources
- [Working with the Container registry - GitHub Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Publishing Docker images - GitHub Docs](https://docs.github.com/actions/guides/publishing-docker-images)
- [Publishing and installing a package with GitHub Actions - GitHub Docs](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions)
- [Running jobs in a container - GitHub Docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/run-jobs-in-a-container)
