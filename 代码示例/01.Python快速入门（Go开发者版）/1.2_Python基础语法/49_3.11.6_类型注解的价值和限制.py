# Python类型注解 vs Go类型声明

# Python: 类型注解可选，运行时不强制
def add(a: int, b: int) -> int:
    return a + b

add("a", "b")  # mypy报错，但运行正常！

# Go: 类型声明强制，编译时检查
# func add(a int, b int) int {
#     return a + b
# }

# add("a", "b")  # 编译错误！
