# OpenAI Audio API — Speech-to-Text, Text-to-Speech, Realtime
> Source: https://platform.openai.com/docs/guides/audio
> Fetched: 2026-06-20

## Overview

OpenAI's audio API covers:
1. **Speech-to-Text (STT)** — Transcribe or translate audio to text
2. **Text-to-Speech (TTS)** — Generate natural-sounding speech from text
3. **Realtime API** — Low-latency bidirectional audio conversations

---

## Speech-to-Text (Transcription)

### Endpoint

```
POST https://api.openai.com/v1/audio/transcriptions
POST https://api.openai.com/v1/audio/translations  # translate to English
```

### Models

| Model | Notes |
|-------|-------|
| `whisper-1` | Original Whisper, $0.006/min, 96 languages |
| `gpt-4o-transcribe` | GPT-4o-based, higher accuracy than Whisper |
| `gpt-4o-mini-transcribe` | GPT-4o-mini-based, strong accuracy/reliability |
| `gpt-realtime-whisper` | Streaming STT, $0.017/min, low-latency |

### Basic Transcription

```python
from openai import OpenAI

client = OpenAI()

with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        language="en"  # optional, auto-detected if omitted
    )

print(transcript.text)
```

### Transcription Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model ID (`whisper-1`, `gpt-4o-transcribe`, etc.) |
| `file` | file | Audio file (see supported formats) |
| `language` | string | BCP-47 language code (optional; auto-detected) |
| `prompt` | string | Prior context to guide transcription (max 224 tokens) |
| `response_format` | string | `"json"`, `"text"`, `"srt"`, `"verbose_json"`, `"vtt"` |
| `temperature` | float | 0–1 (0 = more deterministic) |
| `timestamp_granularities` | array | `["word"]`, `["segment"]`, or both |

### Supported Audio Formats

| Format | Notes |
|--------|-------|
| MP3 | Most common |
| MP4 | Video container with audio |
| M4A | Apple audio |
| WAV | Uncompressed |
| FLAC | Lossless |
| OGG | Open format |
| WEBM | Web audio |
| MPEG | Legacy |

**Max file size**: 25 MB per request

### Get Timestamps

```python
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("audio.mp3", "rb"),
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"]
)

# Word-level timestamps
for word in transcript.words:
    print(f"{word.word}: {word.start:.2f}s - {word.end:.2f}s")

# Segment-level
for seg in transcript.segments:
    print(f"[{seg.start:.2f}-{seg.end:.2f}] {seg.text}")
```

### Subtitles (SRT / VTT)

```python
# Get SRT subtitle format
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("video.mp4", "rb"),
    response_format="srt"
)

with open("subtitles.srt", "w") as f:
    f.write(transcript)
```

### Translation (to English)

```python
# Translate non-English audio to English text
translation = client.audio.translations.create(
    model="whisper-1",
    file=open("french_audio.mp3", "rb")
)
print(translation.text)  # English translation
```

### Large File Handling

For files > 25 MB, chunk the audio:

```python
from pydub import AudioSegment

def transcribe_large_file(file_path: str) -> str:
    audio = AudioSegment.from_file(file_path)
    chunk_duration_ms = 10 * 60 * 1000  # 10 minutes
    
    transcripts = []
    for i, start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
        chunk = audio[start_ms:start_ms + chunk_duration_ms]
        chunk_path = f"/tmp/chunk_{i}.mp3"
        chunk.export(chunk_path, format="mp3")
        
        with open(chunk_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        transcripts.append(result.text)
    
    return " ".join(transcripts)
```

---

## Text-to-Speech (TTS)

### Endpoint

```
POST https://api.openai.com/v1/audio/speech
```

### Models

| Model | Notes |
|-------|-------|
| `tts-1` | Optimized for real-time, $15/1M chars |
| `tts-1-hd` | Higher quality, $30/1M chars |
| `gpt-4o-mini-tts` | Instruction-following TTS, latest model |

