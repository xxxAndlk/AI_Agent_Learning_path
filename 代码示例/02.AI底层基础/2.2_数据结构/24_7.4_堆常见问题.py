import heapq

class MedianFinder:
    """使用两个堆维护中位数"""
    def __init__(self):
        self.small = []  # 大顶堆（存较小的一半）
        self.large = []  # 小顶堆（存较大的一半）
    
    def addNum(self, num):
        if len(self.small) == len(self.large):
            heapq.heappush(self.large, -heapq.heappushpop(self.small, -num))
        else:
            heapq.heappush(self.small, -heapq.heappushpop(self.large, num))
    
    def findMedian(self):
        if len(self.small) == len(self.large):
            return (-self.small[0] + self.large[0]) / 2
        return self.large[0]
