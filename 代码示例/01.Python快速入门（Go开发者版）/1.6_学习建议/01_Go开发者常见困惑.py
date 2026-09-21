# Go开发者可能写的"Go风格Python"
def process_data(data: list[dict[str, int]]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for item in data:
        key: str = item.get("name", "")
        value: int = item.get("value", 0)
        if key not in result:
            result[key] = []
        result[key].append(value)
    return result

# 更Pythonic的写法
from collections import defaultdict

def process_data(data):
    result = defaultdict(list)
    for item in data:
        result[item.get("name", "")].append(item.get("value", 0))
    return dict(result)
