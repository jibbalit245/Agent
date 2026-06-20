# Amazon Bedrock Agents
> Source: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html, https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
> Fetched: 2026-06-20

## What are Bedrock Agents?

Agents for Amazon Bedrock are fully managed autonomous AI agents that can:
- Break down complex tasks into steps
- Call APIs and Lambda functions (action groups)
- Query knowledge bases
- Remember context across sessions (Memory)
- Execute code (Code Interpreter)
- Use multiple sub-agents (multi-agent collaboration)

Agents use **ReAct** (Reasoning and Acting) orchestration: the FM reasons about what to do, selects actions, observes results, and iterates.

## Architecture

```
User → Agent (FM-based orchestrator)
              ↓
         ReAct loop:
         1. Reason (chain-of-thought)
         2. Act (call action group / query KB)
         3. Observe result
         4. Repeat until done
         5. Return final response to user
              ↓
    Action Groups (Lambda functions)
    Knowledge Bases (RAG)
    Memory (session context)
```

## Creating an Agent (boto3)

### Step 1: Create the Agent

```python
import boto3

bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")

agent_response = bedrock_agent.create_agent(
    agentName="customer-service-agent",
    description="Handles customer service inquiries",
    agentResourceRoleArn="arn:aws:iam::123456789012:role/BedrockAgentRole",
    foundationModel="anthropic.claude-sonnet-4-6-v1:0",
    instruction="""You are a customer service agent for Acme Corp.
    You help customers with:
    - Order tracking
    - Returns and refunds
    - Product information
    Always be polite and helpful. If you don't know something, say so.""",
    idleSessionTTLInSeconds=1800
)

agent_id = agent_response["agent"]["agentId"]
print(f"Agent ID: {agent_id}")
```

### Step 2: Create Action Group

Action groups define what APIs the agent can call. They consist of:
1. An OpenAPI schema describing the API
2. A Lambda function implementing the API

```python
import json

# Define OpenAPI schema
openapi_schema = json.dumps({
    "openapi": "3.0.0",
    "info": {"title": "Order API", "version": "1.0"},
    "paths": {
        "/get-order-status": {
            "get": {
                "summary": "Get the status of a customer order",
                "operationId": "getOrderStatus",
                "parameters": [
                    {
                        "name": "orderId",
                        "in": "query",
                        "required": True,
                        "description": "The order ID to check",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Order status",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "estimatedDelivery": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})

action_group_response = bedrock_agent.create_agent_action_group(
    agentId=agent_id,
    agentVersion="DRAFT",
    actionGroupName="order-actions",
    description="Actions for managing customer orders",
    
    actionGroupExecutor={
        "lambda": "arn:aws:lambda:us-east-1:123456789012:function:order-api-handler"
    },
    
    apiSchema={
        "payload": openapi_schema
    }
)
```

### Step 3: Lambda Function for Action Group

```python
# order-api-handler Lambda function
import json

def lambda_handler(event, context):
    """
    Lambda function that handles Bedrock Agent action group calls.
    
    Event format from Bedrock Agent:
    {
        "messageVersion": "1.0",
        "agent": {...},
        "inputText": "Check order ORD-12345",
        "sessionId": "session-abc",
        "actionGroup": "order-actions",
        "apiPath": "/get-order-status",
        "httpMethod": "GET",
        "parameters": [{"name": "orderId", "type": "string", "value": "ORD-12345"}],
        "requestBody": {...},
        "sessionAttributes": {},
        "promptSessionAttributes": {}
    }
    """
    
    action_group = event["actionGroup"]
    api_path = event["apiPath"]
    http_method = event["httpMethod"]
    parameters = {p["name"]: p["value"] for p in event.get("parameters", [])}
    
    if api_path == "/get-order-status":
        order_id = parameters.get("orderId")
        # Your business logic here
        status = get_order_status(order_id)
        
        response_body = {
            "application/json": {
                "body": json.dumps({
                    "status": status["status"],
                    "estimatedDelivery": status["estimatedDelivery"]
                })
            }
        }
    else:
        response_body = {
            "application/json": {
                "body": json.dumps({"error": "Unknown API path"})
            }
        }
    
    # Required response format for Bedrock Agents
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": 200,
            "responseBody": response_body
        },
        "sessionAttributes": event.get("sessionAttributes", {}),
        "promptSessionAttributes": event.get("promptSessionAttributes", {})
    }

def get_order_status(order_id):
    # Your actual logic here
    return {"status": "shipped", "estimatedDelivery": "2024-12-20"}
```

