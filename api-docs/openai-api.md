Notice: do not modify this file unless requested.

# OpenAI API Reference

OpenAI Official API
Base URL for SDK: https://api.openai.com/v1

## Request Body:

### 1. Text Input:
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "Hello world"
    }
  ]
}
```

### 2. With Image Input:
```json
{
  "model": "gpt-4o-mini", 
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What's in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,..."
          }
        }
      ]
    }
  ]
}
```

## Code Example:

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: "https://api.openai.com/v1"
});

async function chat() {
  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "user", 
        content: "Hello world"
      }
    ],
    stream: true
  });

  for await (const chunk of response) {
    process.stdout.write(chunk.choices[0]?.delta?.content || '');
  }
}
```

## Supported Models:
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

## Notes:
- Native OpenAI API, no compatibility layer needed
- Supports vision input with images
- Streaming and non-streaming responses
- Rate limits apply based on your OpenAI plan