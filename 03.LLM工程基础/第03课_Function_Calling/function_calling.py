# 第03课示例代码：Function Calling 完整闭环（模型只决定"调哪个工具、参数是什么"，真正执行函数的是本脚本）
# pip install openai python-dotenv
# 说明：在线部分需 OPENAI_API_KEY 环境变量，未实跑；__main__ 里的"离线演示"不依赖 Key、可直接运行，先体验调度执行。

import ast
import json
import operator
import os

# dotenv 可选：没装也不影响运行，只是改用系统环境变量
try:
    from dotenv import load_dotenv

    load_dotenv()  # 支持把 OPENAI_API_KEY 放进同目录 .env（.env 别提交到 git）
except ImportError:
    pass

# 模型名更新很快，这里只是"便宜够用"的示例；学习时请去你的平台模型列表挑当前便宜的那款
MODEL = "gpt-4o-mini"


# ---------- 第一部分：本地工具（纯标准库，离线可跑） ----------

_SIMULATED_WEATHER = {
    "北京": {"condition": "晴", "high_c": 18, "low_c": 7},
    "上海": {"condition": "多云", "high_c": 22, "low_c": 15},
    "广州": {"condition": "小雨", "high_c": 27, "low_c": 21},
}


def get_weather(city: str) -> str:
    """模拟天气查询。真实项目里这里换成天气 API，函数签名和返回格式不变。"""
    data = _SIMULATED_WEATHER.get(city)
    if data is None:
        # 未知城市不编造，老实返回错误说明，让模型决定怎么向用户解释
        return json.dumps(
            {"error": f"没有'{city}'的模拟数据，目前仅支持北京/上海/广州"},
            ensure_ascii=False,
        )
    return json.dumps({"city": city, **data}, ensure_ascii=False)


# 只放行这几种运算节点；函数调用、变量、属性访问等一律拒绝
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不支持的语法：{type(node).__name__}")


def calculate(expression: str) -> str:
    """四则运算计算器。

    为什么不直接 eval：表达式是模型"生成"的，不可信——有人诱导模型输出
    __import__('os').system(...) 这类代码，eval 会真的执行。这里用 ast
    只允许加减乘除、括号和数字，其余全部拒绝。
    """
    try:
        result = _safe_eval(ast.parse(expression, mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError) as exc:
        return json.dumps({"error": f"这个表达式没法算：{exc}"}, ensure_ascii=False)
    result = round(result, 6)
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return json.dumps({"expression": expression, "result": result}, ensure_ascii=False)


# ---------- 第二部分：给模型的"菜单"（Responses API 的工具描述） ----------

TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "查询某城市当日模拟天气。仅当用户问到北京/上海/广州的天气时调用，其他话题不要调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "中文城市名，例如：北京"},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "计算算术表达式的结果，支持 + - * / 和括号。需要精确计算时使用，不要自己心算。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "算术表达式字符串，例如：(128*365+79)/12"},
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
]

# 调度表：单子上的工具名 → 本地函数。以后加新工具，在这里加一行就行。
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculate": calculate,
}


def run_tool(name: str, arguments_json: str) -> str:
    """按模型的单子执行本地函数。

    单子不可全信：函数名可能不存在、参数 JSON 可能非法、参数可能多传漏传，
    所以每一步都兜底——任何问题都返回"错误说明"而不是让程序崩溃。
    """
    func = TOOL_REGISTRY.get(name)  # 用 .get 而不是 []：模型幻觉出函数名时不至于 KeyError
    if func is None:
        available = "、".join(TOOL_REGISTRY)
        return json.dumps({"error": f"未知工具'{name}'，当前可用：{available}"}, ensure_ascii=False)
    try:
        arguments = json.loads(arguments_json) if arguments_json and arguments_json.strip() else {}
    except json.JSONDecodeError:
        return json.dumps({"error": "参数不是合法 JSON，请检查后重新调用"}, ensure_ascii=False)
    try:
        return func(**arguments)
    except TypeError as exc:  # 覆盖参数名错、多传、漏传等情况
        return json.dumps({"error": f"参数不对：{exc}"}, ensure_ascii=False)


# ---------- 第三部分：串起完整闭环（需要 API Key） ----------

MAX_ROUNDS = 5  # 轮数上限：防止模型反复要工具的异常情况把你的额度烧穿


def ask_model(question: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        print("还没安装 openai 库，请先执行：pip install openai")
        return ""

    api_key = os.environ.get("OPENAI_API_KEY")  # Key 一律从环境变量读，绝不写进代码
    if not api_key:
        print("没找到环境变量 OPENAI_API_KEY，请先设置（见第01课），或用 python-dotenv 从 .env 读取。")
        return ""

    client = OpenAI(api_key=api_key)
    conversation = [{"role": "user", "content": question}]

    for round_no in range(1, MAX_ROUNDS + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                input=conversation,
                tools=TOOLS,  # 每一轮都带上菜单，模型才能继续点下一道菜
                tool_choice="auto",
            )
        except Exception as exc:
            print(f"调用 API 失败：{exc}")
            print("常见原因：Key 不对、额度用完、网络不通，检查后重试。")
            return ""

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            # 模型觉得不需要工具了，output_text 就是最终的自然语言回答
            return response.output_text

        # 关键细节：先把模型的输出（含调用请求）放进历史，再逐个补上执行结果
        conversation += response.output
        print(f"[第 {round_no} 轮] 模型请求 {len(calls)} 个工具调用")
        for call in calls:
            print(f"    单子：{call.name}({call.arguments})")
            result = run_tool(call.name, call.arguments)
            print(f"    结果：{result}")
            conversation.append(
                {"type": "function_call_output", "call_id": call.call_id, "output": result}
            )

    return "工具调用轮数达到上限，提前结束。可以换个问法，或检查工具描述是否写得太模糊。"


if __name__ == "__main__":
    print("=" * 56)
    print("离线演示：不需要 Key，直接体验『调度执行』")
    print("=" * 56)
    demo_calls = [
        ("get_weather", json.dumps({"city": "北京"}, ensure_ascii=False)),
        ("calculate", json.dumps({"expression": "(128*365+79)/12"})),
        ("get_weather", json.dumps({"city": "成都"}, ensure_ascii=False)),  # 未知城市 → 看错误处理
        ("send_email", json.dumps({"to": "someone"})),  # 未知工具 → 看安全处理
        ("calculate", "我想算一加一"),  # 非法 JSON → 看安全处理
    ]
    for name, args in demo_calls:
        print(f"\n单子：{name}  参数：{args}")
        print(f"  -> {run_tool(name, args)}")

    print("\n" + "=" * 56)
    if os.environ.get("OPENAI_API_KEY"):
        question = "帮我查一下北京今天天气，再算算 (128*365+79)/12 等于多少。"
        print(f"正在问模型：{question}\n")
        answer = ask_model(question)
        if answer:
            print(f"\n模型的最终回答：{answer}")
    else:
        print("在线闭环需要 API Key：设置 OPENAI_API_KEY 环境变量后重新运行本脚本。")
        print("说明：本文件的 API 部分需 Key、未实跑；上面的离线演示已本地验证。")
