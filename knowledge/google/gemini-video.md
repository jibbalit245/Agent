# Google Gemini API: Video Understanding

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Gemini models provide comprehensive video analysis capabilities, including content search, text extraction, information structuring, scene captioning, and screen recording analysis.

## Setup

```python
%pip install -U -q "google-genai>=1.16.0"
```

```python
from google import genai
from google.genai import types
import time

client = genai.Client(api_key='YOUR_API_KEY')
MODEL_ID = "gemini-2.5-flash"
```

## Upload and Process Video

```python
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

video = upload_video('my_video.mp4')
```

**Note**: Video processing typically requires several minutes due to tokenization requirements.

## Basic Video Analysis

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        video,
        'Provide a comprehensive summary of this video.'
    ]
)
print(response.text)
```

## Scene Captioning with Timestamps

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        video,
        "For each scene in this video, generate captions with timecodes."
    ]
)
print(response.text)
```

Output format includes JSON objects with:
- Time intervals
- Scene descriptions
- Spoken text in quotation marks

## Text Extraction from Video

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        video,
        "Transcribe all visible text (sticky notes, slides, whiteboards). Organize in a table."
    ]
)
print(response.text)
```

## Screen Recording Analysis

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        video,
        "Generate a 3-5 sentence summary of the user's actions with timecodes."
    ]
)
print(response.text)
```

Alternative analyses:
```python
# Key shots with emoji tags
"Identify 5 key shots with 10-word descriptions and visible objects."

# Bullet-point breakdown
"Generate bullet points with timestamps as JSON objects."

# User interaction mapping
"Map all user interface interactions by timestamp."
```

## YouTube Video Analysis

```python
yt_link = "https://www.youtube.com/watch?v=VIDEO_ID"

response = client.models.generate_content(
    model=MODEL_ID,
    contents=types.Content(
        parts=[
            types.Part(text="Find all instances where 'AI' is mentioned with timestamps."),
            types.Part(file_data=types.FileData(file_uri=yt_link)),
        ]
    )
)
print(response.text)
```

## Video Segment Analysis (Time Offsets)

Analyze specific portions of a video:

```python
video = upload_video('long_video.mp4')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(
                    file_uri=video.uri,
                    mimeType=video.mime_type
                ),
                video_metadata=types.VideoMetadata(
                    start_offset='60s',    # Start at 1 minute
                    end_offset='120s'      # End at 2 minutes
                )
            ),
            types.Part(text="Describe what happens in this segment.")
        ]
    )
)
```

**Parameter Details:**
- `start_offset`: Beginning timestamp in seconds format (e.g., `'60s'`, `'1250s'`)
- `end_offset`: Ending timestamp in seconds format

## Frame Rate Customization

Control analysis detail level:

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        types.Part(
            file_data=types.FileData(file_uri=video.uri, mimeType=video.mime_type),
            video_metadata=types.VideoMetadata(
                start_offset='15s',
                end_offset='35s',
                fps=24  # High FPS for fast action
            )
        ),
        types.Part(text="Analyze every detail of this sequence.")
    ]
)
```

**FPS Guidelines:**
| FPS | Best For |
|-----|---------|
| 1 (default) | Lectures, interviews, static content |
| 2-4 | General video, moderate action |
| 8-24 | Sports, fast action, pit stops, rapid sequences |

## System Instructions with Video

```python
config = types.GenerateContentConfig(
    system_instruction="You are a sports analyst. Focus on player movements and tactics."
)

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[video, "Analyze this game footage"],
    config=config
)
```

## Structured Video Output

```python
import typing_extensions as typing

class VideoScene(typing.TypedDict):
    start_time: str
    end_time: str
    description: str
    key_objects: list[str]
    spoken_words: str

result = client.models.generate_content(
    model=MODEL_ID,
    contents=[video, "Extract all scenes"],
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[VideoScene],
    }
)

import json
scenes = json.loads(result.text)
```

## Sample Prompts

| Task | Prompt |
|------|--------|
| Scene captioning | "Generate captions for each scene with timecodes and spoken text." |
| Data extraction | "Transcribe and organize all visible text into a structured table." |
| Summary | "Summarize in 3-5 sentences with corresponding timecodes." |
| Key moments | "Identify 5 key shots with 10-word descriptions and visible objects." |
| Search | "Find all instances where [topic] is mentioned." |
| Bullet points | "Generate bullet points with timestamps as JSON objects." |

## Supported Video Formats

- MP4
- MOV
- AVI
- FLV
- MPG / MPEG
- WEBM
- WMV
- 3GPP

**Inline size limit**: 100MB maximum for inline video data

## Video Generation (Veo)

For generating videos (not analysis), use Veo:

```python
from google.genai import types
import time

# Text to video
operation = client.models.generate_videos(
    model='veo-3.1-generate-preview',
    prompt='A neon hologram of a cat driving at top speed',
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0].video
video.show()
```

### Image to Video

```python
image = types.Image.from_file(location="local/path/file.png")

operation = client.models.generate_videos(
    model='veo-3.1-generate-preview',
    prompt='Night sky transition',
    image=image,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)
```

### Video to Video (Extension)

```python
operation = client.models.generate_videos(
    model='veo-3.1-generate-preview',
    prompt='Continue the scene',
    video=types.Video(uri="gs://bucket-name/inputs/videos/cat_driving.mp4"),
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=5,
        enhance_prompt=True,
    ),
)
```

## Video Generation Models

| Model | Description |
|-------|-------------|
| `veo-3.0-generate-001` | Standard Veo 3 |
| `veo-3.0-fast-generate-001` | Fast Veo 3 |
| `veo-3.1-generate-preview` | Latest preview |

## Related Resources

- AI Studio live demo: https://aistudio.google.com/starter-apps/video
- Video analysis cookbook: `quickstarts/Video_understanding.ipynb`
- Veo generation cookbook: `quickstarts/Get_started_Veo.ipynb`
