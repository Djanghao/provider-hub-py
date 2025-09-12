Notice: do not modify this file unless requested.
Supported Models:
- qwen3-max-preview
- qwen-plus
- qwen-flash
- qwen3-coder-plus
- qwen3-coder-flash
- qwen-vl-max
- qwen-vl-plus

OpenAI 兼容
使用SDK调用时需配置的base_url：https://dashscope.aliyuncs.com/compatible-mode/v1

1. 文本输入
```python
import os
from openai import OpenAI


client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
    # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
    # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
    # extra_body={"enable_thinking": False},
)
print(completion.model_dump_json())
```
```node.js
import OpenAI from "openai";

const openai = new OpenAI(
    {
        // 若没有配置环境变量，请用百炼API Key将下行替换为：apiKey: "sk-xxx",
        apiKey: process.env.DASHSCOPE_API_KEY,
        baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
);

async function main() {
    const completion = await openai.chat.completions.create({
        model: "qwen-plus",  //此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages: [
            { role: "system", content: "You are a helpful assistant." },
            { role: "user", content: "你是谁？" }
        ],
    });
    console.log(JSON.stringify(completion))
}

main();
```
多轮输入:
通义千问 API 是无状态的 (Stateless)。它不会自动记录历史对话。要实现多轮对话，开发者必须在每次请求中显式地传递完整的上下文信息。

工作原理
实现多轮对话的核心是维护一个 messages 数组。每一轮对话都需要将用户的最新提问和模型的历史回复追加到此数组中，并将其作为下一次请求的输入。
以下示例为多轮对话时 messages 的状态变化：

第一轮对话

向messages 数组添加用户问题。
 
[
    {"role": "user", "content": "推荐一部关于太空探索的科幻电影。"}
]
第二轮对话
向messages数组添加大模型回复内容与用户的最新提问。
[
    {"role": "user", "content": "推荐一部关于太空探索的科幻电影。"},
    {"role": "assistant", "content": "我推荐《xxx》，这是一部经典的科幻作品。"},
    {"role": "user", "content": "这部电影的导演是谁？"}
]

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_response(messages):
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=messages
    )
    return completion.choices[0].message.content

# 初始化 messages
messages = []

# 第 1 轮
messages.append({"role": "user", "content": "推荐一部关于太空探索的科幻电影。"})
print("第1轮")
print(f"用户：{messages[0]['content']}")
assistant_output = get_response(messages)
messages.append({"role": "assistant", "content": assistant_output})
print(f"模型：{assistant_output}\n")

# 第 2 轮
messages.append({"role": "user", "content": "这部电影的导演是谁？"})
print("第2轮")
print(f"用户：{messages[-1]['content']}")
assistant_output = get_response(messages)
messages.append({"role": "assistant", "content": assistant_output})
print(f"模型：{assistant_output}\n")
```
```node.js
import OpenAI from "openai";

const BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1";
const openai = new OpenAI({
  apiKey: process.env.DASHSCOPE_API_KEY,
  baseURL: BASE_URL,
});

async function getResponse(messages) {
  const completion = await openai.chat.completions.create({
    model: "qwen-plus",
    messages: messages,
  });
  return completion.choices[0].message.content;
}

async function runConversation() {
  const messages = [];

  // 第 1 轮
  messages.push({ role: "user", content: "推荐一部关于太空探索的科幻电影。" });
  console.log("第1轮");
  console.log("用户：" + messages[0].content);

  let assistant_output = await getResponse(messages);
  messages.push({ role: "assistant", content: assistant_output });
  console.log("模型：" + assistant_output + "\n");

  // 第 2 轮
  messages.push({ role: "user", content: "这部电影的导演是谁？" });
  console.log("第2轮");
  console.log("用户：" + messages[messages.length - 1].content);

  assistant_output = await getResponse(messages);
  messages.push({ role: "assistant", content: assistant_output });
  console.log("模型：" + assistant_output + "\n");
}

