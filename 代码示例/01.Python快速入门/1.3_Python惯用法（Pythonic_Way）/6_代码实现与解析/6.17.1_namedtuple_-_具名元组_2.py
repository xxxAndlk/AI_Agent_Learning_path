# 实际案例：函数返回坐标
from collections import namedtuple

Result = namedtuple('Result', ['x', 'y', 'status'])

def find_peak(heights):
    # 假设找到峰值位置
    return Result(x=5, y=100, status="found")

result = find_peak([1,3,5,3,1])
print(f"峰值位置: ({result.x}, {result.y})")
