# 动态类型意味着类型在运行时确定
x = 1           # x是int
x = "hello"     # x现在是str
x = [1, 2, 3]   # x现在是list

# 但仍应使用类型提示
from typing import List, Dict, Optional

def greet(name: str, times: int = 1) -> str:
    return name * times

def find_user(user_id: int) -> Optional[Dict[str, any]]:
    # 返回dict或None
    pass
