# Amazon Bedrock Guardrails
> Source: https://aws.amazon.com/bedrock/guardrails/, https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-components.html, https://gerardo.dev/en/bedrock-guardrails.html
> Fetched: 2026-06-20

## What are Guardrails?

Guardrails for Amazon Bedrock implement configurable safety policies for your AI applications. They work across all Bedrock models (including third-party models via the Converse API) and can be applied to:
- Direct model invocations
- Bedrock Agents
- Knowledge Base queries

## Safety Policies Available

1. **Content Filters** — Block harmful content by category (hate, insults, sexual, violence, misconduct, prompt attack)
2. **Denied Topics** — Define custom off-limits topics (e.g., "competitor products", "legal advice")
3. **Word Filters** — Block specific words or phrases
4. **Sensitive Information (PII) Filters** — Detect/redact personally identifiable information
5. **Grounding Checks** — Detect hallucinations in RAG responses
6. **Contextual Grounding** — Check factual accuracy against a reference source

## Creating a Guardrail (Python/boto3)

```python
import boto3

bedrock = boto3.client("bedrock", region_name="us-east-1")

response = bedrock.create_guardrail(
    name="my-content-guardrail",
    description="Safety guardrail for customer service bot",
    
    # Topic blocks
    topicPolicyConfig={
        "topicsConfig": [
            {
                "name": "Legal Advice",
                "definition": "Any request for legal advice, legal opinions, or legal representation",
                "examples": ["Can I sue them?", "Is this legal?"],
                "type": "DENY"
            },
            {
                "name": "Competitor Products",
                "definition": "Questions about or recommendations of competitor products",
                "examples": ["Should I use OpenAI instead?"],
                "type": "DENY"
            }
        ]
    },
    
    # Content category filters
    contentPolicyConfig={
        "filtersConfig": [
            {
                "type": "SEXUAL",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "VIOLENCE",
                "inputStrength": "MEDIUM",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "HATE",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "INSULTS",
                "inputStrength": "MEDIUM",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "MISCONDUCT",
                "inputStrength": "MEDIUM",
                "outputStrength": "MEDIUM"
            },
            {
                "type": "PROMPT_ATTACK",
                "inputStrength": "HIGH",
                "outputStrength": "NONE"  # Only applies to input
            }
        ]
    },
    
    # PII / sensitive information
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": "EMAIL", "action": "ANONYMIZE"},
            {"type": "PHONE", "action": "ANONYMIZE"},
            {"type": "NAME", "action": "ANONYMIZE"},
            {"type": "US_SOCIAL_SECURITY_NUMBER", "action": "BLOCK"},
            {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
            {"type": "AWS_ACCESS_KEY", "action": "BLOCK"},
            {"type": "ADDRESS", "action": "ANONYMIZE"},
            {"type": "AGE", "action": "NONE"},  # detect but don't mask
        ],
        "regexesConfig": [
            {
                "name": "internal-employee-id",
                "description": "Internal employee ID format EMP-XXXXXXXX",
                "pattern": r"EMP-\d{8}",
                "action": "ANONYMIZE"
            }
        ]
    },
    
    # Word blocks
    wordPolicyConfig={
        "wordsConfig": [
            {"text": "competitor_xyz"},
            {"text": "badword1"},
        ],
        "managedWordListsConfig": [
            {"type": "PROFANITY"}  # AWS-maintained profanity list
        ]
    },
    
    # Grounding check (hallucination detection)
    contextualGroundingPolicyConfig={
        "filtersConfig": [
            {
                "type": "GROUNDING",
                "threshold": 0.7  # 0-1; higher = stricter
            },
            {
                "type": "RELEVANCE",
                "threshold": 0.7
            }
        ]
    },
    
    # What to show when blocked
    blockedInputMessaging="I'm sorry, I can't process that request.",
    blockedOutputsMessaging="I'm sorry, I can't provide that information."
)

guardrail_id = response["guardrailId"]
guardrail_arn = response["guardrailArn"]
print(f"Created guardrail: {guardrail_id}")

# Publish a version (required before use in production)
version_response = bedrock.create_guardrail_version(guardrailIdentifier=guardrail_id)
guardrail_version = version_response["version"]
print(f"Version: {guardrail_version}")
```

## Using a Guardrail with Converse API

```python
import boto3

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock_runtime.converse(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    messages=[
        {
            "role": "user",
            "content": [{"text": "What is your social security number?"}]
        }
    ],
    guardrailConfig={
        "guardrailIdentifier": "my-guardrail-id",  # ID or ARN
        "guardrailVersion": "1",  # "DRAFT" for testing, or a published version number
        "trace": "enabled"  # See what the guardrail matched
    }
)

# Check if guardrail blocked
if response.get("stopReason") == "guardrail_intervened":
    print("Guardrail blocked this response")
    print(response["output"]["message"]["content"][0]["text"])  # blocked message
else:
    print(response["output"]["message"]["content"][0]["text"])
```

## Using a Guardrail with InvokeModel

```python
import boto3
import json

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    guardrailIdentifier="my-guardrail-id",
    guardrailVersion="1",
    trace="ENABLED",  # "ENABLED" or "DISABLED"
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "User message here"}]
    }),
    contentType="application/json",
    accept="application/json"
)

result = json.loads(response["body"].read())
```

## Streaming with Guardrails

```python
response = bedrock_runtime.converse_stream(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    messages=[{"role": "user", "content": [{"text": "Tell me about..."}]}],
    guardrailConfig={
        "guardrailIdentifier": "my-guardrail-id",
        "guardrailVersion": "1",
        "streamProcessingMode": "SYNCHRONOUS",  # Check before streaming, "ASYNCHRONOUS" for async
        "trace": "enabled"
    }
)

for event in response["stream"]:
    if "contentBlockDelta" in event:
        print(event["contentBlockDelta"]["delta"].get("text", ""), end="")
    if "messageStop" in event:
        if event["messageStop"].get("stopReason") == "guardrail_intervened":
            print("\n[GUARDRAIL INTERVENED]")
```

## Apply Guardrail to Arbitrary Text

You can apply guardrails outside of model calls (e.g., for user inputs):

```python
response = bedrock_runtime.apply_guardrail(
    guardrailIdentifier="my-guardrail-id",
    guardrailVersion="1",
    source="INPUT",  # "INPUT" or "OUTPUT"
    content=[
        {
            "text": {
                "text": "This is the content to check"
            }
        }
    ]
)

print(response["action"])  # "NONE" or "GUARDRAIL_INTERVENED"
print(response["outputs"])  # Masked/blocked output
print(response["assessments"])  # What triggered the guardrail
```

## PII Entity Types

Supported PII types for detection/anonymization:
```
ADDRESS
AGE
AWS_ACCESS_KEY
AWS_SECRET_KEY
CA_HEALTH_NUMBER
CA_SOCIAL_INSURANCE_NUMBER
CREDIT_DEBIT_CARD_CVV
CREDIT_DEBIT_CARD_EXPIRY
CREDIT_DEBIT_CARD_NUMBER
EMAIL
DRIVER_ID
IP_ADDRESS
LICENSE_PLATE
MAC_ADDRESS
NAME
PASSWORD
PHONE
PIN
SWIFT_CODE
UK_NATIONAL_HEALTH_SERVICE_NUMBER
UK_NATIONAL_INSURANCE_NUMBER
UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER
URL
USERNAME
US_BANK_ACCOUNT_NUMBER
US_BANK_ROUTING_NUMBER
US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER
US_PASSPORT_NUMBER
US_SOCIAL_SECURITY_NUMBER
VEHICLE_IDENTIFICATION_NUMBER
```

## Content Filter Categories and Strengths

| Category | Description | Available Strengths |
|----------|-------------|---------------------|
| SEXUAL | Explicit sexual content | NONE, LOW, MEDIUM, HIGH |
| VIOLENCE | Violent content | NONE, LOW, MEDIUM, HIGH |
| HATE | Hate speech | NONE, LOW, MEDIUM, HIGH |
| INSULTS | Personal attacks | NONE, LOW, MEDIUM, HIGH |
| MISCONDUCT | Illegal activities | NONE, LOW, MEDIUM, HIGH |
| PROMPT_ATTACK | Jailbreaking attempts (input only) | NONE, LOW, MEDIUM, HIGH |

## Pricing

| Component | Price |
|-----------|-------|
| Text units processed (input/output) | $0.75 per 1,000 text units |
| Image units | $0.0006 per image |
| Contextual grounding (1K tokens) | $0.10 |

One text unit = 1,000 characters. Processing is billed separately from model invocation.

## Guardrail Trace (Debugging)

Enable trace to see what the guardrail matched:

```python
response = bedrock_runtime.converse(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    messages=[...],
    guardrailConfig={
        "guardrailIdentifier": "my-guardrail-id",
        "guardrailVersion": "1",
        "trace": "enabled"
    }
)

# Trace information appears in the response
trace = response.get("trace", {})
guardrail_trace = trace.get("guardrail", {})
print(guardrail_trace)
# Shows: which policies triggered, what was masked, action taken
```

## Managing Guardrails

```python
# List guardrails
response = bedrock.list_guardrails()
for g in response["guardrails"]:
    print(g["guardrailId"], g["name"], g["status"])

# Get guardrail details
guardrail = bedrock.get_guardrail(
    guardrailIdentifier="my-guardrail-id",
    guardrailVersion="1"
)

# Update guardrail
bedrock.update_guardrail(
    guardrailIdentifier="my-guardrail-id",
    name="updated-name",
    # ... updated config
)

# Delete guardrail
bedrock.delete_guardrail(guardrailIdentifier="my-guardrail-id")
```

## IAM Policy for Guardrails

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:CreateGuardrail",
        "bedrock:UpdateGuardrail",
        "bedrock:DeleteGuardrail",
        "bedrock:GetGuardrail",
        "bedrock:ListGuardrails",
        "bedrock:CreateGuardrailVersion",
        "bedrock:ApplyGuardrail"
      ],
      "Resource": "*"
    }
  ]
}
```
