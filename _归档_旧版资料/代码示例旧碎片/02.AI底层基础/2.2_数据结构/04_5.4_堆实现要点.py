# Python heapq使用技巧
import heapq

# 大顶堆（存储负数）
class MaxHeap:
    def __init__(self):
        self.data = []
    
    def push(self, val):
        heapq.heappush(self.data, -val)
    
    def pop(self):
        return -heapq.heappop(self.data)
    
    def peek(self):
        return -self.data[0] if self.data else None

# TopK问题
def top_k(nums, k):
    """使用小顶堆找最大的K个元素"""
    heap = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap
