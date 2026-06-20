# Google Gemini API: Audio

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Gemini models can process audio files for transcription, summarization, question-answering, and analysis. Audio input is supported via the File API for larger files or inline for smaller clips.

## Setup

```python
%pip install -q -U "google-genai>=1.0.0"
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
MODEL_ID = "gemini-2.5-flash"
```

## Supported Audio Formats

- MP3
- WAV
- FLAC
- AAC
- OGG (Vorbis)
- OPUS

## Upload Audio via File API

```python
import subprocess

# Download an audio file
URL = "https://storage.googleapis.com/generativeai-downloads/data/State_of_the_Union_Address_30_January_1961.mp3"
subprocess.run(["wget", "-q", URL, "-O", "sample.mp3"])

# Upload via File API
audio_file = client.files.upload(file='sample.mp3')
print(f"File uploaded: {audio_file.name}")
```

## Basic Audio Analysis

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        'Listen carefully to the following audio file. Provide a brief summary.',
        audio_file,
    ]
)

print(response.text)
```

## Audio Transcription

```python
audio_file = client.files.upload(file='interview.mp3')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        audio_file,
        'Transcribe this audio recording verbatim, including speaker identification if possible.'
    ]
)

print(response.text)
```

## Audio Q&A

```python
audio_file = client.files.upload(file='lecture.mp3')

questions = [
    "What is the main topic of this lecture?",
    "What are the three key takeaways?",
    "At what point does the speaker discuss methodology?",
]

for question in questions:
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[audio_file, question]
    )
    print(f"Q: {question}")
    print(f"A: {response.text}\n")
```

## Inline Audio (Small Files)

For smaller audio clips, embed audio data directly:

```python
%pip install -Uq pydub
from pydub import AudioSegment

# Load audio
sound = AudioSegment.from_mp3("short_clip.mp3")

# Convert to bytes for inline use
import io
buffer = io.BytesIO()
sound.export(buffer, format="mp3")
audio_bytes = buffer.getvalue()

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        types.Part.from_bytes(data=audio_bytes, mime_type='audio/mp3'),
        'What is being said in this clip?'
    ]
)
print(response.text)
```

## Multimodal Audio + Text Analysis

```python
audio_file = client.files.upload(file='meeting.mp3')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        audio_file,
        '''
        Please:
        1. Transcribe the meeting
        2. List all action items mentioned
        3. Identify the main decisions made
        4. Format as a structured meeting summary
        '''
    ]
)

print(response.text)
```

## Audio + System Instructions

```python
audio_file = client.files.upload(file='customer_call.mp3')

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[audio_file, "Analyze this customer service call"],
    config=types.GenerateContentConfig(
        system_instruction="""
        You are a customer service quality analyst. 
        Evaluate calls for: sentiment, resolution status, 
        agent effectiveness, and customer satisfaction signals.
        Output structured JSON.
        """,
        response_mime_type='application/json',
    )
)

print(response.text)
```

## Streaming Audio Analysis

```python
audio_file = client.files.upload(file='speech.mp3')

for chunk in client.models.generate_content_stream(
    model=MODEL_ID,
    contents=[audio_file, 'Transcribe this speech in real time']
):
    print(chunk.text, end='', flush=True)
```

## Token Counting for Audio

```python
audio_file = client.files.upload(file='recording.mp3')

token_count = client.models.count_tokens(
    model=MODEL_ID,
    contents=[audio_file, 'Summarize this']
).total_tokens

print(f"Token count: {token_count}")
```

Note: Audio is converted at a fixed rate of tokens per second.

## File API Limits for Audio

| Spec | Details |
|------|---------|
| Max audio duration | 80 seconds per embedding request (gemini-embedding-2) |
| Max file size | 2 GB |
| File retention | 48 hours |
| Storage | Up to 20 GB per project |

## Live Audio API (Real-Time)

For real-time audio streaming interactions, use the Live API:

```python
# See Get_started_LiveAPI.ipynb for full implementation
# The Live API supports low-latency voice/video streaming
```

## Text-to-Speech (TTS)

For generating audio output:

```python
# See Get_started_TTS.ipynb for full TTS implementation
# Gemini can generate speech output with natural-sounding voices
```

## Available Models

- `gemini-2.5-flash` — Recommended for most audio tasks
- `gemini-2.5-pro` — Most capable for complex audio analysis
- `gemini-2.5-flash-lite` — Lightweight option

**Note**: Thinking models (2.5 series) require additional processing time.
