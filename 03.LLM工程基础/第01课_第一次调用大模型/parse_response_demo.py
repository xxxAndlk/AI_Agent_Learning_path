# parse_response_demo.py —— 不需要 API Key：解析一段写死的模拟返回，练习"读字段"
# 运行：python parse_response_demo.py
# 目的：让你在没花钱、没联网的情况下，先看懂模型返回的"包裹"里都有什么、回答藏在哪。

import json

# 一段模拟的 Responses API 返回（真实返回字段更多，这里保留最常用的部分）
# 注意：这是写死的教学数据，不是真实调用结果
mock_response = """
{
  "id": "resp_demo_001",
  "model": "gpt-4o-mini",
  "output_text": "程序就是把你想让电脑做的事，写成它能照着执行的步骤清单。",
  "usage": {
    "input_tokens": 18,
    "output_tokens": 27,
    "total_tokens": 45
  }
}
"""

# json.loads 把 JSON 字符串变成 Python 的字典，之后就能按"键"取值了
data = json.loads(mock_response)

print("=== 先看整个包裹里有什么 ===")
print("本次调用的编号 id :", data["id"])
print("用到的模型 model  :", data["model"])

print("\n=== 回答藏在哪 ===")
print("回答内容 output_text:")
print(data["output_text"])

print("\n=== 花了多少 token ===")
usage = data["usage"]
print(f"输入 {usage['input_tokens']} + 输出 {usage['output_tokens']} = 共 {usage['total_tokens']} token")

# 老写法 chat.completions 的返回长这样，回答在更深一层：
mock_old = """
{
  "choices": [
    {"message": {"role": "assistant", "content": "这是老写法里的回答文本"}}
  ]
}
"""
old = json.loads(mock_old)
print("\n=== 老写法 chat.completions 的读法 ===")
print(old["choices"][0]["message"]["content"])
