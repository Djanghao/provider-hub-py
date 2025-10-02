# Provider Hub

Unified interface for accessing multiple LLM providers.

---

## Table of Contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Core Features](#core-features)
* [API Reference](#api-reference)
* [Supported Models](#supported-models)
* [Testing](#testing)

---

## Installation

```bash
pip install provider-hub
```

---

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

---

## Core Features

### Text Processing

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

---

### Vision Processing

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
image_content = prepare_image_content("https://example.com/image.jpg")

# Create a message with text + image
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

You can also include multiple images in the same request:

```python
# Prepare local images
image_content1 = prepare_image_content("path/to/your/image1.jpg")
image_content2 = prepare_image_content("path/to/your/image2.jpg")
# Add more images as needed

# Create a message with text + multiple images
messages = [
    ChatMessage(
        role="user",
        content=[
            {"type": "text", "text": "What do you see in these images?"},
            image_content1,
            image_content2,
            # Add additional image_content items here
        ]
    )
]
```

---

### Reasoning Mode

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

---

### System Prompt

Set a default system prompt when initializing `LLM`.

```python
from provider_hub import LLM

# Simple string system prompt
llm = LLM(
    model="doubao-seed-1-6-250615", 
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    timeout=30,
    system_prompt="You are a concise assistant."
)
response = llm.chat("Explain recursion in one paragraph")
print(response.content)

# Structured system prompt (list of role/content dicts)
llm2 = LLM(
    model="doubao-seed-1-6-250615", 
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    timeout=30,
    system_prompt=[{"role": "system", "content": "You are a helpful assistant."}]
)
response2 = llm2.chat("Summarize the API")
print(response2.content)
```

**Notes:**

* Do not pass `system` role message directly to `chat(...)`. Use `system_prompt` instead.
* For list format, `role` must be `"system"`.

---

### Streaming Mode

**Only supported by Doubao and Qwen models.**

This library provides two mechanisms for controlling streaming:

* `stream` (bool):

  * `True`: Returns an iterator yielding partial chunk dictionaries as the model generates output.
  * `False`: Returns a final `ChatResponse` object (default).

* `stream_options` (`dict[str, bool]`): Additional options for streaming responses. Only set this when `stream=True`.

  * Example: `{"include_usage": True}` → includes the total token usage in the last line of the output.

```python
from provider_hub import LLM

# Streaming with token usage included
llm = LLM(
    model="doubao-seed-1-6-250615", 
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    timeout=30,
    stream=True,
    stream_options={"include_usage": True}
)

response = llm.chat("Hello, how are you?")

for chunk in response:
    if chunk.choices:
        for choice in chunk.choices:
            if choice.delta.content:
                print(choice.delta.content, end='', flush=True)
    # Print only total token usage data
    else:
        print("\n", chunk.usage)
```

**Notes:**

* Not all providers or models support streaming. Always check a model’s capabilities before enabling streaming to avoid runtime errors.
* `stream_options` is provider-specific. Refer to the provider’s documentation for supported keys.

---

### OpenAI GPT-5 Reasoning Effort

GPT-5 models support adjustable reasoning intensity through the `chat` method.

```python
from provider_hub import LLM

# GPT-5 with high reasoning effort
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

---

## API Reference

### Parameters

| Parameter          | Type      | Description                | Range/Options                             |
| ------------------ | --------- | -------------------------- | ----------------------------------------- |
| `model`            | string    | Model identifier           | See [Supported Models](#supported-models) |
| `temperature`      | float     | Controls randomness        | 0.0–2.0                                   |
| `top_p`            | float     | Nucleus sampling threshold | 0.0–1.0                                   |
| `max_tokens`       | int       | Maximum response length    | Positive integer                          |
| `timeout`          | int       | Request timeout            | Seconds (default: 30)                     |
| `thinking`         | bool/dict | Enable reasoning mode      | Provider-specific format                  |
| `reasoning_effort` | string    | GPT-5 reasoning intensity  | "low", "medium", "high"                   |

---

### Parameter Support by Provider

| Parameter          | OpenAI | DeepSeek | Qwen | Doubao | Notes                                          |
| ------------------ | ------ | -------- | ---- | ------ | ---------------------------------------------- |
| `temperature`      | ✅      | ✅        | ✅    | ✅      | GPT-5 series limited to 1.0                    |
| `top_p`            | ✅      | ✅        | ✅    | ✅      | Full support                                   |
| `max_tokens`       | ✅      | ✅        | ✅    | ✅      | GPT-5 auto-converts to `max_completion_tokens` |
| `timeout`          | ✅      | ✅        | ✅    | ✅      | Full support                                   |
| `thinking`         | ❌      | ✅        | ✅    | ✅      | Model-specific availability                    |
| `reasoning_effort` | ✅      | ❌        | ❌    | ❌      | GPT-5 only                                     |

---

### Provider-Specific Notes

**OpenAI**

* GPT-5 series: only supports `temperature=1.0`; use `reasoning_effort`.
* GPT-4.1: full parameter support.

**DeepSeek**

* Thinking support only in `deepseek-reasoner` model (`thinking=True`).

**Qwen**

* Thinking support only in `qwen3-*` models (qwen3-max-preview, qwen3-coder-plus, qwen3-coder-flash) 
* Format: `thinking=True`
* Vision models `qwen-vl-max`, `qwen-vl-plus` support image processing.

**Doubao**

* Thinking supported by all models (`thinking={"type": "enabled"}`).
* Vision supported in `doubao-seed-1-6-vision-250815`.

**OpenAI_Compatible**

* Use your self-hosted model with this provider by supplying valid `model`, `provider`, `base_url`, and `api_key`.
* This provider requires `base_url` and `api_key` at initialization.

---

### Utility Functions

* **prepare_image_content(image_input)**

```python
# Local file
image_content = prepare_image_content("./image.jpg")

# URL
image_content = prepare_image_content("https://example.com/image.jpg")
```


---

## Supported Models

**OpenAI**

* gpt-5
* gpt-5-mini
* gpt-5-nano
* gpt-4.1

**DeepSeek**

* deepseek-chat
* deepseek-reasoner

**Qwen**

* qwen3-max-preview
* qwen-plus
* qwen-flash
* qwen3-coder-plus
* qwen3-coder-flash
* qwen-vl-max
* qwen-vl-plus
* qwen3-max
* qwen3-vl-plus
* qwen3-omni-flash
* qwen3-235b-a22b
* qwen3-vl-235b-a22b-thinking

**Doubao**

* doubao-seed-1-6-250615
* doubao-seed-1-6-vision-250815
* doubao-seed-1-6-flash-250828

---

## Testing

`-t`, `--test`
Run full connection tests.

```bash
# Test all models
provider-hub -t

# Test one model
provider-hub -t Doubao doubao-seed-1-6-250615

# Test one model with reasoning (when supported)
provider-hub -t Doubao doubao-seed-1-6-250615 -k
```

`-q`, `--quick-test`
Run lightweight connectivity checks.

```bash
# Quick test all models
provider-hub -q

# Quick test a single provider
provider-hub -q Doubao
```

`-k`, `--thinking`
Enable reasoning mode during a test. Used together with `-t`.

```bash
# Test all models with reasoning
provider-hub -t -k
```