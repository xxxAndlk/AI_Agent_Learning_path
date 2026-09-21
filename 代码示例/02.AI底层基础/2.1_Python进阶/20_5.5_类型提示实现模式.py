# 基础类型提示
def greet(name: str) -> str:
    return f"Hello, {name}!"

# 泛型类型
from typing import TypeVar, Generic
T = TypeVar('T')
def first_element(items: list[T]) -> T:
    return items[0]

# Protocol定义接口
from typing import Protocol
class Drawable(Protocol):
    def draw(self) -> None: ...

# dataclass数据类
from dataclasses import dataclass
@dataclass
class Point:
    x: float
    y: float
