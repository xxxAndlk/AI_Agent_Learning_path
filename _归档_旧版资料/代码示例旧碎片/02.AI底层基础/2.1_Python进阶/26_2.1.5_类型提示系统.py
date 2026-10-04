from typing import (
    TypeVar, Generic, Protocol, Optional,  # 导入类型提示相关类
    Union, Callable, List, Dict, Tuple
)
from dataclasses import dataclass            # 导入数据类装饰器

# ============ 1. 基础类型提示 ============
def greet(name: str) -> str:                 # 参数name是str类型，返回str类型
    """简单的问候函数"""
    return f"Hello, {name}!"

def process_numbers(numbers: List[int]) -> int:
    """处理整数列表，返回总和"""
    return sum(numbers)

def get_config(key: str, default: str = "default") -> str:
    """获取配置值，key为str类型，默认值为str类型，返回str"""
    return default

# ============ 2. 泛型(Generic)实现 ============
T = TypeVar('T')                             # 定义泛型类型变量T
U = TypeVar('U')                             # 定义另一个泛型类型变量U

class Container(Generic[T]):
    """泛型容器类：可存储任意类型的数据"""
    
    def __init__(self, value: T):
        """初始化容器
        
        参数:
            value: T类型的值
        """
        self.value = value                   # 存储值，类型为T
    
    def get(self) -> T:                      # get方法返回T类型
        """获取存储的值"""
        return self.value

class Pair(Generic[T, U]):
    """泛型键值对：存储两个不同类型的值"""
    
    def __init__(self, key: T, value: U):
        self.key = key                       # 键类型为T
        self.value = value                   # 值类型为U
    
    def get_key(self) -> T:
        return self.key
    
    def get_value(self) -> U:
        return self.value

# ============ 3. Protocol(结构子类型) ============
class Drawable(Protocol):
    """可绘制协议：定义draw方法，任何有draw方法的类都视为可绘制"""
    
    def draw(self) -> None:                  # 定义协议方法
        """绘制自身"""

class Circle:
    """圆形类：实现Drawable协议"""
    
    def __init__(self, radius: float):
        self.radius = radius
    
    def draw(self) -> None:
        print(f"绘制圆形，半径: {self.radius}")

class Square:
    """正方形类：实现Drawable协议"""
    
    def __init__(self, side: float):
        self.side = side
    
    def draw(self) -> None:
        print(f"绘制正方形，边长: {self.side}")

def render_shape(shape: Drawable) -> None:   # 接受任何实现Drawable的对象
    """渲染形状"""
    shape.draw()

# ============ 4. dataclass数据类 ============
@dataclass
class Point:
    """二维点数据类：自动生成__init__、__repr__、__eq__等方法"""
    x: float                                 # x坐标，类型为float
    y: float                                 # y坐标，类型为float

@dataclass
class DataPoint:
    """带默认值的数据点"""
    x: float = 0.0                           # 默认值
    y: float = 0.0
    label: str = "unknown"                   # 标签，默认为"unknown"

@dataclass
class TensorInfo:
    """张量信息数据类：用于AI框架"""
    shape: Tuple[int, ...]                   # 形状，如(batch, channels, height, width)
    dtype: str = "float32"                   # 数据类型
    device: str = "cpu"                      # 设备

# ============ 5. 复杂类型提示 ============
# Union: 联合类型（Python 3.10+可用 int | str 替代）
def process(value: Union[int, str]) -> str:
    """处理整数或字符串"""
    return str(value)

# Optional: 可选类型（等价于Union[Type, None]）
def find_user(user_id: int) -> Optional[Dict[str, str]]:
    """查找用户，返回用户字典或None"""
    if user_id > 0:
        return {"id": str(user_id), "name": "User"}
    return None

# Callable: 可调用类型
def apply_operation(
    func: Callable[[int, int], int],         # 接收两个int参数，返回int的函数
    a: int, 
    b: int
) -> int:
    """应用操作函数"""
    return func(a, b)

# ============ 主程序入口 ============
if __name__ == "__main__":
    # 使用泛型容器
    int_container = Container(42)            # Container[int]
    str_container = Container("hello")       # Container[str]
    print(f"容器值: {int_container.get()}, {str_container.get()}")
    
    # 使用键值对
    pair = Pair("accuracy", 0.95)            # Pair[str, float]
    print(f"键: {pair.get_key()}, 值: {pair.get_value()}")
    
    # 使用Protocol
    circle = Circle(5.0)
    square = Square(10.0)
    render_shape(circle)                     # Circle实现Drawable协议
    render_shape(square)                     # Square实现Drawable协议
    
    # 使用dataclass
    point = Point(3.0, 4.0)
    print(f"点: {point}")                    # 自动生成__repr__
    
    data_point = DataPoint(x=1.5, label="训练数据")
    print(f"数据点: {data_point}")
    
    tensor_info = TensorInfo(shape=(32, 3, 224, 224))
    print(f"张量信息: {tensor_info}")
    
    # 使用Callable
    result = apply_operation(lambda x, y: x + y, 3, 5)
    print(f"操作结果: {result}")
