# 第04课《Tools 与 Agent》配套演示：@tool 定义工具 + create_agent 组装 Agent
# pip install langchain langchain-openai python-dotenv
# 运行说明：文件末尾的"离线演示"只调本地工具，不需要 API Key，可直接跑；
#           Agent 对话部分需要设置环境变量 OPENAI_API_KEY（本机未实跑）。
# 安全红线：计算器用 ast 白名单解析表达式，绝不用 eval（原因见讲义第 03 课回顾）。

import ast
import operator
import os

try:
    from langchain_core.tools import StructuredTool, ToolException, tool
except ImportError:
    raise SystemExit("缺少依赖：请先执行 pip install langchain langchain-openai python-dotenv")

try:
    from dotenv import load_dotenv

    load_dotenv()  # 支持把 Key 写在 .env 文件里（.env 不要提交到 git）
except ImportError:
    pass

# docstring 就是给模型看的说明书：写清"做什么"更要写清"什么时候别用"
@tool
def get_weather(city: str) -> str:
    """查询北京/上海/广州当天的模拟天气。仅支持这三个城市，其他城市不要调用本工具。"""
    data = {
        "北京": "晴，最高 18℃",
        "上海": "多云，最高 22℃",
        "广州": "阵雨，最高 27℃",
    }
    return data.get(city, f"暂无 {city} 的数据")


_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_calc(node):
    # 只放行数字和四则运算，其余节点（变量、函数调用……）一律拒绝
    if isinstance(node, ast.Expression):
        return _safe_calc(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_calc(node.left), _safe_calc(node.right))
    raise ValueError("只支持数字与加减乘除、括号")


# StructuredTool.from_function + handle_tool_error=True：工具内部抛 ToolException 时，
# 框架把错误信息当"执行结果"回填给模型，程序不崩
# （版本注意：v1.x 的 @tool 装饰器工厂已不接受 handle_tool_error 参数，开关要开在工具对象上）
def calculator_func(expression: str) -> str:
    """计算一个算术表达式的值。expression 只能包含数字、加减乘除、括号和空格，例如 (12+8)*3。"""
    try:
        return str(_safe_calc(ast.parse(expression, mode="eval")))
    except Exception:
        raise ToolException(f"无法计算表达式 {expression!r}：只支持数字与加减乘除、括号")


calculator = StructuredTool.from_function(
    func=calculator_func,
    name="calculator",
    handle_tool_error=True,  # description 自动取上面的 docstring
)


def offline_demo():
    print("== 离线演示：直接调用工具（不需要 API Key）==")
    # 看看 @tool 从函数身上自动提取出的"模型视角说明书"
    print(f"工具名：{get_weather.name}；参数 schema：{get_weather.args}")
    for city in ("北京", "上海"):
        print(f"get_weather({city!r}) -> {get_weather.invoke({'city': city})}")
    print(f"get_weather('成都') -> {get_weather.invoke({'city': '成都'})}")

    for expr in ("(12+8)*3", "100/8"):
        print(f"calculator({expr!r}) -> {calculator.invoke({'expression': expr})}")
    # 故意喂一个非法表达式：ToolException 被框架转成一句友好说明返回，而不是 traceback
    print(f"calculator('1+abc') -> {calculator.invoke({'expression': '1+abc'})}")


def agent_demo():
    # 延迟导入：没装 langchain 全家桶时，上面的离线演示照常可跑
    try:
        from langchain.agents import create_agent
        from langchain_openai import ChatOpenAI
    except ImportError:
        print("\n== Agent 演示跳过：请先 pip install langchain langchain-openai ==")
        return

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n== Agent 演示跳过：未检测到环境变量 OPENAI_API_KEY ==")
        print("设置方法：PowerShell 执行 $env:OPENAI_API_KEY=\"sk-...\"，或写入 .env 用 python-dotenv 读取")
        return

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)  # 示例模型名，可能已更新：按官网模型列表选

    agent = create_agent(
        model=llm,
        tools=[get_weather, calculator],
        system_prompt="你是助理。只能用提供的工具查天气、做计算；查不到就直说，不要编造。",
    )

    print("\n== Agent 演示（需 API Key，未实跑）==")
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "北京和上海今天哪个更热？温差是多少度？"}]}
        )
        print("Agent 最终回答：", result["messages"][-1].content)
    except Exception as err:
        # 网络/Key/额度类故障给中文提示，不抛裸 traceback
        print(f"Agent 调用失败：{err}")
        print("常见原因：Key 未设置或不正确、网络不通、账户额度不足。")


if __name__ == "__main__":
    offline_demo()
    agent_demo()
