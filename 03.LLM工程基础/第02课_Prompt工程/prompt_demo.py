# 第02课配套演示：同一个任务，"差提示"与"好提示"各跑一次，亲眼看看差距
# pip install openai python-dotenv
# 需要 API Key（环境变量 OPENAI_API_KEY），未填 key 时只跑文末的离线小练
# 注：需要 API Key，未实跑；模型名只是示例，可能已更新，按官网模型列表选一个便宜够用的

import os

# 没装 openai 也不影响下面的离线小练
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# .env 里有 OPENAI_API_KEY 的话自动读进来（没有 python-dotenv 也不影响，环境变量照常生效）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = os.environ.get("DEMO_MODEL", "gpt-4o-mini")  # 示例名，按官网模型列表自行替换

# 装了 openai 才建客户端；没装时为 None，走文末离线小练
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) if OpenAI else None


def ask(prompt, system=None):
    """发一条提示给模型，返回回答文本。

    system 相当于常驻的"角色设定"，prompt 是这次的活儿。
    新代码用 Responses API；你还会在网上大量见到旧的 chat.completions 写法，会读即可。
    """
    kwargs = {"model": MODEL, "input": prompt}
    if system:
        kwargs["instructions"] = system
    resp = client.responses.create(**kwargs)
    return resp.output_text


# ---- 同一个任务，两版提示 ----
TASK_BAD = "帮我写个请假短信。"

TASK_GOOD = (
    "我是公司职员小李，明天因带孩子看病需要请一天事假，领导姓王，平时沟通客气但不啰嗦。"
    "请写一条请假微信：说明原因和时间，主动提工会工作已交接给同事小张，"
    "不超过 60 字，结尾不用客套话。"
)


def main():
    print("=" * 50)
    print("【差提示】", TASK_BAD)
    print("-" * 50)
    print(ask(TASK_BAD))
    print()
    print("=" * 50)
    print("【好提示】", TASK_GOOD)
    print("-" * 50)
    print(ask(TASK_GOOD, system="你是一位帮忙处理日常职场沟通的助手。"))


def offline_check():
    """离线小练：不花一分钱，用写死的文本按规则检查提示有没有关键零件。

    真正发请求前先本地自检一遍，能提前抓住大部分"话没说清楚"。
    """
    samples = [
        ("帮我写个通知。", False),
        ("用表格列出Python的5个优点，每条不超过20字。", True),
        ("你是一位小学老师，给三年级学生解释为什么先乘除后加减。", True),
    ]
    for text, expected in samples:
        has_task = any(v in text for v in ("写", "列出", "解释", "总结", "改写", "判断"))
        has_shape = any(v in text for v in ("不超过", "以内", "格式", "表格", "条"))
        has_role = "你是" in text  # 交代了角色，也算把话说清楚的一种
        ok = has_task and (has_shape or has_role)
        verdict = "任务明确，交代了输出要求或角色" if ok else "说得太模糊，缺任务或缺要求"
        print(f"[{'通过' if ok == expected else '不符预期'}] {text}\n  -> {verdict}\n")


if __name__ == "__main__":
    if OpenAI is None or not os.environ.get("OPENAI_API_KEY"):
        print("未检测到 OPENAI_API_KEY（或还没装 openai 库）：本次只跑离线小练，不调用模型。")
        print("配置方法：pip install openai python-dotenv，系统环境变量里加 OPENAI_API_KEY，")
        print("或在本目录建 .env 文件写一行 OPENAI_API_KEY=sk-...（.env 别提交到 git）\n")
        offline_check()
    else:
        try:
            main()
        except Exception as e:
            # 常见情况：key 无效 / 网络不通 / 额度用尽。别让红 traceback 吓到学生。
            msg = str(e)
            if "401" in msg or "invalid" in msg.lower():
                print("调用失败：API Key 无效或未生效，请回第 01 课检查 Key 的创建与配置。")
            elif "429" in msg or "quota" in msg.lower() or "insufficient" in msg.lower():
                print("调用失败：额度不足或请求太频繁，去平台确认余额与限流设置。")
            else:
                print(f"调用失败：网络或服务暂时不可用（{msg}）。检查网络后稍后再试。")
