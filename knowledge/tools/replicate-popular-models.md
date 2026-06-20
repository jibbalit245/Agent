# Replicate Popular Models

> Source: https://replicate.com/explore
> Note: Page returned HTTP 403 during crawl; content compiled from search results and knowledge base.

## Overview

Replicate hosts 50,000+ open-source models. The explore page features the most popular and trending models across categories.

## Most Popular Categories

### Text-to-Image Generation

| Model | Identifier | Description |
|-------|-----------|-------------|
| FLUX.1 Schnell | `black-forest-labs/flux-schnell` | Fast, high-quality image generation; 4-step distilled model |
| FLUX.1 Dev | `black-forest-labs/flux-dev` | Higher quality, 50-step FLUX model |
| FLUX.1.1 Pro | `black-forest-labs/flux-1.1-pro` | Professional tier FLUX with enhanced outputs |
| FLUX.1 Pro | `black-forest-labs/flux-pro` | Original professional FLUX model |
| Stable Diffusion XL | `stability-ai/sdxl` | Leading open-source image generator |
| Stable Diffusion 3.5 Large | `stability-ai/stable-diffusion-3.5-large` | Latest Stability AI model |
| Stable Diffusion 2.1 | `stability-ai/stable-diffusion` | Classic stable diffusion |
| SDXL Turbo | `stability-ai/sdxl-turbo` | Real-time image generation, 1-step |
| Ideogram | `ideogram-ai/ideogram-v2` | Excels at text in images |
| Recraft V3 | `recraft-ai/recraft-v3` | Design-focused generation |

### Language Models (Text Generation)

| Model | Identifier | Description |
|-------|-----------|-------------|
| Llama 3.1 405B | `meta/meta-llama-3.1-405b-instruct` | Most powerful open LLM from Meta |
| Llama 3.1 70B | `meta/meta-llama-3.1-70b-instruct` | Strong balance of power/speed |
| Llama 3.1 8B | `meta/meta-llama-3.1-8b-instruct` | Fast, efficient Llama 3.1 |
| Llama 3 70B | `meta/meta-llama-3-70b-instruct` | Llama 3 instruction-tuned |
| Llama 3 8B | `meta/meta-llama-3-8b-instruct` | Smaller Llama 3 |
| Mistral 7B | `mistralai/mistral-7b-instruct-v0.2` | Efficient 7B instruction model |
| Mixtral 8x7B | `mistralai/mixtral-8x7b-instruct-v0.1` | Mixture-of-experts model |
| CodeLlama 34B | `meta/codellama-34b-instruct` | Code-specialized Llama |

### Image-to-Image & Editing

| Model | Identifier | Description |
|-------|-----------|-------------|
| FLUX Fill | `black-forest-labs/flux-fill-pro` | Inpainting and outpainting |
| SDXL Img2Img | `stability-ai/sdxl` | Transform existing images |
| ControlNet | `jagilley/controlnet-*` | Precise control with pose/edge |
| InstantID | `philz1337x/instantid` | Identity-preserving generation |
| Face Restoration | `tencentarc/gfpgan` | Restore and enhance faces |
| Real-ESRGAN | `nightmareai/real-esrgan` | Image upscaling |
| CodeFormer | `sczhou/codeformer` | Face restoration |

### Video Generation

| Model | Identifier | Description |
|-------|-----------|-------------|
| Stable Video Diffusion | `stability-ai/stable-video-diffusion` | Image-to-video |
| Zeroscope v2 XL | `anotherjesse/zeroscope-v2-xl` | Text-to-video |
| AnimateDiff | `lucataco/animatediff-lcm` | Animate still images |
| MiniMax Video | `minimax/video-01` | High quality text-to-video |

### Audio & Speech

| Model | Identifier | Description |
|-------|-----------|-------------|
| Whisper | `openai/whisper` | State-of-the-art speech-to-text |
| Whisper Large V3 | `vaibhavs10/incredibly-fast-whisper` | Fast Whisper implementation |
| MusicGen | `meta/musicgen` | Text-to-music generation |
| Bark | `suno-ai/bark` | Text-to-speech with emotions |
| XTTS v2 | `lucataco/xtts-v2` | Multi-lingual voice cloning |
| AudioCraft | `facebookresearch/audiocraft` | Audio generation suite |

