# Claude API — TypeScript SDK Guide
> Source: https://platform.claude.com/docs/en/api/sdks/typescript.md
> Fetched: 2026-06-20
---

## Installation

```bash
npm install @anthropic-ai/sdk
# or
yarn add @anthropic-ai/sdk
# or
pnpm add @anthropic-ai/sdk
```

## Client Initialization

```typescript
import Anthropic from "@anthropic-ai/sdk";

// Default — reads ANTHROPIC_API_KEY from environment
const client = new Anthropic();

// Explicit API key
const client = new Anthropic({ apiKey: "sk-ant-..." });

// Async client (same class, all methods are async)
const client = new Anthropic();
```

## Basic Message Request

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  messages: [{ role: "user", content: "What is the capital of France?" }],
});

for (const block of message.content) {
  if (block.type === "text") {
    console.log(block.text);
  }
}
```

## System Prompts

```typescript
const message = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  system: "You are a helpful coding assistant. Always provide examples.",
  messages: [{ role: "user", content: "How do I read a JSON file in Node.js?" }],
});
```

## Streaming

```typescript
const stream = await client.messages.stream({
  model: "claude-opus-4-8",
  max_tokens: 64000,
  messages: [{ role: "user", content: "Write a story about space." }],
});

for await (const text of stream.text_stream) {
  process.stdout.write(text);
}

const finalMessage = await stream.finalMessage();
console.log("\nTokens used:", finalMessage.usage.input_tokens + finalMessage.usage.output_tokens);
```

## Extended Thinking / Adaptive Thinking

```typescript
const message = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  thinking: { type: "adaptive", display: "summarized" },
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Solve this problem step by step..." }],
});

for (const block of message.content) {
  if (block.type === "thinking") {
    console.log("Thinking:", block.thinking);
  } else if (block.type === "text") {
    console.log("Response:", block.text);
  }
}
```

## Vision (Images)

```typescript
import * as fs from "fs";

// Base64 image
const imageData = fs.readFileSync("image.png").toString("base64");

const message = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      {
        type: "image",
        source: {
          type: "base64",
          media_type: "image/png",
          data: imageData,
        },
      },
      { type: "text", text: "What's in this image?" },
    ],
  }],
});

// URL image
const message2 = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      {
        type: "image",
        source: { type: "url", url: "https://example.com/image.png" },
      },
      { type: "text", text: "Describe this image." },
    ],
  }],
});
```

## Tool Use

```typescript
const tools: Anthropic.Tool[] = [{
  name: "get_weather",
  description: "Get the current weather for a location",
  input_schema: {
    type: "object",
    properties: {
      location: { type: "string", description: "City name" },
    },
    required: ["location"],
  },
}];

const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  tools,
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});

if (response.stop_reason === "tool_use") {
  const toolUseBlock = response.content.find(b => b.type === "tool_use");
  if (toolUseBlock && toolUseBlock.type === "tool_use") {
    console.log("Tool:", toolUseBlock.name);
    console.log("Input:", toolUseBlock.input);
    
    // Execute tool and continue conversation
    const result = await getWeather(toolUseBlock.input as { location: string });
    
    const finalResponse = await client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 4096,
      tools,
      messages: [
        { role: "user", content: "What's the weather in Paris?" },
        { role: "assistant", content: response.content },
        {
          role: "user",
          content: [{
            type: "tool_result",
            tool_use_id: toolUseBlock.id,
            content: result,
          }],
        },
      ],
    });
    
    console.log(finalResponse.content[0]);
  }
}
```

## Tool Runner (Beta)

```typescript
import Anthropic, { betaZodTool } from "@anthropic-ai/sdk";
import { z } from "zod";

const client = new Anthropic();

const getWeather = betaZodTool({
  name: "get_weather",
  description: "Get current weather for a location",
  schema: z.object({
    location: z.string().describe("City name, e.g., San Francisco, CA"),
    unit: z.enum(["celsius", "fahrenheit"]).optional(),
  }),
  execute: async ({ location, unit }) => {
    // In production, call real weather API
    return `72°F and sunny in ${location}`;
  },
});

const runner = client.beta.messages.tool_runner({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  tools: [getWeather],
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});

for await (const message of runner) {
  for (const block of message.content) {
    if (block.type === "text") {
      console.log(block.text);
    }
  }
}
```

## Structured Outputs

```typescript
import { z } from "zod";