### Available Voices

| Voice | Description |
|-------|-------------|
| `alloy` | Neutral, balanced |
| `ash` | Clear, expressive |
| `coral` | Warm, friendly |
| `echo` | Male, deep |
| `fable` | British-inflected, expressive |
| `nova` | Female, professional |
| `onyx` | Deep, authoritative |
| `sage` | Calm, wise |
| `shimmer` | Gentle, warm |
| `verse` | Versatile |
| `ballad` (and others) | Various styles |

**Note**: `gpt-4o-mini-tts` supports all 11 built-in voices and custom voice instructions.

### Basic TTS

```python
from pathlib import Path

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello! This is a test of the OpenAI text-to-speech API."
)

# Save to file
with open("speech.mp3", "wb") as f:
    f.write(response.content)

# Or stream to file
response.stream_to_file("speech.mp3")
```

### TTS Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | `"tts-1"`, `"tts-1-hd"`, or `"gpt-4o-mini-tts"` |
| `input` | string | Text to convert (max 4096 characters) |
| `voice` | string | Voice ID (see above) |
| `response_format` | string | `"mp3"` (default), `"opus"`, `"aac"`, `"flac"`, `"wav"`, `"pcm"` |
| `speed` | float | Speed multiplier 0.25–4.0 (default 1.0) |
| `instructions` | string | Voice customization (gpt-4o-mini-tts only) |

### Custom Voice Instructions (gpt-4o-mini-tts)

```python
response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="Your package has been delivered. Have a great day!",
    instructions="Speak like a friendly, upbeat customer service agent. Use a warm, reassuring tone."
)
response.stream_to_file("delivery_notification.mp3")
```

### Streaming TTS

```python
import io
import sounddevice as sd
import soundfile as sf

# Stream audio directly without saving to file
with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="nova",
    input="This text will be streamed as audio..."
) as response:
    audio_data = io.BytesIO(response.read())

# Play audio (requires sounddevice + soundfile)
data, samplerate = sf.read(audio_data)
sd.play(data, samplerate)
sd.wait()
```

### Output Formats for TTS

| Format | Use Case |
|--------|---------|
| `mp3` | General purpose, good compression |
| `opus` | Low-latency streaming, voice calls |
| `aac` | Apple devices, good quality |
| `flac` | Lossless, larger files |
| `wav` | Uncompressed, no codec needed |
| `pcm` | Raw 16-bit PCM at 24kHz, for pipelines |

---

## Realtime API

For low-latency bidirectional voice conversations (think voice assistants).

### Overview

- Connects via **WebSocket** or **WebRTC**
- Bidirectional: send audio → receive audio + text in real time
- Supports voice activity detection (VAD)
- Supports multiple modalities: audio + text simultaneously
- Max session duration: 60 minutes

### Connection

```javascript
// WebSocket connection
const ws = new WebSocket(
    "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
    {
        headers: {
            "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
            "OpenAI-Beta": "realtime=v1"
        }
    }
);
```

### Python WebSocket Example

```python
import websocket
import json
import base64

ws = websocket.WebSocket()
ws.connect(
    "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
    header=[
        f"Authorization: Bearer {os.environ['OPENAI_API_KEY']}",
        "OpenAI-Beta: realtime=v1"
    ]
)

# Configure session
ws.send(json.dumps({
    "type": "session.update",
    "session": {
        "modalities": ["text", "audio"],
        "voice": "alloy",
        "instructions": "You are a helpful voice assistant.",
        "turn_detection": {
            "type": "server_vad",        # server-side voice detection
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 500
        },
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16"
    }
}))

# Send audio (base64-encoded PCM)
with open("audio_chunk.raw", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

ws.send(json.dumps({
    "type": "input_audio_buffer.append",
    "audio": audio_data
}))

# Commit audio buffer (trigger response generation)
ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
```

