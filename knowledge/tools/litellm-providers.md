# LiteLLM Providers Overview

Source: https://docs.litellm.ai/docs/providers
Documentation source: https://github.com/BerriAI/litellm-docs/tree/main/docs/providers

LiteLLM supports calling 100+ LLMs using the OpenAI input/output format.

## Supported Providers

### Major Cloud Providers
- **OpenAI** - GPT-4, GPT-3.5, o1, o3, DALL-E, Whisper, TTS (`providers/openai`)
- **Azure OpenAI** - All OpenAI models via Azure (`providers/azure/azure`)
- **Google Vertex AI** - Gemini, PaLM, Claude via Vertex (`providers/vertex`)
- **Google Gemini** - Gemini Pro, Flash, Ultra (`providers/gemini`)
- **Anthropic** - Claude 3, Claude 2, Claude Instant (`providers/anthropic`)
- **AWS Bedrock** - Claude, Titan, Llama, Mistral via Bedrock (`providers/bedrock`)
- **AWS SageMaker** - Custom and managed models (`providers/aws_sagemaker`)

### Inference Platforms
- **Groq** - Fast LLM inference (`providers/groq`)
- **Together AI** - Open source model hosting (`providers/togetherai`)
- **Fireworks AI** - Fast inference for open models (`providers/fireworks_ai`)
- **DeepInfra** - Serverless GPU inference (`providers/deepinfra`)
- **Anyscale** - Ray-based LLM serving (`providers/anyscale`)
- **Replicate** - Open source model API (`providers/replicate`)
- **Hugging Face** - Inference API and Endpoints (`providers/huggingface`)
- **NVIDIA NIM** - NVIDIA's inference microservices (`providers/nvidia_nim`)
- **Cerebras** - Fast inference chips (`providers/cerebras`)
- **Databricks** - Databricks model serving (`providers/databricks`)

### Open Source / Self-Hosted
- **Ollama** - Local LLM serving (`providers/ollama`)
- **vLLM** - High-throughput LLM serving (`providers/vllm`)
- **LM Studio** - Local model serving via OpenAI compat (`providers/lm_studio`)
- **OpenAI Compatible** - Any OpenAI-compatible endpoint (`providers/openai_compatible`)

### Other Providers
- **AI21** - Jurassic models (`providers/ai21`)
- **Aleph Alpha** - Luminous models (`providers/aleph_alpha`)
- **Cohere** - Command models (`providers/cohere`)
- **Mistral** - Mistral models (`providers/mistral`)
- **DeepSeek** - DeepSeek models (`providers/deepseek`)
- **xAI** - Grok models (`providers/xai`)
- **Black Forest Labs** - FLUX image models (`providers/black_forest_labs`)
- **Fal AI** - Generative media models (`providers/fal_ai`)
- **Baseten** - Model deployment (`providers/baseten`)
- **Cloudflare Workers AI** - Edge AI inference (`providers/cloudflare_workers`)
- **Clarifai** - AI platform (`providers/clarifai`)
- **Codestral** - Mistral's coding model (`providers/codestral`)
- **Friendli AI** - LLM serving (`providers/friendliai`)
- **GitHub Models** - Models via GitHub (`providers/github`)
- **Gradient AI** - Fine-tuning and inference (`providers/gradient_ai`)
- **GradientAI** - Enterprise AI (`providers/gradient_ai`)

## Quick Usage

```python
import litellm

# OpenAI
response = litellm.completion(model="gpt-4o", messages=[{"role": "user", "content": "Hello"}])

# Anthropic
response = litellm.completion(model="claude-3-5-sonnet-20241022", messages=[...])

# Gemini
response = litellm.completion(model="gemini/gemini-1.5-pro", messages=[...])

# Groq
response = litellm.completion(model="groq/llama3-8b-8192", messages=[...])

# Ollama
response = litellm.completion(model="ollama/llama3", messages=[...])

# Together AI
response = litellm.completion(model="together_ai/togethercomputer/llama-2-70b-chat", messages=[...])

# Vertex AI
response = litellm.completion(model="vertex_ai/gemini-1.5-pro", messages=[...])
```

## Model Naming Convention

LiteLLM uses a `provider/model` format:
- `openai/gpt-4o`
- `anthropic/claude-3-5-sonnet-20241022`
- `gemini/gemini-1.5-pro`
- `groq/llama3-70b-8192`
- `ollama/llama3`
- `together_ai/togethercomputer/llama-2-70b-chat`
- `vertex_ai/gemini-1.5-pro`
- `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0`

## Provider Environment Variables

| Provider | Environment Variable |
|----------|---------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| Google Vertex AI | `GOOGLE_APPLICATION_CREDENTIALS` or `VERTEXAI_PROJECT` + `VERTEXAI_LOCATION` |
| AWS Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION_NAME` |
| Azure OpenAI | `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| Groq | `GROQ_API_KEY` |
| Together AI | `TOGETHERAI_API_KEY` |
| Cohere | `COHERE_API_KEY` |
| Replicate | `REPLICATE_API_KEY` |
| Hugging Face | `HUGGINGFACE_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Ollama | No key required (local) |
| NVIDIA NIM | `NVIDIA_NIM_API_KEY` |
| Fireworks AI | `FIREWORKS_AI_API_KEY` |
| Cerebras | `CEREBRAS_API_KEY` |
| Databricks | `DATABRICKS_API_KEY`, `DATABRICKS_API_BASE` |
| xAI | `XAI_API_KEY` |

## Full Provider List (164 documented providers)

abliteration, ai21, aiml, aleph_alpha, amazon_nova, anthropic, anthropic_tool_search, anyscale, apertis, aws_polly, aws_sagemaker, azure/azure, azure/azure_embedding, azure/azure_responses, azure/azure_speech, azure_ai, azure_ai_agents, azure_ai_img, azure_ai_speech, azure_ai_vector_stores, azure_document_intelligence, azure_ocr, baseten, bedrock, bedrock_agents, bedrock_agentcore, bedrock_batches, bedrock_embedding, bedrock_image_gen, bedrock_imported, bedrock_mantle, bedrock_rerank, bedrock_vector_store, bedrock_writer, black_forest_labs, black_forest_labs_img_edit, bytez, cerebras, chutes, clarifai, cloudflare_workers, codestral, cohere, compactifai, custom_llm_server, dashscope, databricks, datarobot, deepgram, deepinfra, deepseek, docker_model_runner, elevenlabs, fireworks_ai, friendliai, galadriel, gemini, gmi, groq, huggingface, litellm_proxy, mistral, nvidia_nim, nvidia_riva, ollama, openai, openai_compatible, replicate, text_completion_openai, together_ai (togetherai), vertex, xai, and many more.

See individual provider pages at: https://docs.litellm.ai/docs/providers/{provider_name}
