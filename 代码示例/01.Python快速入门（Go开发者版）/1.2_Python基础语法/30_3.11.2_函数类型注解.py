# ============ 函数类型注解 ============

# 基本函数类型注解（类似Go的 func add(a int, b int) int）
def greet(name: str) -> str:           # 参数name是str，返回str
    return f"你好, {name}!"

# 多个参数（类似Go的多参数）
def add(a: int, b: int) -> int:
    return a + b

# 无返回值（类似Go的 func foo()）
def print_message(message: str) -> None:  # -> None 表示无返回值
    print(message)

# 多返回值（Go原生支持，Python用Tuple模拟）
def divide(a: float, b: float) -> Tuple[float, Optional[str]]:
    """返回除法结果和可能的错误信息"""
    if b == 0:
        return 0.0, "除数不能为零"
    return a / b, None

# 可变参数（类似Go的 ...int）
def sum_all(*numbers: int) -> int:    # *numbers收集为tuple[int, ...]
    return sum(numbers)

# 关键字参数（Go不支持）
def create_user(name: str, age: int, **kwargs: str) -> Dict[str, Any]:
    """**kwargs收集为Dict[str, str]"""
    user = {"name": name, "age": age}
    user.update(kwargs)
    return user

# 使用示例
result = divide(10, 2)           # result: Tuple[float, Optional[str]]
value, error = result
if error:
    print(f"错误: {error}")
else:
    print(f"结果: {value}")       # 输出: 5.0

total = sum_all(1, 2, 3, 4, 5)   # total: int
user = create_user("张三", 25, city="北京", email="zs@example.com")
