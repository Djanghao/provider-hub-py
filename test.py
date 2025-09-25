from provider_hub import LLM

# Simple string system prompt
llm = LLM(
    model="qwen3-max", 
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    timeout=30,
    stream=True,
    stream_options={"include_usage": True}
)

response = llm.chat("Hello, how are you?")
# for chunk in response:
#     if chunk.choices:
#         for choice in chunk.choices:
#             # only print chunks that include response
#             if choice.delta.content:
#                 print(chunk.model_dump_json())
#     # Print the last line with total token usage
#     else:
#         print(chunk.model_dump_json())

# # Or if you only want to flush out the response word by word:
for chunk in response:
    if chunk.choices:
        for choice in chunk.choices:
            if choice.delta.content:
                print(choice.delta.content, end='', flush=True)
    # Print only total token usage data
    else:
        print("\n", chunk.usage)