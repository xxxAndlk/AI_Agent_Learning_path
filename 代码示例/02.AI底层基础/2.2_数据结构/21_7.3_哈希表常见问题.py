def two_sum(nums, target):
    """使用哈希表O(n)时间复杂度"""
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
