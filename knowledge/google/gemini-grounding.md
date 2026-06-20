# Google Gemini API: Grounding

> Source: Fetched from GitHub google-gemini/cookbook (ai.google.dev returned HTTP 403)
> Date: 2026-06-20

## Overview

Information grounding connects language models to verifiable information sources to enhance accuracy, relevance, and factual correctness of responses. The Gemini API supports five grounding methods.

## Setup

```python
%pip install -q -U "google-genai>=1.43.0"  # 1.43+ required for Maps grounding
```

```python
from google import genai
from google.genai import types

client = genai.Client(api_key='YOUR_API_KEY')
MODEL_ID = "gemini-2.5-flash"
```

## Grounding Methods Summary

| Grounding Type | Primary Use Case | Key Advantage |
|---|---|---|
| **Google Search** | Current events, recent data | Nearly real-time, comprehensive |
| **Google Maps** | Local businesses, geographic queries | Accurate location data, reviews |
| **YouTube** | Video summarization, content analysis | Direct video understanding |
| **URL Context** | Specific documents, publications | Precise source material |
| **Combined** | Complex multi-source queries | Comprehensive coverage |

---

## 1. Google Search Grounding

Enables access to nearly real-time information for queries requiring current knowledge.

```python
config = {
    "tools": [
        {"google_search": {}}
    ]
}

response = client.models.generate_content(
    model=MODEL_ID,
    contents="What was the latest IPL match and who won?",
    config=config,
)

print(response.text)
```

### Accessing Search Metadata

```python
grounding = response.candidates[0].grounding_metadata

# Search queries used
print(grounding.web_search_queries)

# Sources used
for chunk in grounding.grounding_chunks:
    print(chunk.web.uri)
    print(chunk.web.title)

# Interactive search widget HTML
print(grounding.search_entry_point.rendered_content)
```

### Chat with Search Grounding

```python
search_tool = {'google_search': {}}

chat = client.chats.create(
    model=MODEL_ID,
    config={'tools': [search_tool]}
)

response = chat.send_message('What are the latest news in AI?')
print(response.text)

# Follow-up
response = chat.send_message('Tell me more about the most interesting one')
print(response.text)
```

---

## 2. Google Maps Grounding

Incorporates location-aware functionality and real-world geographic data.

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents="What are the best restaurants near Central Park?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())],
        tool_config=types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(
                    latitude=40.7680797,
                    longitude=-73.9818957
                )
            )
        ),
    )
)

print(response.text)
```

### Source Attribution for Maps

```python
def generate_sources(response):
    grounding = response.candidates[0].grounding_metadata
    supported_chunk_indices = {
        i for support in grounding.grounding_supports
        for i in support.grounding_chunk_indices
    }
    sources = []
    for i in supported_chunk_indices:
        ref = grounding.grounding_chunks[i].maps
        sources.append(f"- [{ref.title}]({ref.uri})")
    return "\n".join(sources)

print(generate_sources(response))
```

### Maps Interactive Widget

Requires a Google Maps API key with Places API and Maps JavaScript API enabled:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY&loading=async&v=alpha&libraries=places" async></script>
<gmp-place-contextual context-token="TOKEN_VALUE"></gmp-place-contextual>
```

Enable with `types.GoogleMaps(enable_widget=True)`.

---

## 3. YouTube Content Grounding

Process video content directly via public YouTube URLs.

```python
yt_link = "https://www.youtube.com/watch?v=VIDEO_ID"

response = client.models.generate_content(
    model=MODEL_ID,
    contents=types.Content(
        parts=[
            types.Part(text="Summarize this video."),
            types.Part(file_data=types.FileData(file_uri=yt_link)),
        ]
    ),
)

print(response.text)
```

### Custom Frame Rate for Video Analysis

```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        types.Part(text="Describe action with high detail."),
        types.Part(
            file_data=types.FileData(file_uri=yt_link),
            video_metadata=types.VideoMetadata(fps=2)  # Default: 1 FPS
        ),
    ]
)
```

**FPS Guidance:**
- **Default (1 FPS)**: Good for static content (lectures, security footage)
- **Higher FPS (2-24)**: Better for rapid motion, fine-grained temporal analysis

---

## 4. URL Context Grounding

Direct access to content from specified web pages, PDFs, and images via URL.

```python
config = {
    "tools": [{
        "url_context": {}
    }],
}

response = client.models.generate_content(
    contents=["Based on https://example.com/report, what are the key findings?"],
    model=MODEL_ID,
    config=config
)

print(response.text)
```

**Limitations:**
- Maximum 20 links per prompt

### Check Retrieval Status

```python
url_meta = response.candidates[0].url_context_metadata

for entry in url_meta.url_metadata:
    print(entry.retrieved_url)
    print(entry.url_retrieval_status)
    # URL_RETRIEVAL_STATUS_SUCCESS or failure reason
```

**Supported content types**: Website pages, PDF documents, Images

---

## 5. Combined Grounding Methods

Multiple grounding tools can be used simultaneously:

```python
config = {
    "tools": [
        {"url_context": {}},
        {"google_search": {}}
    ],
}

response = client.models.generate_content(
    contents=["Based on https://specific-report.com and recent news, analyze..."],
    model=MODEL_ID,
    config=config
)
```

---

## Grounding Metadata Structure

All grounded responses include metadata:

```python
grounding = response.candidates[0].grounding_metadata

# Search queries performed
grounding.web_search_queries

# Web sources
grounding.grounding_chunks  # List of source chunks with URIs

# Content-to-source mapping
grounding.grounding_supports  # Links content segments to source chunks

# Interactive widget
grounding.search_entry_point.rendered_content
```

---

## Best Practices

1. Select the appropriate grounding method based on query requirements
2. Enable widgets only when displaying them to users (adds latency otherwise)
3. Always check URL retrieval status for URL context requests
4. Use combined approaches for queries requiring multiple information types
5. Adjust video FPS based on content characteristics and token budget
6. Always attribute sources in final output when required by usage policies
