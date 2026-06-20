# OpenAI Image Generation API
> Source: https://platform.openai.com/docs/guides/image-generation
> Fetched: 2026-06-20

## Overview

OpenAI provides image generation (text-to-image), image editing, and image variation APIs. The current primary model is `gpt-image-1.5`. DALL-E 3 was retired March 4, 2026; DALL-E 2 ended support May 12, 2026.

---

## Models

### gpt-image-1.5 (Current)
- High-quality image generation
- Supports text rendering, following detailed prompts
- Better instruction following than DALL-E models

### gpt-image-1
- Predecessor to 1.5
- Still available via API

### DALL-E 3 (Retired March 4, 2026)
- No longer available for new deployments

### DALL-E 2 (Retired May 12, 2026)
- No longer available

---

## Endpoints

```
POST https://api.openai.com/v1/images/generations   # generate from text
POST https://api.openai.com/v1/images/edits         # edit an image
POST https://api.openai.com/v1/images/variations    # create variations
```

---

## Image Generation

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="gpt-image-1",
    prompt="A serene mountain lake at sunset with pine trees reflected in the water",
    n=1,
    size="1024x1024"
)

image_url = response.data[0].url
print(image_url)
```

### Generation Parameters

| Parameter | Type | Options / Notes |
|-----------|------|-----------------|
| `model` | string | `"gpt-image-1"`, `"gpt-image-1.5"` |
| `prompt` | string | Text description of desired image (max 32,000 chars) |
| `n` | int | Number of images (1–10 for DALL-E 2; 1 for gpt-image models) |
| `size` | string | See size options below |
| `quality` | string | `"low"`, `"medium"`, `"high"` (gpt-image-1+) |
| `response_format` | string | `"url"` (default) or `"b64_json"` |
| `output_format` | string | `"png"` (default) or `"jpeg"` |
| `background` | string | `"auto"` (default) or `"transparent"` |
| `output_compression` | int | 0–100 for JPEG only |
| `user` | string | End-user ID |

### Size Options (gpt-image-1)

| Size | Aspect Ratio | Notes |
|------|-------------|-------|
| `1024x1024` | 1:1 | Square (default) |
| `1024x1536` | 2:3 | Portrait |
| `1536x1024` | 3:2 | Landscape |
| `auto` | — | Model selects best size |

### Quality Options

| Quality | Description |
|---------|-------------|
| `low` | Faster, lower detail |
| `medium` | Balanced |
| `high` | Best detail, slower |

### Return Formats

```python
# URL (default) — link expires after ~1 hour
response = client.images.generate(
    model="gpt-image-1",
    prompt="A red apple",
    response_format="url"
)
url = response.data[0].url

# Base64 JSON — embedded image data
response = client.images.generate(
    model="gpt-image-1",
    prompt="A red apple",
    response_format="b64_json"
)
import base64
image_bytes = base64.b64decode(response.data[0].b64_json)
with open("apple.png", "wb") as f:
    f.write(image_bytes)
```

---

## Image Editing

Edit an existing image based on a mask and prompt.

```python
with open("original.png", "rb") as img, open("mask.png", "rb") as mask:
    response = client.images.edit(
        model="gpt-image-1",
        image=img,
        mask=mask,  # transparent areas = edit zone
        prompt="A sunflower in a vase",
        n=1,
        size="1024x1024"
    )

image_url = response.data[0].url
```

### Edit Requirements

- **Image format**: PNG, JPEG, WebP
- **Image size**: Max 25 MB
- **Mask**: PNG with transparent (alpha=0) pixels marking the edit area
- Both image and mask must be the same dimensions
- Images should be square for best results

---

## Image Variations (DALL-E 2 only)

Create variations of an existing image (not supported on gpt-image models):

```python
# Only for DALL-E 2
with open("image.png", "rb") as img:
    response = client.images.create_variation(
        model="dall-e-2",
        image=img,
        n=2,
        size="1024x1024"
    )
```

---

## Transparent Backgrounds

```python
response = client.images.generate(
    model="gpt-image-1",
    prompt="A product logo with no background",
    background="transparent",
    output_format="png",  # PNG required for transparency
    size="1024x1024"
)
```

---

## JPEG with Compression

```python
response = client.images.generate(
    model="gpt-image-1",
    prompt="A photograph of mountains",
    output_format="jpeg",
    output_compression=80,  # 0-100, higher = better quality
    size="1024x1024"
)
```

---

## Prompt Tips for Better Results

1. **Be specific**: "A 3D render of a red sports car in front of a modern building at golden hour" works better than "a red car"
2. **Specify style**: "Oil painting", "Photorealistic", "Digital art", "Watercolor", "Pixel art"
3. **Include lighting**: "Soft studio lighting", "Dramatic shadows", "Backlit"
4. **Specify camera**: "Wide angle", "Macro lens", "Portrait mode", "Aerial view"
5. **For text in images**: Be explicit: "with the text 'Hello World' in the center"

---

## Pricing (Current)

Pricing for gpt-image models is based on image resolution and quality:

| Model | Quality | Price per Image (approx) |
|-------|---------|------------------------|
| gpt-image-1 | Standard | ~$0.04/image (1024x1024) |
| gpt-image-1 | HD | ~$0.08/image |
| gpt-image-1.5 | Standard | Check current pricing |

---

## Downloading and Saving Images

```python
import requests
from pathlib import Path

def save_generated_image(prompt: str, path: str):
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        response_format="url"
    )
    
    image_url = response.data[0].url
    
    # Download from URL
    img_response = requests.get(image_url)
    img_response.raise_for_status()
    
    Path(path).write_bytes(img_response.content)
    print(f"Saved to {path}")
```

---

## Integration with Vision Models

Generate an image and then analyze it with a vision-capable model:

```python
# Generate
gen_response = client.images.generate(
    model="gpt-image-1",
    prompt="A chart showing sales growth",
    response_format="url"
)
image_url = gen_response.data[0].url

# Analyze with vision
analysis = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What does this chart show?"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    }]
)
print(analysis.choices[0].message.content)
```

---

## Sources
- [Image generation | OpenAI API](https://platform.openai.com/docs/guides/image-generation)
- [Create image | OpenAI API Reference](https://developers.openai.com/api/reference/resources/images/methods/generate)
- [OpenAI Image Generation Guide | AI Tools Navigator](https://toolnavs.com/en/article/979-openai-image-generation-guide-update-key-points-for-using-gpt-image-and-image-ap)
