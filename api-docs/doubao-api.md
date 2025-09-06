Notice: do not modify this file unless requested.
# 1. doubao native sdk (prefered)
## default
```python
import os
from volcenginesdkarkruntime import Ark

client = Ark(api_key=os.environ.get("ARK_API_KEY"))

completion = client.chat.completions.create(
    model="doubao-1-5-pro-32k-250115",
    messages=[
        {"role": "user", "content": "You are a helpful assistant."}
    ]
)
print(completion.choices[0].message)
```
```response
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "Hello! How can I help you today?",
        "role": "assistant"
      }
    }
  ],
  "created": 1742631811,
  "id": "0217426318107460cfa43dc3f3683b1de1c09624ff49085a456ac",
  "model": "doubao-1-5-pro-32k-250115",
  "service_tier": "default",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 9,
    "prompt_tokens": 19,
    "total_tokens": 28,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```
## stream:
```python
import os

from volcenginesdkarkruntime import Ark

client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    resp = client.chat.completions.create(
        model="doubao-1-5-pro-32k-250115",
        messages=[{"content":"You are a helpful assistant.","role":"system"},{"content":"hello","role":"user"}],
        stream=True,
    )
    for chunk in resp:
        if not chunk.choices:
            continue

        print(chunk.choices[0].delta.content, end="")
```
```response
{"choices":[{"delta":{"content":"Hello","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":"!","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":" How","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":" can","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":" I","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":" help","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":" you","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":" today","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":"?","role":"assistant"},"index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

{"choices":[{"delta":{"content":"","role":"assistant"},"finish_reason":"stop","index":0}],"created":1742632436,"id":"021742632435712396f12d018b5d576a7a55349c2eba0815061fc","model":"doubao-1-5-pro-32k-250115","service_tier":"default","object":"chat.completion.chunk","usage":null}

[DONE]
```
## image input
```python
import os

from volcenginesdkarkruntime import Ark

client = Ark(api_key=os.environ.get("ARK_API_KEY"))


if __name__ == "__main__":
    resp = client.chat.completions.create(
        model="doubao-1-5-vision-pro-32k-250115",
        messages=[{"content":[{"image_url":{"url":"https://ark-project.tos-cn-beijing.volces.com/images/view.jpeg"},"type":"image_url"},{"text":"图片主要讲了什么?","type":"text"}],"role":"user"}],
    )
    print(resp.choices[0].message.content)
```
```response
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "画面中呈现了一幅宁静的户外景象。一个人乘坐在橙黄色的皮划艇上，手持船桨，正在平静的水面划行。水面如镜，倒映着周围景致。远处是茂密的森林，森林后方矗立着巍峨的雪山，山体覆盖着白雪。天空呈浅蓝色，飘浮着一些云朵。整体氛围静谧而美好，展现出自然的纯净与壮阔。 ",
        "role": "assistant"
      }
    }
  ],
  "created": 1742636149,
  "id": "0217426361458116592a076493be583bc5e33f80ac2dcf1efc31b",
  "model": "doubao-1-5-vision-pro-32k-250115",
  "service_tier": "default",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 85,
    "prompt_tokens": 521,
    "total_tokens": 606,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```
