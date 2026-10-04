# first_call.py —— 发出你的第一次大模型 API 请求，并把回答打印出来
# pip install openai python-dotenv
# 注意：需 API Key，未实跑。运行前先设置环境变量 OPENAI_API_KEY（做法见讲义第三节）。

import os
import sys

# 若项目根目录有 .env 文件（见讲义），自动加载；没装 python-dotenv 也不影响
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("还没安装 openai 库：请先激活虚拟环境，再运行 pip install openai")
    sys.exit(1)

# 常见错误的中文提示，不让用户直面英文 traceback
from openai import (
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)


def main():
    # Key 一律从环境变量读，绝不写死在代码里
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("没有找到 API Key。请先设置环境变量 OPENAI_API_KEY，例如：")
        print('  Windows PowerShell:  $env:OPENAI_API_KEY="sk-你的Key"')
        print("  Mac / Linux:         export OPENAI_API_KEY=sk-你的Key")
        print("或在项目根目录建 .env 文件写入 OPENAI_API_KEY=sk-你的Key（记得加进 .gitignore）")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    prompt = "用一句话向完全没接触过编程的人解释：什么是程序？"
    try:
        # 2026 年主流写法：Responses API。model 只是示例名，可能已更新，
        # 运行前按官网模型列表挑一款"当前便宜够用"的替换
        response = client.responses.create(model="gpt-4o-mini", input=prompt)
    except AuthenticationError:
        print("401 认证失败：Key 不对或没生效。检查是否复制完整、当前终端是否设置过环境变量。")
        sys.exit(1)
    except RateLimitError:
        print("429 请求被拒：多半是额度用完或欠费，去平台确认余额；也可能请求太频繁，稍等再试。")
        sys.exit(1)
    except NotFoundError:
        print("404 模型不存在：model 名写错了，去官网模型列表核对（注意大小写和横杠）。")
        sys.exit(1)
    except APIConnectionError:
        print("网络连不上：检查网络；访问境外平台可能需按其文档配置网络，或改用国内平台。")
        sys.exit(1)

    print("模型回答：")
    print(response.output_text)  # 回答文本就在这个字段
    usage = response.usage
    print(f"本次用量：输入 {usage.input_tokens} token，输出 {usage.output_tokens} token")

    # 老写法 chat.completions 在旧代码、旧教程里大量可见，会读即可：
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