runConversation();
```
应用于生产环境
多轮对话会带来巨大的 Token 消耗，且容易超出大模型上下文最大长度导致报错。以下策略可帮助您有效管理上下文与控制成本。

1. 上下文管理
messages 数组会随对话轮次增加而变长，最终可能超出模型的 Token 限制。建议参考以下内容，在对话过程中管理上下文长度。

1.1. 上下文截断
当对话历史过长时，保留最近的 N 轮对话历史。该方式实现简单，但会丢失较早的对话信息。

1.2. 滚动摘要
为了在不丢失核心信息的前提下动态压缩对话历史，控制上下文长度，可随着对话的进行对上下文进行摘要：

a. 对话历史达到一定长度（如上下文长度最大值的 70%）时，将对话历史中较早的部分（如前一半）提取出来，发起独立 API 调用使大模型对这部分内容生成“记忆摘要”；

b. 构建下一次请求时，用“记忆摘要”替换冗长的对话历史，并拼接最近的几轮对话。

1.3. 向量化召回
滚动摘要会丢失部分信息，为了使模型可以从海量对话历史中“回忆”起相关信息，可将对话管理从“线性传递”转变为“按需检索”：

a. 每轮对话结束后，将该轮对话存入向量数据库；

b. 用户提问时，通过相似度检索相关对话记录；

c. 将检索到的对话记录与最近的用户输入拼接后输入大模型。  

2. 成本控制
输入 Token 数会随着对话轮数的增加显著增加使用成本，以下成本管理策略供您参考。

2.1. 减少输入 Token
通过上文介绍的上下文管理策略减少输入 Token，降低成本。

2.2. 使用支持上下文缓存的模型
发起多轮对话请求时，messages 部分会重复计算并计费。阿里云百炼对qwen-max、qwen-plus等模型提供了上下文缓存功能，可以降低使用成本并提升响应速度，建议优先使用支持上下文缓存的模型。


2. 图片输入
```python
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-plus",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[{"role": "user","content": [
            {"type": "image_url",
             "image_url": {"url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"}},
            {"type": "text", "text": "这是什么"},
            ]}]
    )
print(completion.model_dump_json())
```
```node.js
import OpenAI from "openai";

const openai = new OpenAI(
    {
        // 若没有配置环境变量，请用百炼API Key将下行替换为：apiKey: "sk-xxx",
        apiKey: process.env.DASHSCOPE_API_KEY,
        baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
);

async function main() {
    const response = await openai.chat.completions.create({
        model: "qwen-vl-max", // 此处以qwen-vl-max为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages: [{role: "user",content: [
            { type: "image_url",image_url: {"url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"}},
            { type: "text", text: "这是什么？" },
        ]}]
    });
    console.log(JSON.stringify(response));
}

main();
```
3. 工具调用
```python
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
)

tools = [
    # 工具1 获取当前时刻的时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}  # 因为获取当前时间无需输入参数，因此parameters为空字典
        }
    },  
    # 工具2 获取指定城市的天气
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {  
                "type": "object",
                "properties": {
                    # 查询天气时需要提供位置，因此参数设置为location
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
messages = [{"role": "user", "content": "杭州天气怎么样"}]
completion = client.chat.completions.create(
    model="qwen-plus",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=messages,
    tools=tools
)

print(completion.model_dump_json())
```
```node.js
import OpenAI from "openai";

const openai = new OpenAI(
    {
        // 若没有配置环境变量，请用百炼API Key将下行替换为：apiKey: "sk-xxx",
        apiKey: process.env.DASHSCOPE_API_KEY,
        baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
);

const messages = [{"role": "user", "content": "杭州天气怎么样"}];
const tools = [
// 工具1 获取当前时刻的时间
{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "当你想知道现在的时间时非常有用。",
        // 因为获取当前时间无需输入参数，因此parameters为空
        "parameters": {}  
    }
},  
// 工具2 获取指定城市的天气
{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "当你想查询指定城市的天气时非常有用。",
        "parameters": {  
            "type": "object",
            "properties": {
                // 查询天气时需要提供位置，因此参数设置为location
                "location": {
                    "type": "string",
                    "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                }
            },
            "required": ["location"]
        }
    }
}
];

async function main() {
    const response = await openai.chat.completions.create({
        model: "qwen-plus", // 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages: messages,
        tools: tools,
    });
    console.log(JSON.stringify(response));
}

main();
```
