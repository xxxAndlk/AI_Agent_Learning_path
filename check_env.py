# -*- coding: utf-8 -*-
"""
环境自检脚本（纯标准库，无需先安装任何第三方库）

用法：
    python check_env.py

作用：检查 Python 版本、各章要用的第三方库、API Key 是否就绪，并给出中文建议。
支持 OpenAI 及国产模型（DeepSeek / 智谱 GLM / 通义千问 / Kimi）的 Key 识别。
脚本正常退出（返回 0），缺少可选库不算错误，按提示按需安装即可。
"""

import sys
import os
import importlib.util


# 支持的 Key 环境变量名 → 对应厂商
KEY_NAMES = [
    ("OPENAI_API_KEY", "OpenAI"),
    ("DEEPSEEK_API_KEY", "DeepSeek"),
    ("ZHIPU_API_KEY", "智谱 GLM"),
    ("DASHSCOPE_API_KEY", "通义千问"),
    ("MOONSHOT_API_KEY", "Kimi"),
    ("LLM_API_KEY", "自定义兼容服务"),
]

# base_url 关键字 → 厂商
BASE_URL_RULES = [
    ("api.deepseek.com", "DeepSeek"),
    ("open.bigmodel.cn", "智谱 GLM"),
    ("dashscope.aliyuncs.com", "通义千问"),
    ("api.moonshot.cn", "Kimi"),
    ("api.openai.com", "OpenAI"),
]


def guess_provider(base_url):
    """根据 base_url 猜测厂商；识别不出返回 None。"""
    if not base_url:
        return None
    low = base_url.lower()
    for kw, name in BASE_URL_RULES:
        if kw in low:
            return name
    return None


def load_env_file():
    """读取脚本同目录的 .env（不依赖第三方库）。
    返回 {变量名: 值}；文件不存在或读不了返回空字典。"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    data = {}
    if not os.path.exists(env_path):
        return data
    try:
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                data[name.strip()] = value.strip()
    except OSError:
        return {}
    return data


def detect_key():
    """检测已配置的 Key。环境变量优先于 .env 文件。
    返回 (key值, 变量名, 厂商)；都没有返回 (None, None, None)。"""
    file_env = load_env_file()

    for var, provider in KEY_NAMES:  # 先查环境变量
        val = os.environ.get(var)
        if val:
            p = guess_provider(os.environ.get("OPENAI_BASE_URL")) or provider
            return val, var, p

    for var, provider in KEY_NAMES:  # 再查 .env
        val = file_env.get(var)
        if val:
            p = guess_provider(file_env.get("OPENAI_BASE_URL")) or provider
            return val, var, p

    return None, None, None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=" * 52)
    print("AI Agent 学习路径 · 环境自检")
    print("=" * 52)

    v = sys.version_info
    print("\n[1] Python 版本：%d.%d.%d（系统：%s）"
          % (v.major, v.minor, v.micro, sys.platform))
    if (v.major, v.minor) >= (3, 10):
        print("    [OK] 版本符合要求（推荐 3.12 及以上）")
    else:
        print("    [!!] 版本偏旧，建议升级到 Python 3.12+")
        print("         https://www.python.org/downloads/")

    libs = [
        ("openai",        "第3章：调用大模型"),
        ("dotenv",        "第3章：读取 .env 配置"),
        ("requests",      "第1/14章：发送网络请求"),
        ("langchain",     "第4章：LangChain 框架"),
        ("langchain_core","第4章：核心组件"),
        ("chromadb",      "第5章：向量数据库 Chroma"),
        ("faiss",         "第7章：向量库 FAISS"),
        ("numpy",         "第2/9章：数值计算"),
        ("pandas",        "第9章：数据处理"),
        ("fastapi",       "第14章：后端接口"),
        ("streamlit",     "第14章：快速做界面"),
    ]
    print("\n[2] 第三方库（没装 = 正常，学到再装）")
    for mod, desc in libs:
        ready = importlib.util.find_spec(mod) is not None
        print("    %s %-14s %s" % ("[OK]" if ready else "[  ]", mod, desc))

    key, var, provider = detect_key()
    print("\n[3] 大模型 API Key：")
    if key:
        print("    [OK] 已检测到 %s（厂商：%s）" % (var, provider))
        print("         出于安全，不显示 Key 的具体内容。")
    else:
        print("    [  ] 还没配置。第 1 章不需要；")
        print("         想不花钱先试一次：看《新手使用指南.md》")
        print("         第四节「零成本第一次调用」（DeepSeek 注册送额度）。")

    openai_ready = importlib.util.find_spec("openai") is not None
    print("\n" + "=" * 52)
    print("结论：")
    print("  · 学第 1 章：现在就能开始，只需 Python，不用装任何库。")
    if key and openai_ready:
        print("  · 学第 3 章及以后：Key 和 openai 库都就绪，可以出发了。")
    elif key and not openai_ready:
        print("  · Key 已就绪，再执行一次 pip install openai python-dotenv，")
        print("    就能开始第 3 章。")
    else:
        print("  · 学到第 3 章前：执行 pip install openai python-dotenv，")
        print("    再按指南第四节配置 Key（可用免费额度）即可。")
    print("=" * 52)


if __name__ == "__main__":
    main()