### Session Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `modalities` | array | `["text"]`, `["audio"]`, or `["text", "audio"]` |
| `model` | string | Model ID for the session |
| `voice` | string | Voice for audio output (can't change after first audio response) |
| `instructions` | string | System-level instructions |
| `input_audio_format` | string | `"pcm16"`, `"g711_ulaw"`, `"g711_alaw"` |
| `output_audio_format` | string | `"pcm16"`, `"g711_ulaw"`, `"g711_alaw"` |
| `turn_detection` | object | VAD configuration (see below) |
| `tools` | array | Function tools available to the model |
| `tool_choice` | string | Tool selection strategy |
| `temperature` | float | 0.6–1.2 (default 0.8) |
| `max_response_output_tokens` | int | Max output tokens per response |

### Turn Detection (VAD)

```json
{
  "type": "server_vad",
  "threshold": 0.5,
  "prefix_padding_ms": 300,
  "silence_duration_ms": 500
}
```

Or semantic VAD:
```json
{
  "type": "semantic_vad",
  "eagerness": "low"  // "low", "medium", "high", "auto"
}
```

Disable VAD entirely (manual turn control):
```json
{"type": "none"}
```

### Client Events (what you send)

| Event | Description |
|-------|-------------|
| `session.update` | Update session configuration |
| `input_audio_buffer.append` | Send audio chunk |
| `input_audio_buffer.commit` | Finalize audio input |
| `input_audio_buffer.clear` | Clear buffered audio |
| `conversation.item.create` | Add a message to conversation |
| `response.create` | Trigger a response |
| `response.cancel` | Cancel current response |

### Server Events (what you receive)

| Event | Description |
|-------|-------------|
| `session.created` | Session initialized |
| `session.updated` | Session config updated |
| `conversation.created` | New conversation started |
| `input_audio_buffer.committed` | Audio buffer finalized |
| `input_audio_buffer.speech_started` | VAD detected speech |
| `input_audio_buffer.speech_stopped` | VAD detected silence |
| `response.created` | Response generation started |
| `response.output_item.added` | New output item |
| `response.audio.delta` | Audio chunk received |
| `response.audio.done` | Audio output complete |
| `response.text.delta` | Text chunk received |
| `response.text.done` | Text output complete |
| `response.done` | Response fully complete |
| `error` | Error occurred |

---

## New Realtime Voice Models (2026)

### gpt-realtime-2
- **Use case**: Voice agents requiring GPT-5-class reasoning
- **Features**: Complex multi-turn conversations, tool use
- **Pricing**: Higher than standard realtime

### gpt-realtime-whisper
- **Use case**: Streaming speech-to-text only (not conversational)
- **Pricing**: $0.017/minute
- Supports `audio.input.transcription.delay` options: `minimal`, `low`, `medium`, `high`, `xhigh`

### gpt-realtime-translate
- **Use case**: Live speech-to-speech translation
- **Features**: 70+ input languages → 13 output languages
- **Mode**: Real-time, keeps pace with speaker

---

## Audio Pricing

| Service | Model | Price |
|---------|-------|-------|
| Transcription | whisper-1 | $0.006/minute |
| Transcription | gpt-realtime-whisper | $0.017/minute |
| TTS | tts-1 | $15.00/1M characters |
| TTS | tts-1-hd | $30.00/1M characters |
| TTS | gpt-4o-mini-tts | Competitive |
| Realtime | gpt-4o-realtime-preview | Per audio token |

---

## Sources
- [Speech to text | OpenAI API](https://developers.openai.com/api/docs/guides/speech-to-text)
- [Text to speech | OpenAI API](https://developers.openai.com/api/docs/guides/text-to-speech)
- [Realtime API with WebSocket | OpenAI API](https://developers.openai.com/api/docs/guides/realtime-websocket)
- [Realtime conversations | OpenAI API](https://developers.openai.com/api/docs/guides/realtime-conversations)
- [Advancing voice intelligence | OpenAI](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)
