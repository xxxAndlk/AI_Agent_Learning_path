# first_call.py —— 第一次调用大模型：向 DeepSeek 发一句话，并把回答打印出来
# 前置：已激活虚拟环境、pip install openai python-dotenv、已设置环境变量 DEEPSEEK_API_KEY
import os
import sys

# 若文件夹里有 .env 文件，自动加载；没装 python-dotenv 也不影响
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("还没安装 openai 库：请先激活虚拟环境（命令行前有 (.venv)），再运行 pip install openai")
    sys.exit(1)

# 调用失败时的几类常见错误，各自给一句中文提示，不让你直面英文报错
from openai import (
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)


def main():
    # Key 一律从环境变量读，绝不写死在代码里
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("没有找到 API Key。请先在当前终端设置环境变量 DEEPSEEK_API_KEY：")
        print('  Windows PowerShell:  $env:DEEPSEEK_API_KEY="sk-你的Key"')
        print("  Mac / Linux:         export DEEPSEEK_API_KEY=sk-你的Key")
        print("或在本文件夹建 .env，写入 DEEPSEEK_API_KEY=sk-你的Key（记得加进 .gitignore）。")
        sys.exit(1)

    # DeepSeek 兼容 openai 库：除了 Key，只需多给一个 base_url，指向它的服务器
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    question = "用一句话向完全没接触过编程的人解释：什么是程序？"
    try:
        # 2026 年的新写法 Responses API；model 用 DeepSeek 当前便宜够用的 deepseek-flash
        response = client.responses.create(model="deepseek-flash", input=question)
    except AuthenticationError:
        print("401 认证失败：Key 不对或没生效。检查是否复制完整、当前终端是否设置过环境变量。")
        sys.exit(1)
    except RateLimitError:
        print("429 请求被拒：多半是额度用完或欠费，去 platform.deepseek.com 看余额；也可能太频繁，稍等再试。")
        sys.exit(1)
    except NotFoundError:
        print("404 模型不存在：模型名写错了，去 DeepSeek 官网模型列表核对（deepseek-flash，全小写、中间是横杠）。")
        sys.exit(1)
    except APIConnectionError:
        print("网络连不上：确认能打开 platform.deepseek.com，检查网络后重试。")
        sys.exit(1)

    print("模型回答：")
    print(response.output_text)  # 回答文本就在这个字段
    usage = getattr(response, "usage", None)
    if usage is not None:
        print(f"本次用量：输入 {usage.input_tokens} token，输出 {usage.output_tokens} token")

    # 旧写法 chat.completions 在老教程里大量可见，DeepSeek 也支持，会读即可：
    # response = client.chat.completions.create(
    #     model="deepseek-flash",
    #     messages=[{"role": "user", "content": question}],
    # )
    # print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
