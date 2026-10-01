# 实际案例：滑动窗口
from collections import deque

def sliding_window_max(nums, k):
    """计算滑动窗口最大值"""
    dq = deque()  # 存储索引
    result = []
    
    for i, num in enumerate(nums):
        # 移除超出窗口的元素
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # 移除比当前元素小的元素（它们永远不会是最大值）
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        
        dq.append(i)
        
        # 记录窗口最大值
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result

print(sliding_window_max([1,3,-1,-3,5,3,6,7], 3))
# 输出: [3, 3, 5, 5, 6, 7]
