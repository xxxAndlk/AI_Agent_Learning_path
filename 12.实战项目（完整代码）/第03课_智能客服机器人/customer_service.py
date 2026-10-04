# -*- coding: utf-8 -*-
"""智能客服机器人（第03课实战项目）：意图识别 -> 知识库检索 -> 口吻模板回复。

零依赖可跑（纯标准库）：
    python customer_service.py        # 进入命令行对话（输入 q 退出）
    python customer_service.py demo   # 自动轮播三类典型对话
可选升级（需 API Key，未实跑）：pip install openai 后 polish_with_llm() 可让模型
把"模板骨架 + 检索到的制度"润色成更有温度的回复。
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 知识库
# 客服最常被问的制度（生产中换成向量检索/文档库）
KB = {
    "年假": "年假：入职满一年每年 5 天，满三年 10 天，满五年 15 天，需提前 3 个工作日申请",
    "报销": "报销：票据需在费用发生后 10 个工作日内提交，住宿上限每晚 400 元",
    "vpn": "VPN：在 IT 服务台提交工单，审批通过后邮件下发安装指引",
    "wifi": "Wi-Fi：办公网 SSID 为 OFFICE，访客网 SSID 为 GUEST（需短信验证码）",
}

GREET_WORDS = ("你好", "您好", "在吗", "hi", "hello")
COMPLAINT_WORDS = ("投诉", "垃圾", "烂", "气死", "忍无可忍", "态度")

# 口吻模板：骨架话术人定，模型（如有）只负责润色填充
TONE = {
    "greet": "您好，我是智能助手小智 😊 请问有什么可以帮您？",
    "complaint": (
        "实在抱歉给您带来了不好的体验，您的反馈我已经详细记录，"
        "会第一时间转交给人工客服跟进，请您稍候。"
    ),
    "miss": (
        "这个问题我暂时没有查到准确依据，不敢乱说。"
        "已为您转接人工客服，或您可以换个说法再试试～"
    ),
    "hit": "您好，关于「{topic}」：{fact}。还有其他问题随时找我！",
    "other": "抱歉，这个问题超出了我的服务范围，已为您转接人工客服。",
}


# ---------------------------------------------------------------- 意图识别
def detect_intent(msg):
    """关键词分流：问候/投诉/咨询/其他。生产中换成模型分类，思路相同。"""
    low = msg.lower()
    if any(w in low for w in COMPLAINT_WORDS):
        return "complaint"
    if any(w in low for w in GREET_WORDS):
        return "greet"
    if any(k in msg for k in KB):
        return "ask"
    return "other"


# ---------------------------------------------------------------- 检索与回答
def lookup(msg):
    """查知识库，返回 (关键词, 制度原文) 或 None。"""
    for k, fact in KB.items():
        if k in msg:
            return k, fact
    return None


def polish_with_llm(question, fact):
    """可选升级：让模型把制度润色得更有温度。缺 Key/缺库/失败都退回 None。"""
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI  # pip install openai
    except ImportError:
        return None
    try:
        client = OpenAI()
        resp = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),  # 示例名，按官网当前列表替换
            input=(
                "你是公司客服。按下面的固定口吻回复用户，答案必须只用给定制度内容，"
                "制度里没有的不要编。\n"
                f"口吻：亲切专业、一句话答复、结尾主动提供后续帮助。\n"
                f"制度：{fact}\n用户问题：{question}"
            ),
        )
        return resp.output_text
    except Exception:
        return None


def answer(msg):
    """主线：意图 -> 分流 -> 组回复。查不到老实承认，绝不硬编。"""
    intent = detect_intent(msg)
    if intent == "ask":
        hit = lookup(msg)
        if hit is None:
            return TONE["miss"], "查无依据"
        topic, fact = hit
        polished = polish_with_llm(msg, fact)
        if polished:
            return polished, f"《{topic}》(模型润色)"
        return TONE["hit"].format(topic=topic, fact=fact), f"《{topic}》"
    return TONE[intent], "话术"  # greet/complaint/other 走模板


# ---------------------------------------------------------------- 对话循环
def chat():
    print("=" * 50)
    print("智能客服小智（输入 q 退出）")
    print("=" * 50)
    while True:
        try:
            msg = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            return
        if not msg:
            continue
        if msg.lower() == "q":
            print("小智：感谢咨询，再见！")
            return
        reply, src = answer(msg)
        print(f"小智：{reply}    （依据：{src}）")


def demo():
    print("=" * 50)
    print("智能客服 · 三类典型对话自动演示")
    print("=" * 50)
    for msg in ["在吗", "差旅报销有什么要求", "你们这系统也太烂了吧"]:
        print(f"你：{msg}")
        reply, src = answer(msg)
        print(f"小智：{reply}    （依据：{src}）\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        chat()


if __name__ == "__main__":
    main()