## thinking mode
```python
import os
# 升级方舟 SDK 到最新版本 pip install -U 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark

client = Ark(
    # 从环境变量中读取您的方舟API Key
    api_key=os.environ.get("ARK_API_KEY"), 
    # 深度思考模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
    timeout=1800,
    )
response = client.chat.completions.create(
    # 替换 <Model> 为您的Model ID
    model="doubao-seed-1.6-250615",
    messages=[
        {"role": "user", "content": "我要研究深度思考模型与非深度思考模型区别的课题，体现出我的专业性"}
    ],
     thinking={
         "type": "disabled" # 不使用深度思考能力,
         # "type": "enabled" # 使用深度思考能力
         # "type": "auto" # 模型自行判断是否使用深度思考能力
     },
)

print(response)
```
```response
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "研究“深度思考模型与非深度思考模型的区别”是一个兼具理论深度与实践意义的课题，...",
        "role": "assistant"
      }
    }
  ],
  "created": 1750342275,
  "id": "0217503421709253ddc3c2b93f219d1c79fa57be98ff8fa5ef2ba",
  "model": "doubao-seed-1-6-250615",
  "service_tier": "default",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 3178,
    "prompt_tokens": 54,
    "total_tokens": 3232,
    "prompt_tokens_details": { "cached_tokens": 0 },
    "completion_tokens_details": { "reasoning_tokens": 0 }
  }
}
```
# 2. Examples:
doubao-1.6
```python
# export ARK_API_KEY="YOUR_API_KEY" 查看API KEY \n\nimport os
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)

response = client.chat.completions.create(
    # 您可以前往 在线推理页 创建接入点后进行使用
    model="<YOUR_ENDPOINT_ID>",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                },
                {"type": "text", "text": "这是哪里？"},
            ],
        }
    ],
    
    # 免费开启推理会话应用层加密，访问 https://www.volcengine.com/docs/82379/1389905 了解更多
    extra_headers={'x-is-encrypted': 'true'},
    temperature=1,
    top_p=0.7,
    max_tokens=32768,
    thinking={"type":"enabled"},
)

print(response.choices[0])
```

doubao-1.6-thinking
```python
# export ARK_API_KEY="YOUR_API_KEY" 查看API KEY \n\nimport os
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)

response = client.chat.completions.create(
    # 您可以前往 在线推理页 创建接入点后进行使用
    model="<YOUR_ENDPOINT_ID>",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                },
                {"type": "text", "text": "这是哪里？"},
            ],
        }
    ],
    
    # 免费开启推理会话应用层加密，访问 https://www.volcengine.com/docs/82379/1389905 了解更多
    extra_headers={'x-is-encrypted': 'true'},
    max_tokens=32768,
)

print(response.choices[0])
```
doubao-1.6-vision
```python
# export ARK_API_KEY="YOUR_API_KEY" 查看API KEY \n\nimport os
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)

response = client.chat.completions.create(
    # 您可以前往 在线推理页 创建接入点后进行使用
    model="<YOUR_ENDPOINT_ID>",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                },
                {"type": "text", "text": "这是哪里？"},
            ],
        }
    ],
    
    # 免费开启推理会话应用层加密，访问 https://www.volcengine.com/docs/82379/1389905 了解更多
    extra_headers={'x-is-encrypted': 'true'},
    temperature=1,
    top_p=0.7,
    max_tokens=32768,
    thinking={"type":"enabled"},
)

print(response.choices[0])
```

文本消息部分 object
多模态消息中，内容文本输入。视觉理解模型、部分大语言模型支持此类型消息。
属性
messages.content.type string 必选
图像消息类型，此处应为 image_url。
messages.content.image_url object 必选
图片消息的内容部分。
属性
messages.content.image_url.url string 必选
支持传入图片链接或图片的Base64编码，不同模型支持图片大小略有不同，具体请参见使用说明。
messages.content.image_url.detail string / null  默认值 low
支持手动设置图片的质量。
high：高细节模式，适用于需要理解图像细节信息的场景，如对图像的多个局部信息/特征提取、复杂/丰富细节的图像理解等场景，理解更全面。此时 min_pixels 取值3136、max_pixels 取值4014080。
low：低细节模式，适用于简单的图像分类/识别、整体内容理解/描述等场景，理解更快速。此时 min_pixels 取值3136、max_pixels 取值1048576。
auto：默认模式，不同模型选择的模式略有不同，具体请参见理解图像的深度控制。

# 3. openai sdk
```node.js
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.['ARK_API_KEY'],
  baseURL: 'https://ark.cn-beijing.volces.com/api/v3',
});

// Image input:
async function main() {
  const response = await openai.chat.completions.create({
    apiKey: process.env['ARK_API_KEY'],
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'image_url',
            image_url: {
              url: 'https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg',
            },
          },
          { type: 'text', text: '这是哪里？' },
        ],
      },
    ],
    model: '{TEMPLATE_ENDPOINT_ID}',
  });

  console.log(response.choices[0]);
}

main();
```

