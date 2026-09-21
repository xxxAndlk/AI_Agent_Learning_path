# Python 3.9之前的泛型语法不同
# Python 3.9+:
def process(items: list[int]) -> list[int]:
    return items

# Python 3.8及以下:
from typing import List

def process_legacy(items: List[int]) -> List[int]:  # 需要typing.List
    return items
