# 重构时mypy会告诉你哪里需要更新
def process(data: List[Dict[str, int]]) -> List[int]:
    return [item["value"] for item in data]
