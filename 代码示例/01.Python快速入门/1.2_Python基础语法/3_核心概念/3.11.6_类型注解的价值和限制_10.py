

# 类型注解可选，运行时不强制
def add(a: int, b: int) -> int:
    return a + b

add("a", "b")  # mypy报错，但运行正常！

#     return a + b
# }

# add("a", "b")  # 编译错误！
