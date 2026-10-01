# Python解释器完全忽略类型注解
def foo(x: int) -> str:
    return x  # 运行时返回int，但声明返回str
