from openai import OpenAI

client = OpenAI()

# 使用Responses API的file_search工具
response = client.responses.create(
    model="gpt-5.4-mini",
    input="公司年假政策是什么？",
    tools=[{
        "type": "file_search",
        "vector_store_ids": ["vs_xxx"]
    }]
)
