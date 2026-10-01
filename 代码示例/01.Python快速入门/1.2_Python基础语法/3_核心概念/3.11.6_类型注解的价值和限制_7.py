# 动态类型特性无法完全静态化
from typing import Any

def dynamic(value: Any) -> Any:
    return value  # Any绕过了类型检查
