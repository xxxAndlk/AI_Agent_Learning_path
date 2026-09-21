from typing import Dict, List, Union

# 推荐：逐步添加类型注解
# 1. 新代码使用类型注解
def new_function(x: int, y: int) -> int:
    return x + y

# 2. 公共API使用类型注解
def api_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "ok"}

# 3. 复杂逻辑使用类型注解
def process_items(items: List[Dict[str, Union[int, str]]]) -> List[int]:
    return [int(v) for item in items for v in item.values() if isinstance(v, int)]

# 4. 内部实现可省略
def internal_helper(data):
    """内部函数可以省略类型"""
    return [x * 2 for x in data]

# 5. 使用# type: ignore忽略无法解决的类型问题
result = some_dynamic_call()  # type: ignore  # 忽略类型检查
