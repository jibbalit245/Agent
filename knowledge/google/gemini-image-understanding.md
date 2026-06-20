# Google Gemini API: Image Understanding

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Gemini models support multimodal input, accepting images alongside text to enable image understanding, analysis, classification, and question-answering.

## Setup

```python
%pip install -U -q "google-genai>=1.4.0"
```

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client(api_key='YOUR_API_KEY')
MODEL_ID = "gemini-2.5-flash"
```

## Basic Image Analysis (PIL/Local)

```python
from PIL import Image

img = Image.open('image.jpg')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[img, 'Describe this image in detail']
)

print(response.text)
```

## Upload Image via File API

```python
image_file = client.files.upload(file='photo.jpg')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        image_file,
        'What objects are visible in this image?'
    ]
)

print(response.text)
```

## Image from URL (via GCS or File API)

```python
# From Google Cloud Storage
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        'What is this image about?',
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        ),
    ]
)
```

## Inline Image Bytes

```python
with open('image.png', 'rb') as f:
    image_bytes = f.read()

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        'What is this image about?',
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/png'
        ),
    ]
)
```

## Streaming with Images

```python
for chunk in client.models.generate_content_stream(
    model=MODEL_ID,
    contents=[
        'What is this image about?',
        types.Part.from_uri(
            file_uri='gs://generativeai-downloads/images/scones.jpg',
            mime_type='image/jpeg',
        ),
    ],
):
    print(chunk.text, end='')
```

## Image Classification with Enums

```python
import enum
from google.genai import types

class InstrumentClass(enum.Enum):
    PERCUSSION = "Percussion"
    STRING = "String"
    WOODWIND = "Woodwind"
    BRASS = "Brass"
    KEYBOARD = "Keyboard"

image = client.files.upload(file='instrument.jpg')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[image, 'What category of instrument is this?'],
    config=types.GenerateContentConfig(
        response_mime_type="text/x.enum",
        response_schema=InstrumentClass
    )
)

print(response.text)  # Returns: "Brass" (unquoted)
```

## Structured Image Analysis

```python
import typing_extensions as typing

class ImageAnalysis(typing.TypedDict):
    objects: list[str]
    scene_type: str
    dominant_colors: list[str]
    estimated_time_of_day: str
    mood: str

image_file = client.files.upload(file='photo.jpg')

result = client.models.generate_content(
    model=MODEL_ID,
    contents=[image_file, "Analyze this image"],
    config={
        'response_mime_type': 'application/json',
        'response_schema': ImageAnalysis,
    }
)

import json
analysis = json.loads(result.text)
print(analysis)
```

## Multiple Images in One Prompt

```python
img1 = client.files.upload(file='before.jpg')
img2 = client.files.upload(file='after.jpg')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        img1,
        'First image shows the before state.',
        img2,
        'Second image shows the after state. What changed between these two images?'
    ]
)

print(response.text)
```

## Spatial Understanding

Gemini can understand spatial relationships within images:

```python
image = client.files.upload(file='room_photo.jpg')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        image,
        'List all objects in this room and describe their spatial relationships to each other.'
    ]
)
print(response.text)
```

## PDF as Image Input

PDFs are processed page by page (each page becomes a screenshot + OCR):

```python
pdf_file = client.files.upload(file='document.pdf')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        pdf_file,
        'Extract all tables from this document and format them in markdown.'
    ]
)
print(response.text)
```

## Token Counting for Images

```python
image_file = client.files.upload(file='photo.jpg')

token_count = client.models.count_tokens(
    model=MODEL_ID,
    contents=[image_file, 'Describe this image']
).total_tokens

print(f"Total tokens (text + image): {token_count}")
```

## Supported Image Formats

- JPEG / JPG
- PNG
- GIF
- WEBP
- BMP
- TIFF
- HEIC

## Image Generation (Imagen 4)

Separate from image understanding, use Imagen for generating images:

```python
result = client.models.generate_images(
    model='imagen-4.0-generate-001',
    prompt='A photorealistic image of a golden retriever playing in autumn leaves',
    config=dict(
        number_of_images=1,
        output_mime_type='image/jpeg',
        person_generation='ALLOW_ADULT',
        aspect_ratio='16:9',
        image_size='1k',
    )
)

# Display or save the image
generated_image = result.generated_images[0].image
generated_image.show()
```

## Native Image Output (Gemini Models)

Some Gemini models can also output images:

```python
response = client.models.generate_content(
    model='gemini-3.1-flash-image',
    contents='A cartoon infographic for flying sneakers',
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="9:16"),
    ),
)

for part in response.parts:
    if part.inline_data:
        generated_image = part.as_image()
        generated_image.show()
```

## Available Models for Image Understanding

- `gemini-2.5-flash` — Fast, capable multimodal
- `gemini-2.5-pro` — Most capable, 2M context
- `gemini-2.5-flash-lite` — Lightweight option
