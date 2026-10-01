# ============ typing模块常用类型 ============
from typing import List, Dict, Set, Tuple, Optional, Union, Callable, Any

# List - 列表类型
numbers: List[int] = [1, 2, 3, 4, 5]

# Dict - 字典类型
person: Dict[str, Union[str, int]] = {
    "name": "张三",
    "age": 25
}

# Set - 集合类型
unique_ids: Set[int] = {1, 2, 3}

# Tuple - 元组类型
coord: Tuple[int, int] = (10, 20)

# Optional - 可选类型
name: Optional[str] = None    # 可以是str或None
name = "李四"                  # 也可以是str

# Union - 联合类型
result: Union[int, str] = 42   # 可以是int或str
result = "error"               # 也可以是str

# Callable - 可调用类型
def add(a: int, b: int) -> int:
    return a + b

callback: Callable[[int, int], int] = add  # 参数是(int, int)，返回int

# Any - 任意类型
data: Any = "anything"        # 可以是任意类型
data = 123
data = [1, 2, 3]
