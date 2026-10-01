def multiply(a: int, b: int) -> int:
    return a * b

# mypy会在编译时发现这个错误
result = multiply("hello", "world")  # Error!
