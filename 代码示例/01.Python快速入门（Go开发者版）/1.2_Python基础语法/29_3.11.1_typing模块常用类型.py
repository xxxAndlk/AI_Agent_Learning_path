# ============ typing模块常用类型 ============
from typing import List, Dict, Set, Tuple, Optional, Union, Callable, Any

# List - 列表类型（类似Go的 []int）
# Go: []int
numbers: List[int] = [1, 2, 3, 4, 5]

# Dict - 字典类型（类似Go的 map[string]int）
# Go: map[string]int
person: Dict[str, Union[str, int]] = {
    "name": "张三",
    "age": 25
}

# Set - 集合类型（类似Go的 map[T]struct{}）
# Go: map[string]struct{}
unique_ids: Set[int] = {1, 2, 3}

# Tuple - 元组类型（类似Go的 struct）
# Go: struct { Name string; Age int }
coord: Tuple[int, int] = (10, 20)

# Optional - 可选类型（类似Go的 *T 或空接口）
# Go: *string 或 interface{}
name: Optional[str] = None    # 可以是str或None
name = "李四"                  # 也可以是str

# Union - 联合类型（类似Go的 interface{} 或类型分支）
# Go: interface{}
result: Union[int, str] = 42   # 可以是int或str
result = "error"               # 也可以是str

# Callable - 可调用类型（类似Go的函数类型）
# Go: func(int, int) int
def add(a: int, b: int) -> int:
    return a + b

callback: Callable[[int, int], int] = add  # 参数是(int, int)，返回int

# Any - 任意类型（类似Go的 interface{}）
# Go: interface{}
data: Any = "anything"        # 可以是任意类型
data = 123
data = [1, 2, 3]
