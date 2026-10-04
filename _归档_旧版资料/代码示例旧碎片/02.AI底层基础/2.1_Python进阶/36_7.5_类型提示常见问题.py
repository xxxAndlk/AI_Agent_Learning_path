# 问题：过度使用Protocol
# Protocol用于结构子类型，继承用于行为复用
# 不要滥用Protocol

# 正确使用：
class Drawable(Protocol):
    def draw(self) -> None: ...

# 继承用于共享实现：
class Shape:
    def draw(self) -> None:
        raise NotImplementedError
