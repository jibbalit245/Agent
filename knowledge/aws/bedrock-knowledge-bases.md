# Amazon Bedrock Knowledge Bases (RAG)
> Source: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html, https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html
> Fetched: 2026-06-20

## What are Knowledge Bases?

Knowledge Bases for Amazon Bedrock is a fully managed RAG (Retrieval Augmented Generation) pipeline. It:
1. Ingests documents from S3 (or other sources)
2. Chunks and embeds them into a vector store
3. Provides APIs to retrieve relevant chunks and generate answers

You don't manage embedding models or vector databases directly — Bedrock handles it.

## Vector Store Options

| Vector Store | Notes |
|-------------|-------|
| Amazon OpenSearch Serverless | Fully managed; most common choice |
| Amazon OpenSearch Managed Cluster | More control, added March 2025 |
| Amazon Aurora (PostgreSQL + pgvector) | SQL-native vector search |
| Amazon Neptune Analytics | Graph + vector hybrid |
| Amazon S3 Vectors | New, cost-effective for infrequent queries (sub-second latency) |
| Pinecone | External managed vector DB |
| MongoDB Atlas | External managed vector DB |
| Redis Enterprise Cloud | External managed vector DB |

For most use cases, start with **Amazon OpenSearch Serverless** (zero management overhead) or **S3 Vectors** (cheapest).

## Embedding Models Supported

| Model | Model ID | Dimensions |
|-------|----------|-----------|
| Titan Embeddings V2 | `amazon.titan-embed-text-v2:0` | 256, 512, or 1024 |
| Titan Embeddings V1 | `amazon.titan-embed-text-v1` | 1536 |
| Cohere Embed English | `cohere.embed-english-v3` | 1024 |
| Cohere Embed Multilingual | `cohere.embed-multilingual-v3` | 1024 |

## Data Sources Supported

- Amazon S3 (most common)
- Confluence
- SharePoint
- Salesforce
- Web Crawling (URLs)
- Custom data sources (via API)

## Setting Up a Knowledge Base (Console Flow)

1. Go to **Bedrock > Knowledge Bases > Create**
2. Select data source (S3 bucket with documents)
3. Select embedding model (Titan V2 recommended)
4. Select vector store (OpenSearch Serverless for simplest setup)
5. Wait for ingestion to complete
6. Test with RetrieveAndGenerate

## Creating a Knowledge Base (boto3)

### Step 1: Create IAM Role

The knowledge base needs a role with permissions to access S3 and call Bedrock:

```python
# You typically create this via console or CloudFormation
# The role needs:
# - s3:GetObject, s3:ListBucket on your S3 bucket
# - bedrock:InvokeModel for the embedding model
```

### Step 2: Create Knowledge Base

```python
import boto3

bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")

kb_response = bedrock_agent.create_knowledge_base(
    name="my-knowledge-base",
    description="Product documentation knowledge base",
    roleArn="arn:aws:iam::123456789012:role/BedrockKBRole",
    
    knowledgeBaseConfiguration={
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
        }
    },
    
    storageConfiguration={
        "type": "OPENSEARCH_SERVERLESS",
        "opensearchServerlessConfiguration": {
            "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/my-collection",
            "vectorIndexName": "bedrock-kb-index",
            "fieldMapping": {
                "vectorField": "bedrock-knowledge-base-default-vector",
                "textField": "AMAZON_BEDROCK_TEXT_CHUNK",
                "metadataField": "AMAZON_BEDROCK_METADATA"
            }
        }
    }
)

kb_id = kb_response["knowledgeBase"]["knowledgeBaseId"]
print(f"Knowledge Base ID: {kb_id}")
```

### Step 3: Create Data Source (S3)

```python
ds_response = bedrock_agent.create_data_source(
    knowledgeBaseId=kb_id,
    name="my-s3-docs",
    
    dataSourceConfiguration={
        "type": "S3",
        "s3Configuration": {
            "bucketArn": "arn:aws:s3:::my-documents-bucket",
            "inclusionPrefixes": ["docs/", "manuals/"]  # Optional: only ingest these prefixes
        }
    },
    
    vectorIngestionConfiguration={
        "chunkingConfiguration": {
            "chunkingStrategy": "FIXED_SIZE",
            "fixedSizeChunkingConfiguration": {
                "maxTokens": 512,
                "overlapPercentage": 20
            }
        }
    }
)

ds_id = ds_response["dataSource"]["dataSourceId"]
print(f"Data Source ID: {ds_id}")
```

### Step 4: Sync Data

```python
# Trigger ingestion
sync_response = bedrock_agent.start_ingestion_job(
    knowledgeBaseId=kb_id,
    dataSourceId=ds_id
)
job_id = sync_response["ingestionJob"]["ingestionJobId"]

# Poll for completion
import time
while True:
    job = bedrock_agent.get_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=ds_id,
        ingestionJobId=job_id
    )
    status = job["ingestionJob"]["status"]
    print(f"Status: {status}")
    if status in ["COMPLETE", "FAILED", "STOPPED"]:
        break
    time.sleep(10)
```

