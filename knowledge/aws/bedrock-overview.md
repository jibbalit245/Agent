# Amazon Bedrock Overview
> Source: https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html, https://bigdataboutique.com/blog/amazon-bedrock-explained-foundation-models-agents-knowledge-bases
> Fetched: 2026-06-20

## What is Amazon Bedrock?

Amazon Bedrock is a fully managed service that provides access to a diverse catalog of high-performing foundation models (FMs) from leading AI providers through a single API. It offers serverless infrastructure, so you can experiment with and deploy generative AI applications without managing underlying hardware or infrastructure. You pay only for what you use — no servers to provision or clusters to maintain.

Bedrock also includes higher-level features built on top of model access: Agents (for multi-step autonomous tasks), Knowledge Bases (RAG pipelines backed by vector stores), Guardrails (safety controls), Flows (visual workflow builder), and Evaluations (model quality assessment).

## Supported Foundation Models (as of 2026)

Bedrock provides access to models from many providers:

| Provider | Notable Models |
|----------|---------------|
| **Anthropic** | Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5 |
| **Meta** | Llama 3.3 70B, Llama 4 Scout, Llama 4 Maverick |
| **Mistral AI** | Mistral Large 3, Mixtral 8x7B |
| **Amazon** | Nova Pro, Nova Lite, Nova Micro, Titan Text Premier, Titan Embeddings |
| **AI21 Labs** | Jamba 1.5 Large, Jamba Instruct |
| **Cohere** | Command R+, Command R |
| **DeepSeek** | DeepSeek R1 |
| **Google** | Gemma (open-weight) |
| **OpenAI** | gpt-oss-120b, gpt-oss-20b (open-weight variants) |
| **Qwen** | Qwen3 |
| **Stability AI** | Stable Diffusion (image generation) |
| **NVIDIA** | Nemotron |
| **TwelveLabs** | Video understanding models |
| **Writer** | Palmyra |
| **Luma AI** | Video generation |
| **Marketplace** | 100+ additional specialized models via Bedrock Marketplace |

## Enabling Model Access

As of late 2025, Amazon Bedrock **automatically enables access to all serverless foundation models** in your AWS Region — the old "Model Access" page and manual enablement flow have been retired. You no longer need to manually request access for most models.

Exceptions:
- **AWS Marketplace models** still require explicit agreement via the console, `ListFoundationModelAgreementOffers` / `CreateFoundationModelAgreement` APIs.
- Account administrators can still restrict model access via **IAM policies** or **Service Control Policies (SCPs)**.

## Regional Availability

Bedrock is available across all commercial AWS regions. Cross-region inference (expanded in Q1 2026) lets you route requests across regions for higher availability and throughput. Key regions with broad model support include:
- `us-east-1` (N. Virginia) — widest model availability
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

Use **Global inference profiles** (prefix `global.`) for automatic cross-region routing, or region-specific profiles (prefix `us.`, `eu.`, etc.) for explicit regional control.

## Pricing Model

Bedrock uses three pricing modes:

1. **On-Demand** — Pay per token (input + output), no commitments. Best for variable/bursty traffic.
2. **Batch Inference** — 50% discount vs on-demand; submit large jobs with up to 24-hour turnaround. Asynchronous only.
3. **Provisioned Throughput** — Purchase committed capacity (model units) by the hour; 1-month or 6-month commitments. Best for steady high-volume workloads.

See `bedrock-pricing.md` for specific rates.

## Key Advantages (and Limitations)

**Advantages:**
- No infrastructure management; fully serverless
- Single API to access dozens of models
- Native AWS integrations (IAM, CloudWatch, VPC, S3)
- Built-in safety features (Guardrails)

**Limitations:**
- Cannot fine-tune all models (only some support it)
- Cold starts on serverless can add latency for infrequent calls
- Cross-region inference adds some latency vs same-region
- Some cutting-edge models arrive on other APIs first before Bedrock
