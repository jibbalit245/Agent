# Google Gemini API: File API & File Prompting Strategies

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

The File API enables multimodal prompting with text, image, audio, PDF, and video data. It allows you to upload files for use with the Gemini API's `generate_content` methods.

## Key Specifications

| Spec | Details |
|------|---------|
| **Storage limit** | 20 GB per project |
| **Max file size** | 2 GB per file |
| **File retention** | 48 hours |
| **Cost** | Free in all regions where Gemini API is accessible |
| **Access** | Via API key within 48-hour window |

## Setup

```python
%pip install -q -U "google-genai>=1.57.0"
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
```

## Upload a File

```python
# Upload from local path
file = client.files.upload(file='document.pdf')
print(file.name)   # files/abc123
print(file.uri)    # The file URI for use in prompts
print(file.state)  # PROCESSING, ACTIVE, or FAILED

# Upload with display name
file = client.files.upload(
    file='data.csv',
    config=types.UploadFileConfig(display_name='My Dataset')
)
```

## Wait for Video Processing

Videos may require time to process before use:

```python
import time

def upload_video(video_file_name):
    video_file = client.files.upload(file=video_file_name)
    
    while video_file.state == "PROCESSING":
        print('Waiting for video to be processed.')
        time.sleep(10)
        video_file = client.files.get(name=video_file.name)
    
    if video_file.state == "FAILED":
        raise ValueError(video_file.state)
    
    print(f'Video processing complete: {video_file.uri}')
    return video_file
```

## Use an Uploaded File in a Prompt

```python
# After uploading
file_ref = client.files.upload(file='a11.txt')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=['Could you summarize this file?', file_ref]
)
print(response.text)
```

```python
# With audio
audio_file = client.files.upload(file='speech.mp3')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        'Listen carefully to the following audio file. Provide a brief summary.',
        audio_file,
    ]
)
print(response.text)
```

## Get File Information

```python
file_info = client.files.get(name=file.name)
print(file_info.name)
print(file_info.display_name)
print(file_info.state)
print(file_info.uri)
```

## List Files

```python
for f in client.files.list():
    print(f.name, f.display_name, f.state)
```

## Delete a File

```python
client.files.delete(name=file.name)
```

## Inline Video Data

For videos under 100MB, you can use inline data:

```python
types.Part(
    file_data=types.FileData(
        file_uri='https://www.youtube.com/watch?v=VIDEO_ID'
    )
)
```

## Supported File Formats

### Images
- JPEG, PNG, GIF, WEBP, BMP, TIFF, HEIC

### Audio
- MP3, WAV, FLAC, AAC, OGG (Vorbis), OPUS

### Video
- MP4, MOV, AVI, FLV, MPG, MPEG, WEBM, WMV, 3GPP

### Documents
- PDF

### Text
- TXT, HTML, CSV, XML, JSON, and many code formats

## PDF Processing

```python
# Upload PDF via File API
file_ref = client.files.upload(file='test.pdf')

# Count tokens first
token_count = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents=[file_ref, 'Query text']
).total_tokens
print(f"Token count: {token_count}")

# Generate content
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[file_ref, 'Summarize this file as a bulleted list?']
)
print(response.text)
```

PDF processing notes:
- Each page is converted to a screenshot plus OCR-extracted text
- Supports text extraction, chart/diagram recognition, and multi-page processing

## Batch File Upload for Batch Requests

```python
uploaded_batch = client.files.upload(
    file='batch_requests.json',
    config=types.UploadFileConfig(display_name='batch-input-file')
)

batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=uploaded_batch.name,
    config={'display_name': 'my-batch-job'}
)
```

## Security Notes

- The File API uses API keys for authentication
- Uploaded files are associated with the API key's cloud project
- Files cannot be downloaded from the API after upload
- Protect your API key carefully, as it grants access to uploaded data

## Using Files with Context Caching

```python
document = client.files.upload(file="long_document.txt")

apollo_cache = client.caches.create(
    model='gemini-2.5-flash',
    config={
        'contents': [document],
        'system_instruction': 'You are an expert at analyzing documents.',
    },
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Summarize this document',
    config=types.GenerateContentConfig(
        cached_content=apollo_cache.name,
    )
)
```
