# Python 3.12+ 原生类型参数语法
def first[T](items: list[T]) -> T | None:
    """返回列表的第一个元素，Go开发者应该感到很眼熟"""
    return items[0] if items else None

def map_func[T, U](items: list[T], func: callable[[T], U]) -> list[U]:
    """泛型映射函数，类似于Go的泛型"""
    return [func(item) for item in items]

# 使用示例
numbers = [1, 2, 3]
strings = ["a", "b", "c"]

result1 = first(numbers)           # 类型推断为 int | None
result2 = first(strings)           # 类型推断为 str | None
result3 = map_func(numbers, lambda x: x * 2)  # list[int]
result4 = map_func(strings, str.upper)        # list[str]

# 类型参数还支持约束（类似Go的接口约束）
from typing import TypeVar

# 使用 TypeVar 兼容旧代码
T = TypeVar('T')
U = TypeVar('U', bound=int)  # 约束为 int 的子类
