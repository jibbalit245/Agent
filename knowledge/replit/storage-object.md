# Replit Object Storage

> Source: https://docs.replit.com/storage/object-storage
> Updated URL: https://docs.replit.com/cloud-services/storage-and-databases/object-storage
> Last updated: 2026-06

## What is Object Storage?

Replit Object Storage allows you to **store and manage unstructured data** — files, images, videos, documents, and other binary content — in the cloud. It's similar to AWS S3 or Google Cloud Storage, providing a scalable object store for your apps.

Object Storage is backed by **Google Cloud Storage (GCS)** on the backend.

## Key Features

- Store any type of file (images, videos, documents, archives, etc.)
- Upload, download, list, and delete objects
- Accessible from both workspace and deployed apps
- SDKs for Python and TypeScript/JavaScript
- GCS API compatible for other languages

## Setup

### Accessing Object Storage

Object Storage is configured through the Replit dashboard. Each Repl can have associated storage buckets.

The bucket name/ID is available via the environment variable:
```
REPLIT_OBJECT_STORAGE_BUCKET
```

## Python SDK

### Installation

```bash
poetry add replit.object-storage
# or
pip install replit.object-storage
```

### Basic Usage

```python
from replit.object_storage import Client

# Initialize client (automatically uses REPLIT_OBJECT_STORAGE_BUCKET)
client = Client()

# Upload a file
client.upload_from_filename("my-object-key", "/path/to/local/file.jpg")

# Upload from bytes/string
client.upload_from_text("my-text-file", "Hello, World!")
client.upload_from_bytes("my-binary", b"\x00\x01\x02")

# Download a file
client.download_to_filename("my-object-key", "/path/to/save/file.jpg")

# Download as bytes
data = client.download_as_bytes("my-object-key")

# Download as text
text = client.download_as_text("my-text-file")

# List all objects
objects = client.list()
for obj in objects:
    print(obj.name, obj.size)

# Check if object exists
exists = client.exists("my-object-key")

# Delete an object
client.delete("my-object-key")

# Get object metadata
metadata = client.get("my-object-key")
print(metadata.name, metadata.size, metadata.content_type)
```

### Working with Specific Buckets

```python
from replit.object_storage import Client
import os

# Use default bucket
client = Client()

# Or specify a bucket explicitly
client = Client(bucket_id=os.environ['REPLIT_OBJECT_STORAGE_BUCKET'])
```

### File Upload Example

```python
from replit.object_storage import Client
from pathlib import Path

client = Client()

# Upload image
def upload_image(local_path: str, storage_key: str) -> None:
    client.upload_from_filename(storage_key, local_path)
    print(f"Uploaded {local_path} to {storage_key}")

# Upload with content type
client.upload_from_text(
    "config.json",
    '{"key": "value"}',
    content_type="application/json"
)
```

### Download Example

```python
from replit.object_storage import Client
import io

client = Client()

# Download to file
client.download_to_filename("photo.jpg", "/tmp/photo.jpg")

# Download to memory
image_bytes = client.download_as_bytes("photo.jpg")
image_stream = io.BytesIO(image_bytes)

# Process in memory (e.g., with PIL)
from PIL import Image
img = Image.open(image_stream)
```

## TypeScript/JavaScript SDK

### Installation

```bash
npm install @replit/object-storage
```

### Basic Usage

```typescript
import { Client } from "@replit/object-storage";

const client = new Client();

// Upload
await client.uploadFromFilename("my-key", "./local-file.jpg");
await client.uploadFromText("hello.txt", "Hello, World!");
await client.uploadFromBytes("data.bin", Buffer.from([0, 1, 2]));

// Download
await client.downloadToFilename("my-key", "./downloaded.jpg");
const bytes = await client.downloadAsBytes("my-key");
const text = await client.downloadAsText("hello.txt");

// List objects
const objects = await client.list();
objects.forEach(obj => console.log(obj.name, obj.size));

// Check existence
const exists = await client.exists("my-key");

// Delete
await client.delete("my-key");
```

### JavaScript (CommonJS)

```javascript
const { Client } = require("@replit/object-storage");

const client = new Client();

async function main() {
  // Upload a file
  await client.uploadFromText("greeting.txt", "Hello from Replit!");
  
  // List files
  const files = await client.list();
  console.log("Files:", files.map(f => f.name));
  
  // Download
  const content = await client.downloadAsText("greeting.txt");
  console.log("Content:", content);
}

main();
```

## Using GCS APIs (Other Languages)

For languages without a Replit SDK, use the Google Cloud Storage API directly:

```python
from google.cloud import storage
import os

# GCS credentials are automatically configured by Replit
client = storage.Client()
bucket = client.bucket(os.environ['REPLIT_OBJECT_STORAGE_BUCKET'])

# Upload
blob = bucket.blob("my-object")
blob.upload_from_filename("local-file.txt")

# Download
blob = bucket.blob("my-object")
blob.download_to_filename("downloaded.txt")
```

## Common Use Cases

### Image Upload/Storage (Flask)

```python
from flask import Flask, request, jsonify
from replit.object_storage import Client
import uuid

app = Flask(__name__)
storage = Client()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    key = f"uploads/{uuid.uuid4()}/{file.filename}"
    
    # Save to temp and upload
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)
    storage.upload_from_filename(key, temp_path)
    
    return jsonify({'key': key, 'url': f"/files/{key}"})

@app.route('/files/<path:key>')
def get_file(key):
    data = storage.download_as_bytes(key)
    return data
```

### Data Persistence

```python
import json
from replit.object_storage import Client

client = Client()

def save_data(key: str, data: dict) -> None:
    """Save JSON data to object storage."""
    client.upload_from_text(key, json.dumps(data))

def load_data(key: str) -> dict:
    """Load JSON data from object storage."""
    if client.exists(key):
        text = client.download_as_text(key)
        return json.loads(text)
    return {}

# Usage
save_data("user-settings.json", {"theme": "dark", "language": "en"})
settings = load_data("user-settings.json")
```

## Pricing

Object Storage pricing is based on:
- **Storage used** (GB per month)
- **Operations** (reads, writes, lists)
- **Data transfer** (egress)

Exact pricing is available in the Replit billing dashboard. Core plan credits can be used for Object Storage costs.

## Limitations and Notes

- Object Storage is designed for unstructured data (files, blobs), not structured data
- For structured data, use Replit Database (key-value) or PostgreSQL
- Large file uploads may need to be streamed
- Objects are private by default (not publicly accessible via URL without custom serving)
