# 用途：纯标准库离线演示 Tool Use 工程细节——工具注册表、get 兜底、参数校验重试、错误恢复
# 运行：python tool_use_demo.py（零依赖、零密钥）

MAX_RETRIES = 2  # 重试上限：参数类错误最多修正重试这么多次

TOOL_REGISTRY = {}  # 名字 -> {"description", "func"}；查询一律用 .get，查不到走兜底


def register(description):
    """装饰器：把函数登记进工具注册表（名字取函数名）"""
    def deco(func):
        TOOL_REGISTRY[func.__name__] = {"description": description, "func": func}
        return func
    return deco


WEATHER = {"北京": "晴，12~22℃", "上海": "多云，15~21℃"}


@register(description="两数四则运算，op 取 + - * / 之一（除数为 0 会报错）")
def calc(a, b, op):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ValueError("除数不能为 0")
        return a / b
    raise ValueError(f"不支持的运算符'{op}'")


@register(description="查询指定城市当前天气（离线演示表：北京/上海）")
def get_weather(city):
    if city not in WEATHER:
        raise ValueError(f"演示表只有北京/上海，没有'{city}'")
    return f"{city}：{WEATHER[city]}"


@register(description="统计一段文字的字数")
def count_chars(text):
    return len(text)


def call_tool(name, **kwargs):
    """调度一个工具：get 兜底 -> 参数校验（有限重试）-> 执行 -> 错误分类恢复。
    返回 (是否成功, 结果文本, 日志列表)"""
    log = []

    tool = TOOL_REGISTRY.get(name)  # 关键：用 .get，查不到返回 None 走兜底
    if tool is None:
        menu = "；".join(f"{n}（{i['description']}）" for n, i in TOOL_REGISTRY.items())
        log.append(f"[工具缺失] 没有名为'{name}'的工具。现有菜单：{menu}")
        return False, None, log

    for attempt in range(1, MAX_RETRIES + 1):
        log.append(f"[尝试 {attempt}] 调用 {name}，参数：{kwargs}")
        try:
            result = tool["func"](**kwargs)
            log.append(f"[成功] 结果：{result}")
            return True, result, log
        except TypeError as e:  # 参数形状不对：可修正，值得重试
            log.append(f"[参数错] {e}")
            if attempt < MAX_RETRIES:
                fixed = fix_args(name, kwargs)
                if fixed != kwargs:
                    log.append(f"[恢复] 修正参数后重试：{fixed}")
                    kwargs = fixed
                    continue
            log.append("[放弃] 无法自动修正参数，上报用户")
            return False, None, log
        except ValueError as e:  # 业务性失败：重试也没用，换策略
            log.append(f"[工具失败] {e}")
            log.append("[恢复] 不盲目重试，降级处理：把原因告知用户或换其他工具")
            return False, str(e), log

    return False, None, log


def fix_args(name, kwargs):
    """极简参数修正演示：get_weather 缺 city 时补一个默认城市"""
    if name == "get_weather" and "city" not in kwargs:
        return {**kwargs, "city": "北京"}
    return kwargs


def offline_demo():
    print("=" * 60)
    print("Tool Use：注册表 -> get 兜底 -> 有限重试 -> 错误恢复（离线真跑）")
    print("=" * 60)

    menu = "\n".join(f"   - {n}：{i['description']}" for n, i in TOOL_REGISTRY.items())
    print("\n1) 工具菜单（模型就靠这些描述选工具）：")
    print(menu)

    scenes = [
        ("2) 第一幕：调不存在的工具（.get 兜底报菜单）", "book_flight", {"dest": "巴黎"}),
        ("3) 第二幕：除零——业务失败不重试、换策略", "calc", {"a": 10, "b": 0, "op": "/"}),
        ("4) 第三幕：缺参数——修正一次后重试成功", "get_weather", {}),
        ("5) 对照：参数齐全时一把过", "get_weather", {"city": "上海"}),
    ]
    for title, name, kwargs in scenes:
        print(f"\n{title}：")
        _, out, log = call_tool(name, **kwargs)
        for entry in log:
            print("   ", entry)


if __name__ == "__main__":
    offline_demo()
