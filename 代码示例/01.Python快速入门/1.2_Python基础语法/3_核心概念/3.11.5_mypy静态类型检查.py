# ============ mypy使用示例 ============

# 准备一个带类型注解的文件 example.py
"""
# example.py
from typing import List, Dict, Optional

def process_data(data: List[int]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for i, num in enumerate(data):
        result[f"item_{i}"] = num * 2
    return result

def get_value(d: Dict[str, int], key: str) -> int:
    return d[key]  # 可能抛出KeyError

def safe_get_value(d: Dict[str, int], key: str) -> Optional[int]:
    return d.get(key)  # 安全访问
"""

# 运行mypy检查
# mypy example.py

# 类型错误示例（mypy会报错）
def add_numbers(a: int, b: int) -> int:
    return a + b

result = add_numbers("hello", "world")  # mypy: error: Argument 1 to "add_numbers" has incompatible type "str"; expected "int"

# 更多示例
def calculate(a: int, b: int) -> int:
    return a + b

# 正确使用
x = calculate(10, 20)    # mypy: OK

# 错误使用（mypy会检测）
y = calculate([1, 2], [3, 4])  # mypy: error
z = calculate("a", "b")        # mypy: error
