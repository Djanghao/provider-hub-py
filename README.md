# Provider Hub

Unified Python interface for multiple AI providers: OpenAI, DeepSeek, Qwen, and Doubao. Supports text chat, image analysis, thinking mode, and async operations.

**Author**: Djanghao  

## Features

- **OpenAI**: gpt-4o-mini (text, vision)
- **DeepSeek**: deepseek-chat, deepseek-reasoner (text, reasoning)
- **Qwen**: qwen-turbo, qwen-vl-plus (text, vision)
- **Doubao**: doubao-seed models (text, vision, thinking)

## Usage

### Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Setup

```bash
export OPENAI_API_KEY="sk-..."
export DEEPSEEK_API_KEY="sk-..."
export DASHSCOPE_API_KEY="sk-..."
export ARK_API_KEY="..."
```

### Basic Setup

```python
from providers import ProviderHub
from models import Message, ChatRequest, Role

hub = ProviderHub("config.yaml")
```

### Simple Text Chat

```python
response = hub.quick_chat("qwen", "Hello world")
print(response)
```

### Async Chat

```python
import asyncio

async def main():
    messages = [
        Message.text(Role.SYSTEM, "You are a helpful assistant."),
        Message.text(Role.USER, "What is 2+2? Answer with just the number.")
    ]
    
    request = ChatRequest(
        messages=messages,
        model="gpt-4o-mini",
        max_tokens=50
    )
    
    response = await hub.achat("openai", request)
    print(response.content)

asyncio.run(main())
```

### Image Analysis

```python
import asyncio
from models import encode_image_to_base64

async def main():
    image_data = encode_image_to_base64("assets/meme.jpg")
    message = Message.with_image(
        Role.USER,
        "What do you see in this image?",
        image_data
    )
    
    request = ChatRequest(
        messages=[message],
        model="doubao-seed-1-6-vision-250815",
        max_tokens=100
    )
    
    response = await hub.achat("doubao", request)
    print(response.content)

asyncio.run(main())
```

### Multi-turn Conversation

```python
import asyncio

async def main():
    messages = [
        Message.text(Role.SYSTEM, "You are a helpful assistant."),
        Message.text(Role.USER, "What is Python?"),
        Message.text(Role.ASSISTANT, "Python is a programming language."),
        Message.text(Role.USER, "Is it popular? Just yes or no.")
    ]
    
    request = ChatRequest(
        messages=messages,
        model="qwen-turbo",
        max_tokens=50
    )
    
    response = await hub.achat("qwen", request)
    print(response.content)

asyncio.run(main())
```

### Thinking Mode (Doubao)

```python
import asyncio

async def main():
    request = ChatRequest(
        messages=[Message.text(Role.USER, "What is 15 × 23? Show your calculation.")],
        model="doubao-seed-1-6-thinking-250715",
        thinking={"type": "enabled"},
        max_tokens=300
    )
    
    response = await hub.achat("doubao", request)
    print(response.content)

asyncio.run(main())
```

### Hub Methods

```python
hub = ProviderHub("config.yaml")

# List available providers
providers = hub.list_providers()

# Quick text chat
response = hub.quick_chat("qwen", "Hello")

# Async quick chat
response = await hub.aquick_chat("qwen", "Hello")

# Full chat request
request = ChatRequest(messages=[...])
response = await hub.achat("qwen", request)
```

## Configuration

Edit `config.yaml`:

```yaml
providers:
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}
    base_url: https://api.openai.com/v1
    default_model: gpt-4o-mini
    models:
      - gpt-4o-mini

defaults:
  temperature: 0.7
  max_tokens: 500
  stream: false
  top_p: 1.0
```

## Testing

```bash
python test_connection.py
```

Tests all providers with text, image, and thinking capabilities. Generates `test_report.log` with detailed results.