### Step 4: Associate Knowledge Base (Optional)

```python
bedrock_agent.associate_agent_knowledge_base(
    agentId=agent_id,
    agentVersion="DRAFT",
    knowledgeBaseId="my-kb-id",
    description="Product documentation knowledge base",
    knowledgeBaseState="ENABLED"
)
```

### Step 5: Prepare and Deploy

```python
# Prepare the agent (validates configuration)
bedrock_agent.prepare_agent(agentId=agent_id)

# Create an alias for the agent (required for invocation)
alias_response = bedrock_agent.create_agent_alias(
    agentId=agent_id,
    agentAliasName="prod-v1",
    description="Production alias"
)
alias_id = alias_response["agentAlias"]["agentAliasId"]
print(f"Agent Alias: {alias_id}")
```

## Invoking an Agent

```python
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# Single-turn invocation
response = bedrock_agent_runtime.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId="session-user-123",  # Use same session ID for multi-turn conversations
    inputText="What is the status of order ORD-12345?",
    enableTrace=True  # See the reasoning chain
)

# The response is a streaming EventStream
output_text = ""
trace_events = []

for event in response["completion"]:
    if "chunk" in event:
        output_text += event["chunk"]["bytes"].decode("utf-8")
    if "trace" in event:
        trace_events.append(event["trace"])

print("Response:", output_text)

# View trace for debugging
for trace in trace_events:
    print(json.dumps(trace, indent=2, default=str))
```

## Session Attributes

Pass custom data that persists across turns in the same session:

```python
response = bedrock_agent_runtime.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId="session-user-456",
    inputText="What's my order status?",
    sessionState={
        "sessionAttributes": {
            "customer_id": "CUST-789",
            "preferred_language": "en"
        },
        "promptSessionAttributes": {
            "current_date": "2024-12-15"  # These go into the prompt
        }
    }
)
```

## Memory (Persistent Across Sessions)

Enable memory to retain context from previous conversations:

```python
# Enable memory at agent level (configure in console or API)
# Then invoke with memory enabled:
response = bedrock_agent_runtime.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId="new-session-for-existing-user",
    memoryId="user-789-memory",  # Unique per user
    inputText="What did I order last time?"
)
```

## Code Interpreter (Built-in Tool)

Agents can execute Python code for data analysis:

```python
# Enable Code Interpreter when creating action group
bedrock_agent.create_agent_action_group(
    agentId=agent_id,
    agentVersion="DRAFT",
    actionGroupName="CodeInterpreter",
    actionGroupState="ENABLED",
    parentActionGroupSignature="AMAZON.CodeInterpreter"  # Built-in tool
)
```

## IAM Permissions Required

### Agent execution role (trust relationship):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "bedrock.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Agent execution role policies:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:*:*:function:your-action-group-lambda"
    }
  ]
}
```

### Lambda resource policy (to allow Bedrock to invoke it):
```bash
aws lambda add-permission \
  --function-name order-api-handler \
  --statement-id allow-bedrock-agent \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-account 123456789012
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ResourceNotFoundException` | Agent/alias ID wrong | Verify IDs in console |
| `AccessDeniedException` | Missing IAM permissions | Check agent role has InvokeModel |
| Lambda invocation failed | Lambda runtime error | Check Lambda CloudWatch logs |
| Agent returns generic response | Instruction too vague | Improve agent instruction with specific guidance |
| Trace shows wrong action selected | Schema definition unclear | Improve OpenAPI description fields |
