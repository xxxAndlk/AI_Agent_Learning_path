# 常见mypy错误及修复
# 错误1: 参数类型不匹配
def greet(name: str) -> str:
    return f"Hello, {name}!"

greet(123)  # Error: Argument 1 to "greet" has incompatible type "int"; expected "str"

# 错误2: 返回类型不匹配
def double(x: int) -> int:
    return str(x * 2)  # Error: Incompatible return type: expected "int", got "str"

# 错误3: 联合类型需要类型守卫
def process(value: int | str) -> str:
    # Error: Item "int" of "int | str" has no attribute "upper"
    return value.upper()  # 需要先检查类型

def process_fixed(value: int | str) -> str:
    if isinstance(value, str):
        return value.upper()  # 类型守卫，mypy知道这是str
    return str(value)