### Image Understanding (Vision)

| Model | Identifier | Description |
|-------|-----------|-------------|
| LLaVA 13B | `yorickvp/llava-13b` | Visual question answering |
| BLIP-2 | `andreasjansson/blip-2` | Image captioning and VQA |
| CLIP | `openai/clip-vit-large-patch14` | Image-text similarity |
| GPT-4V compatible | Various | Visual understanding |

### 3D & Other

| Model | Identifier | Description |
|-------|-----------|-------------|
| TripoSR | `stability-ai/triposr` | Single image to 3D |
| Zero123++ | `sudo-ai/zero123plus` | Multi-view 3D generation |
| Depth Estimation | `cjwbw/midas` | Depth from single image |
| Background Removal | `cjwbw/rembg` | Remove image backgrounds |
| Segment Anything | `sczhou/segment-anything` | Object segmentation |

## FLUX Model Family

FLUX is currently the leading open-source image generation model family (as of 2026):

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| FLUX.1 Schnell | Very fast (4 steps) | Good | Prototyping, high-volume |
| FLUX.1 Dev | Medium (50 steps) | Excellent | Production, high quality |
| FLUX.1 Pro | Medium | Best | Professional outputs |
| FLUX.1.1 Pro | Fast | Best | Latest, improved speed+quality |
| FLUX Fill Pro | Medium | Excellent | Inpainting/outpainting |
| FLUX Redux | Fast | Good | Image variation |
| FLUX Canny | Medium | Excellent | Edge-controlled generation |
| FLUX Depth | Medium | Excellent | Depth-controlled generation |

## Running Popular Models - Examples

### Generate an Image with FLUX Schnell

```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "a photo of an astronaut riding a rainbow unicorn",
        "aspect_ratio": "1:1",
        "output_format": "webp",
        "output_quality": 80,
        "num_outputs": 1,
        "go_fast": True,
        "megapixels": "1"
    }
)

with open("output.webp", "wb") as f:
    f.write(output[0].read())
```

### Generate Text with Llama 3

```python
output = replicate.run(
    "meta/meta-llama-3-70b-instruct",
    input={
        "prompt": "Tell me about quantum computing",
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "system_prompt": "You are a helpful AI assistant."
    }
)
print("".join(output))
```

### Transcribe Audio with Whisper

```python
output = replicate.run(
    "openai/whisper",
    input={
        "audio": open("audio.mp3", "rb"),
        "model": "large-v3",
        "language": "en",
        "translate": False
    }
)
print(output["transcription"])
```

### Remove Image Background

```python
output = replicate.run(
    "cjwbw/rembg",
    input={"image": open("photo.jpg", "rb")}
)
with open("no_bg.png", "wb") as f:
    f.write(output.read())
```

### Upscale an Image

```python
output = replicate.run(
    "nightmareai/real-esrgan",
    input={
        "image": open("low_res.jpg", "rb"),
        "scale": 4,
        "face_enhance": True
    }
)
with open("upscaled.png", "wb") as f:
    f.write(output.read())
```

## Finding Models

### Browse by Category

```python
import replicate

# Get text-to-image models
collection = replicate.collections.get("text-to-image")
for model in collection.models[:10]:
    print(f"{model.owner}/{model.name}: {model.run_count:,} runs")

# Search all models
for page in replicate.paginate(replicate.models.list):
    for model in page.results:
        if "flux" in model.name.lower():
            print(f"{model.owner}/{model.name}")
```

### Check Model Schema Before Running

```python
model = replicate.models.get("black-forest-labs/flux-schnell")
version = model.latest_version
schema = version.openapi_schema

# See all input parameters
input_schema = schema["components"]["schemas"]["Input"]["properties"]
for param, info in input_schema.items():
    print(f"{param}: {info.get('description', '')} (default: {info.get('default', 'N/A')})")
```