## Querying a Knowledge Base

### Option 1: RetrieveAndGenerate (Full RAG)

Retrieves relevant chunks AND generates a response using a foundation model:

```python
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

response = bedrock_agent_runtime.retrieve_and_generate(
    input={
        "text": "How do I reset my password?"
    },
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": kb_id,
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6-v1:0",
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {
                    "numberOfResults": 5  # How many chunks to retrieve
                }
            }
        }
    },
    sessionId="session-abc123"  # Keep for multi-turn conversations
)

print(response["output"]["text"])  # Generated answer

# Citations
for citation in response.get("citations", []):
    for ref in citation.get("retrievedReferences", []):
        print(f"Source: {ref['location']['s3Location']['uri']}")
        print(f"Content: {ref['content']['text'][:200]}...")
```

### Option 2: Retrieve Only

Just retrieve relevant chunks, without generating a response:

```python
retrieve_response = bedrock_agent_runtime.retrieve(
    knowledgeBaseId=kb_id,
    retrievalQuery={
        "text": "password reset procedure"
    },
    retrievalConfiguration={
        "vectorSearchConfiguration": {
            "numberOfResults": 10,
            "overrideSearchType": "HYBRID"  # "SEMANTIC" or "HYBRID"
        }
    }
)

for result in retrieve_response["retrievalResults"]:
    score = result["score"]
    content = result["content"]["text"]
    location = result["location"]["s3Location"]["uri"]
    print(f"Score: {score:.3f} | Source: {location}")
    print(f"Content: {content[:200]}...\n")
```

### Option 3: Use with Converse API

Pass knowledge base results as context in a Converse call:

```python
# 1. Retrieve relevant chunks
chunks = bedrock_agent_runtime.retrieve(...)["retrievalResults"]
context = "\n\n".join([r["content"]["text"] for r in chunks])

# 2. Include in Converse call
response = bedrock_runtime.converse(
    modelId="anthropic.claude-sonnet-4-6-v1:0",
    system=[{
        "text": f"You are a helpful assistant. Use the following context to answer questions:\n\n{context}"
    }],
    messages=[{
        "role": "user",
        "content": [{"text": "How do I reset my password?"}]
    }]
)
```

## Advanced Features

### Agentic Retrieval (Multi-hop)

For complex queries that require multiple retrieval steps:

```python
response = bedrock_agent_runtime.retrieve_and_generate(
    input={"text": "Compare the Q3 and Q4 2024 revenue figures and explain the difference"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": kb_id,
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6-v1:0",
            "orchestrationConfiguration": {
                "queryTransformationConfiguration": {
                    "type": "QUERY_DECOMPOSITION"  # Break complex queries into sub-queries
                }
            }
        }
    }
)
```

### Custom Chunking Strategies

```python
# Hierarchical chunking (parent-child, better context)
"chunkingConfiguration": {
    "chunkingStrategy": "HIERARCHICAL",
    "hierarchicalChunkingConfiguration": {
        "levelConfigurations": [
            {"maxTokens": 1500},  # Parent chunk
            {"maxTokens": 300}    # Child chunk
        ],
        "overlapTokens": 60
    }
}

# Semantic chunking (splits on topic boundaries)
"chunkingConfiguration": {
    "chunkingStrategy": "SEMANTIC",
    "semanticChunkingConfiguration": {
        "maxTokens": 300,
        "bufferSize": 0,
        "breakpointPercentileThreshold": 95
    }
}

# No chunking (whole documents as single chunks)
"chunkingConfiguration": {
    "chunkingStrategy": "NONE"
}
```

## Supported Document Types

- PDF
- Microsoft Word (.docx, .doc)
- Microsoft PowerPoint (.pptx)
- HTML
- Markdown (.md)
- Plain text (.txt)
- CSV
- JSON
- JSONL
- XML

## Pricing

| Component | Price |
|-----------|-------|
| Storage (vector store) | Varies by vector store choice |
| Embedding (per 1K tokens) | ~$0.0001 (Titan V2) |
| Retrieval (per 1K queries) | ~$0.005 |
| RetrieveAndGenerate | Embedding + Retrieval + Model inference |

OpenSearch Serverless is billed separately by AWS (~$700/month minimum for 2 OCUs; one for indexing, one for search). For cost-sensitive use cases with infrequent queries, use S3 Vectors instead.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ResourceNotFoundException` | KB ID wrong or in different region | Check region and ID |
| `AccessDeniedException` | Missing IAM permissions | Add `bedrock:Retrieve`, `bedrock-agent-runtime:RetrieveAndGenerate` |
| Ingestion job FAILED | S3 bucket permissions wrong | Ensure KB role has S3 read access |
| Empty results | No documents match query | Check ingestion completed; lower similarity threshold |
