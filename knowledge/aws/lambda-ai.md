# AWS Lambda for AI Inference
> Source: https://logiciel.io/blog/aws-lambda-ai-inference, https://blaxel.ai/blog/aws-lambda-gpu, https://medium.com/@salmananwaar1127/best-practices-for-using-aws-lambda-for-model-inference-67cdbeeb3b61, https://aws.amazon.com/blogs/compute/deploying-ai-models-for-inference-with-aws-lambda-using-zip-packaging/
> Fetched: 2026-06-20

## What Lambda Can and Cannot Do for AI

AWS Lambda is a serverless compute service that runs code in response to events. For AI workloads, it occupies a specific niche:

**Good fit:**
- Orchestration layer that calls Bedrock, SageMaker, or external model APIs
- Lightweight preprocessing / postprocessing
- Small quantized models (ONNX, TFLite) that fit within memory/size limits
- API Gateway + Lambda as a managed inference proxy

**Poor fit:**
- Large model inference requiring GPU (Lambda has no GPU support as of 2026)
- Stateful multi-step agents that need persistent memory
- Long-running inference jobs (>15 minute hard timeout)
- Training or fine-tuning

## Lambda Limits Relevant to AI

| Limit | Value |
|-------|-------|
| Memory | 128 MB – 10,240 MB |
| Ephemeral storage (/tmp) | 512 MB – 10,240 MB |
| Timeout | 15 minutes (900 seconds) |
| Deployment package (zip) | 250 MB (unzipped) |
| Container image size | Up to 10 GB |
| Payload size (synchronous) | 6 MB (request + response) |
| Payload size (async) | 256 KB |
| CPU | Proportional to memory (1 vCPU at 1,769 MB) |
| GPU | Not supported |

**Key takeaway**: Lambda supports up to 10 GB container images and 10 GB RAM, which is enough for many quantized/small models. But there is no GPU — CPU inference only.

## Pattern 1: Lambda as Bedrock Proxy (Most Common)

Lambda sits behind API Gateway and forwards requests to Bedrock. This adds authentication, rate limiting, request logging, and input validation without managing any servers.

```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def lambda_handler(event, context):
    # Parse incoming request (from API Gateway)
    body = json.loads(event.get("body", "{}"))
    user_message = body.get("message", "")

    if not user_message:
        return {"statusCode": 400, "body": json.dumps({"error": "No message provided"})}

    # Call Bedrock
    response = bedrock.converse(
        modelId="anthropic.claude-sonnet-4-6-v1:0",
        messages=[{
            "role": "user",
            "content": [{"text": user_message}]
        }],
        inferenceConfig={"maxTokens": 1024}
    )

    reply = response["output"]["message"]["content"][0]["text"]

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"reply": reply})
    }
```

### Required IAM permissions for the Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:Converse",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

## Pattern 2: API Gateway + Lambda Architecture

```
Client → API Gateway → Lambda → Bedrock / SageMaker Endpoint
                            ↓
                        DynamoDB (conversation history)
                            ↓
                        S3 (logs, documents)
```

API Gateway provides:
- HTTPS endpoint with TLS
- API key authentication or Cognito/JWT auth
- Request throttling and quota management
- Request/response transformation
- Stage management (dev/staging/prod)

Deployment via SAM template:
```yaml
# template.yaml
Resources:
  InferenceFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      Runtime: python3.12
      MemorySize: 2048
      Timeout: 120
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /chat
            Method: post
```

## Pattern 3: Lambda with Container Image (for Larger Models)

For ML models that exceed the 250 MB zip limit (e.g., ONNX models, sentence transformers), package as a container image.

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy model files
COPY model/ /var/task/model/
COPY app.py /var/task/

CMD ["app.lambda_handler"]
```

```python
# app.py — lightweight ONNX inference example
import onnxruntime as ort
import numpy as np
import json

# Load model at cold start (outside handler)
session = ort.InferenceSession("/var/task/model/model.onnx")

def lambda_handler(event, context):
    body = json.loads(event["body"])
    input_data = np.array(body["input"], dtype=np.float32)

    outputs = session.run(None, {"input": input_data})
    return {
        "statusCode": 200,
        "body": json.dumps({"prediction": outputs[0].tolist()})
    }
```

Build and push to ECR:
```bash
aws ecr create-repository --repository-name my-inference-lambda
docker build -t my-inference-lambda .
docker tag my-inference-lambda:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-inference-lambda:latest
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-inference-lambda:latest
```

## Performance Tuning

**Memory**: More memory = more CPU. For CPU inference, bump memory significantly:
- 128 MB (default): minimal processing
- 3,008 MB: ~1.7 vCPU — good for transformer inference
- 10,240 MB: ~6 vCPUs — maximum CPU parallelism

**Cold starts**: Lambda functions have cold starts when a new container initializes. For AI, this is significant because model loading is slow.

Strategies to reduce cold start impact:
- **Provisioned concurrency**: Keep N instances pre-warmed (costs money even when idle)
- **SnapStart** (Java only, as of 2026): Not applicable to Python
- **Keep models small**: Load smaller quantized models (ONNX Q8) for faster init
- **Load model outside handler**: `session = ort.InferenceSession(...)` at module level, not inside `lambda_handler`

**Timeout**: Default is 3 seconds. For AI inference, set to at least 60–120 seconds. For Bedrock calls that might stream large responses, set to 300+ seconds.

## Streaming Responses via Lambda

Lambda supports streaming responses (Invoke URL, not API Gateway) via Lambda Response Streaming:

```python
import boto3

bedrock = boto3.client("bedrock-runtime")

# Lambda streaming handler
def lambda_handler(event, context):
    # Note: streaming via Lambda requires Response Streaming feature
    # Use API Gateway WebSocket or HTTP streaming endpoint
    pass
```

For streaming AI responses to web clients, consider:
- API Gateway WebSocket API
- AWS AppSync subscriptions
- Server-sent events via API Gateway HTTP API

## Cost

Lambda pricing:
- **Duration**: $0.0000166667 per GB-second
- **Requests**: $0.20 per 1M requests
- Free tier: 1M requests/month, 400,000 GB-seconds/month

Example: A Lambda with 2 GB RAM running for 5 seconds per request, 10,000 requests/month:
- Duration: 2 GB × 5s × 10,000 = 100,000 GB-s × $0.0000166667 = **$1.67**
- Requests: 10,000 × $0.0000002 = **$0.002**
- Total: **~$1.67/month** (mostly Bedrock costs will dominate)

Lambda is extremely cheap for the orchestration layer. The model inference (Bedrock, SageMaker) is where real costs accumulate.
