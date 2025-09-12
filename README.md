# Provider Hub

Unified LLM provider interface for multi-agent systems.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Supported Models](#supported-models)
- [Testing](#testing)

## Installation

```bash
pip install provider_hub
```

## Quick Start

### 1. Environment Setup

Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key  
DASHSCOPE_API_KEY=your-qwen-api-key
ARK_API_KEY=your-doubao-api-key
```

### 2. Basic Usage

```python
from provider_hub import LLM

# Simple text chat
llm = LLM(
    model="doubao-seed-1-6-250615", 
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    timeout=30
)
response = llm.chat("Hello, how are you?")
print(response.content)
```

## Core Features

### 📝 Text Processing

All models support standard text chat functionality with configurable parameters.

```python
from provider_hub import LLM

llm = LLM(
    model="qwen-plus",
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    timeout=30
)
response = llm.chat("Explain quantum computing")
print(response.content)
```

### 🖼️ Vision Processing

Process both local images and URLs with vision-capable models.

```python
from provider_hub import LLM, ChatMessage, prepare_image_content

# Vision model setup
vision_llm = LLM(
    model="qwen-vl-plus",
    temperature=0.5,
    max_tokens=150,
    timeout=60
)

# Process local image
image_content = prepare_image_content("path/to/your/image.jpg")

# Or process image URL
# image_content = prepare_image_content("https://example.com/image.jpg")

messages = [ChatMessage(
    role="user",
    content=[
        {"type": "text", "text": "What do you see in this image?"},
        image_content
    ]
)]
response = vision_llm.chat(messages)
print(response.content)
```

### 🧠 Reasoning Mode

Enable step-by-step reasoning for complex problem solving.

```python
from provider_hub import LLM

# DeepSeek reasoning
deepseek_reasoning = LLM(
    model="deepseek-reasoner", 
    thinking=True,
    temperature=0.3,
    max_tokens=200,
    timeout=60
)

# Qwen reasoning  
qwen_reasoning = LLM(
    model="qwen3-max-preview",
    thinking=True,
    temperature=0.5,
    max_tokens=180,
    timeout=50
)

# Doubao reasoning
doubao_reasoning = LLM(
    model="doubao-seed-1-6-250615",
    thinking={"type": "enabled"},
    temperature=0.4,
    max_tokens=200,
    timeout=45
)

response = qwen_reasoning.chat("Calculate 15 * 23 step by step")
print(response.content)
```

### ⚡ OpenAI GPT-5 Reasoning Effort

GPT-5 models support adjustable reasoning intensity through the chat method.

```python
from provider_hub import LLM

gpt5_reasoning = LLM(
    model="gpt-5",
    max_tokens=200,
    timeout=40
)

response = gpt5_reasoning.chat(
    "Solve this complex problem step by step",
    reasoning_effort="high"  # Options: "low", "medium", "high"
)
print(response.content)
```

## API Reference

### Parameters

| Parameter | Type | Description | Range/Options |
|-----------|------|-------------|---------------|
| `model` | string | Model identifier | See [Supported Models](#supported-models) |
| `temperature` | float | Controls randomness | 0.0-2.0 (0=deterministic, 2=very creative) |
| `top_p` | float | Nucleus sampling threshold | 0.0-1.0 |
| `max_tokens` | int | Maximum response length | Positive integer |
| `timeout` | int | Request timeout | Seconds (default: 30) |
| `thinking` | bool/dict | Enable reasoning mode | Provider-specific format |
| `reasoning_effort` | string | GPT-5 reasoning intensity | "low", "medium", "high" |

### Parameter Support by Provider

| Parameter | OpenAI | DeepSeek | Qwen | Doubao | Notes |
|-----------|--------|----------|------|---------|-------|
| `temperature` | ✅ | ✅ | ✅ | ✅ | GPT-5 series limited to 1.0 |
| `top_p` | ✅ | ✅ | ✅ | ✅ | Full support |
| `max_tokens` | ✅ | ✅ | ✅ | ✅ | GPT-5 auto-converts to max_completion_tokens |
| `timeout` | ✅ | ✅ | ✅ | ✅ | Full support |
| `thinking` | ❌ | ✅ | ✅ | ✅ | Model-specific availability |
| `reasoning_effort` | ✅ | ❌ | ❌ | ❌ | GPT-5 series only |

### Provider-Specific Notes

#### OpenAI
- **GPT-5 series**: Only support `temperature=1.0`, use `reasoning_effort` instead of `thinking`
- **GPT-4.1**: Full parameter support
- **Reasoning**: Use `reasoning_effort="high"` for complex problems

#### DeepSeek
- **Thinking support**: Only `deepseek-reasoner` model
- **Format**: `thinking=True`
- **Best for**: Mathematical and logical reasoning

#### Qwen
- **Thinking support**: Only `qwen3-*` models (qwen3-max-preview, qwen3-coder-plus, qwen3-coder-flash)
- **Format**: `thinking=True`
- **Vision models**: qwen-vl-max, qwen-vl-plus support image processing

#### Doubao
- **Thinking support**: All models
- **Format**: `thinking={"type": "enabled"}`
- **Vision support**: doubao-seed-1-6-vision-250815

### Classes

#### LLM

Main interface for all LLM providers.

```python
llm = LLM(
    model="model-name",
    temperature=0.7,
    max_tokens=100,
    # ... other parameters
)
```

**Methods:**
- `chat(messages, **kwargs)` → `ChatResponse`: Send messages and get response
  - `reasoning_effort` (OpenAI GPT-5 only): "low", "medium", "high"

#### ChatMessage

Container for structured messages.

```python
message = ChatMessage(
    role="user",  # "user", "assistant", "system"
    content="text or list of content items"
)
```

#### ChatResponse

Response object from LLM.

**Attributes:**
- `content`: Response text
- `model`: Model used
- `usage`: Token usage statistics
- `finish_reason`: Completion reason

### Utility Functions

#### prepare_image_content(image_input)

Prepares image content for vision models.

```python
# Local file
image_content = prepare_image_content("./image.jpg")

# URL
image_content = prepare_image_content("https://example.com/image.jpg")
```

#### test_connection()

Quick connectivity test for available models.

```python
from provider_hub import test_connection
test_connection()
```

## Supported Models

### OpenAI
- `gpt-5`
- `gpt-5-mini`
- `gpt-5-nano`
- `gpt-4.1`

### DeepSeek  
- `deepseek-chat`
- `deepseek-reasoner`

### Qwen
- `qwen3-max-preview`
- `qwen-plus`
- `qwen-flash`
- `qwen3-coder-plus`
- `qwen3-coder-flash`
- `qwen-vl-max`
- `qwen-vl-plus`

### Doubao
- `doubao-seed-1-6-250615`
- `doubao-seed-1-6-vision-250815`
- `doubao-seed-1-6-flash-250828`

## Testing

### Quick Test

Test connectivity to available models:

```python
from provider_hub import test_connection
test_connection()
```

### Comprehensive Test Suite

Run full model testing with detailed reports:

```bash
python test_connection.py
```

This generates:
- `test_report.json` - Machine-readable results
- `test_report.md` - Human-readable report