const ContactSchema = z.object({
  name: z.string(),
  email: z.string(),
  plan: z.string(),
  interests: z.array(z.string()),
});

const response = await client.messages.parse({
  model: "claude-opus-4-8",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Extract: Jane Doe (jane@example.com), Pro plan, interested in AI and ML" }],
  output_format: ContactSchema,
});

const contact = response.parsed_output; // typed as z.infer<typeof ContactSchema>
console.log(contact.name);
console.log(contact.email);
```

## Prompt Caching

```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 1024,
  cache_control: { type: "ephemeral" },
  system: largeDocumentText,  // document to cache
  messages: [{ role: "user", content: "Summarize the key points" }],
});

console.log("Cache writes:", response.usage.cache_creation_input_tokens);
console.log("Cache hits:", response.usage.cache_read_input_tokens);
```

## Error Handling

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

try {
  const response = await client.messages.create({
    model: "claude-opus-4-8",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello" }],
  });
} catch (error) {
  if (error instanceof Anthropic.BadRequestError) {
    console.error("Bad request:", error.message);
  } else if (error instanceof Anthropic.AuthenticationError) {
    console.error("Invalid API key");
  } else if (error instanceof Anthropic.RateLimitError) {
    const retryAfter = error.response.headers.get("retry-after");
    console.error(`Rate limited. Retry after ${retryAfter}s`);
  } else if (error instanceof Anthropic.APIStatusError) {
    console.error(`API error ${error.status}:`, error.message);
  } else {
    throw error;
  }
}
```

## Stop Reasons

```typescript
const response = await client.messages.create({ ... });

switch (response.stop_reason) {
  case "end_turn":
    // Natural completion
    break;
  case "max_tokens":
    // Hit token limit
    break;
  case "tool_use":
    // Model wants to use a tool
    break;
  case "pause_turn":
    // Server-side tool loop paused
    break;
  case "refusal":
    if (response.stop_details) {
      console.log("Category:", response.stop_details.category);
      console.log("Explanation:", response.stop_details.explanation);
    }
    break;
}
```

## Multi-Turn Conversations

```typescript
class ConversationManager {
  private messages: Anthropic.MessageParam[] = [];
  
  constructor(
    private client: Anthropic,
    private model: string = "claude-opus-4-8",
    private system?: string,
  ) {}
  
  async send(userMessage: string): Promise<string> {
    this.messages.push({ role: "user", content: userMessage });
    
    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 16000,
      system: this.system,
      messages: this.messages,
    });
    
    const text = response.content
      .filter(b => b.type === "text")
      .map(b => b.text)
      .join("");
    
    this.messages.push({ role: "assistant", content: response.content });
    return text;
  }
}

const convo = new ConversationManager(client, "claude-opus-4-8", "You are a helpful assistant.");
console.log(await convo.send("Hello!"));
console.log(await convo.send("What can you help me with?"));
```

## Token Counting

```typescript
const tokenResponse = await client.messages.countTokens({
  model: "claude-opus-4-8",
  messages: [{ role: "user", content: "Hello, world!" }],
});
console.log("Input tokens:", tokenResponse.input_tokens);
```

## Message Batches

```typescript
const batch = await client.messages.batches.create({
  requests: prompts.map((prompt, i) => ({
    custom_id: `req-${i}`,
    params: {
      model: "claude-opus-4-8",
      max_tokens: 1024,
      messages: [{ role: "user", content: prompt }],
    },
  })),
});

// Poll for completion
let status = await client.messages.batches.retrieve(batch.id);
while (status.processing_status !== "ended") {
  await new Promise(r => setTimeout(r, 60000));
  status = await client.messages.batches.retrieve(batch.id);
}

for await (const result of await client.messages.batches.results(batch.id)) {
  if (result.result.type === "succeeded") {
    const text = result.result.message.content
      .filter(b => b.type === "text")
      .map(b => b.text)
      .join("");
    console.log(`[${result.custom_id}]:`, text.slice(0, 100));
  }
}
```

## Configuration

```typescript
// Per-request timeout
const response = await client.messages.create(
  { model: "claude-opus-4-8", max_tokens: 1024, messages: [...] },
  { timeout: 30000 }
);

// Global timeout and retries
const client = new Anthropic({
  timeout: 60000,
  maxRetries: 5,
});

// Raw response with headers
const raw = await client.messages.withResponse().create({
  model: "claude-opus-4-8",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});
console.log(raw.response.headers.get("request-id"));
const message = raw.data;
```
