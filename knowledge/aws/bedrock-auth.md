# Bedrock Authentication (IAM, boto3, Credentials)
> Source: https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html, https://medium.com/genai-io/aws-bedrock-quick-setup-with-boto3-94ba0d0088ca, https://aws.amazon.com/blogs/machine-learning/accelerate-ai-development-with-amazon-bedrock-api-keys/
> Fetched: 2026-06-20

## Overview

Authentication for Amazon Bedrock uses standard AWS IAM mechanisms. There are four main credential approaches, roughly in order of preference for production use:

1. IAM Role (EC2 instance profile / ECS task role / Lambda execution role)
2. IAM Role assumption (cross-account or named role)
3. AWS Bedrock API Keys (new, short-lived, good for development)
4. Long-lived IAM User access keys (least preferred; avoid for production)

## Required IAM Permissions

Your IAM user or role needs the following actions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:Converse",
        "bedrock:ConverseStream",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "*"
    }
  ]
}
```

For more restrictive policies, scope `Resource` to specific model ARNs:
```
arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6-v1:0
```

## Method 1: IAM Role (Recommended for Production)

When running on AWS infrastructure (EC2, Lambda, ECS, SageMaker), attach an IAM role with Bedrock permissions. boto3 picks up credentials automatically from the instance metadata service — no credential files needed.

```python
import boto3

# No credentials needed — boto3 uses instance/task role automatically
client = boto3.client("bedrock-runtime", region_name="us-east-1")
```

## Method 2: IAM Role Assumption

If Bedrock access is gated behind a specific IAM role (common in enterprise setups):

```python
import boto3

sts = boto3.client("sts")
assumed = sts.assume_role(
    RoleArn="arn:aws:iam::123456789012:role/BedrockAccessRole",
    RoleSessionName="bedrock-session"
)

creds = assumed["Credentials"]
client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)
```

You can also set `BEDROCK_ASSUME_ROLE` as an environment variable in frameworks that support it.

## Method 3: Bedrock API Keys (2025+, Good for Dev)

Amazon Bedrock now supports short-lived API keys that bypass the standard IAM credential chain. They use the IAM permissions of your current principal and expire at session end (or up to 12 hours).

Generate via console (Bedrock > API Keys > Create) or CLI:
```bash
aws bedrock create-api-key --name my-dev-key
```

Use in code:
```python
import boto3
from botocore.auth import BearerTokenAuth

# Or pass as Authorization: Bearer <key> in HTTP requests
```

These keys are good for rapid prototyping but don't replace IAM roles for production.

## Method 4: Long-Lived Access Keys (Avoid in Production)

```python
import boto3

client = boto3.client(
    "bedrock-runtime",
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region_name="us-east-1"
)
```

**Do not hardcode credentials in source code.** Use environment variables or `~/.aws/credentials` instead.

## Credential File Setup (~/.aws/credentials)

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[bedrock-prod]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

Config file (~/.aws/config):
```ini
[default]
region = us-east-1

[profile bedrock-prod]
region = us-west-2
```

Use a specific profile:
```python
session = boto3.Session(profile_name="bedrock-prod")
client = session.client("bedrock-runtime")
```

## Environment Variables

boto3 checks these environment variables automatically:

| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Access key ID |
| `AWS_SECRET_ACCESS_KEY` | Secret access key |
| `AWS_SESSION_TOKEN` | Session token (for temporary credentials) |
| `AWS_DEFAULT_REGION` | Default region (e.g., `us-east-1`) |
| `AWS_PROFILE` | Named profile from `~/.aws/credentials` |

Example:
```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_DEFAULT_REGION="us-east-1"
```

## boto3 Credential Chain (Resolution Order)

boto3 tries credentials in this order:
1. Explicitly passed in code (`aws_access_key_id=...`)
2. Environment variables (`AWS_ACCESS_KEY_ID`, etc.)
3. AWS credentials file (`~/.aws/credentials`)
4. AWS config file (`~/.aws/config`)
5. Container credentials (ECS task role)
6. Instance metadata (EC2 instance profile)

## Two Different Bedrock Clients

Note that there are **two** separate boto3 service clients for Bedrock:

| Client | Service Name | Purpose |
|--------|-------------|---------|
| `bedrock` | `bedrock` | Management plane: list models, get model info, manage provisioned throughput |
| `bedrock-runtime` | `bedrock-runtime` | Data plane: invoke models, stream responses |

For inference, you always use `bedrock-runtime`.

## Common Auth Pitfalls

- **Wrong region**: Model might not be available in your configured region. Set `AWS_DEFAULT_REGION` or pass `region_name` explicitly.
- **Missing permissions**: `AccessDeniedException` usually means the IAM policy is missing `bedrock:InvokeModel` or `bedrock:Converse`.
- **Expired credentials**: Temporary credentials (session tokens, assumed roles) expire. Implement refresh logic.
- **SCP blocks**: Even if your IAM policy allows it, an SCP at the org level can block Bedrock access. Check with your AWS admin.
