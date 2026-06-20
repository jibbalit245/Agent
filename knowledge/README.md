# Knowledge Base

This directory contains curated platform documentation used by the `knowledge_search` tool.

## Structure

Each subdirectory corresponds to a platform:

```
knowledge/
├── anthropic/      — Claude API, model IDs, pricing, rate limits
├── huggingface/    — Hub, Inference API, Spaces, serverless endpoints
├── openai/         — API, models, embeddings, fine-tuning
├── openrouter/     — Routing, pricing, model availability
├── aws/            — Bedrock, SageMaker, IAM setup
├── google/         — Vertex AI, Gemini API, service accounts
├── runpod/         — Serverless endpoints, GPU pods, templates
├── replit/         — Deployments, secrets, environment setup
└── github/         — Actions, Codespaces, model marketplace
```

Each file is a markdown document with `## ` section headers, sourced from official documentation.
The first lines of each file include a comment with the source URL and fetch date.

## Refreshing the knowledge base

Run the fetch script to update all platforms:

```bash
python scripts/fetch_docs.py
```

Or refresh a single platform:

```bash
python scripts/fetch_docs.py --platform anthropic
```

The script uses `httpx` and `beautifulsoup4` to fetch pages and clean them to markdown.
It saves output to `knowledge/<platform>/<slug>.md`.

## Adding new sources

Edit the `SOURCES` dict in `scripts/fetch_docs.py` to add URLs for a platform,
then re-run the script.

## Notes

- Pricing and model lists change frequently — re-fetch monthly or when you notice stale answers.
- The `knowledge_search` tool scores sections by keyword frequency; put important terms in `## ` headers.
- Files in `.gitkeep`-only subdirectories are placeholders; populate them by running `fetch_docs.py`.
