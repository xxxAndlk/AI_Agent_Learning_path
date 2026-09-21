from collections import deque
import heapq


class Queue:
    """队列类：先进先出（FIFO）的数据结构
    
    队列是一种受限的线性表，只允许在一端（队尾）插入，
    在另一端（队头）删除。
    """
    
    def __init__(self):
        """初始化空队列"""
        self.items = []                # 使用Python列表存储队列元素
    
    def is_empty(self):
        """判断队列是否为空"""
        return len(self.items) == 0
    
    def enqueue(self, item):
        """入队：将元素添加到队尾
        
        时间复杂度: O(1)
        """
        self.items.append(item)        # 列表末尾添加
    
    def dequeue(self):
        """出队：移除并返回队头元素
        
        时间复杂度: O(n)，列表头部删除需要移动元素
        优化：使用collections.deque实现O(1)出队
        """
        if self.is_empty():
            return None
        return self.items.pop(0)       # 移除并返回列表头部
    
    def front(self):
        """查看队头元素但不移除"""
        return self.items[0] if self.items else None
    
    def size(self):
        """返回队列大小"""
        return len(self.items)


class DequeDemo:
    """双端队列（Deque）演示
    
    双端队列允许在两端 O(1) 时间复杂度内进行插入和删除操作。
    常见用途：滑动窗口、LRU缓存、单调队列等。
    """
    
    def __init__(self):
        """初始化空双端队列"""
        self.deque = deque()           # 使用collections.deque
    
    def max_sliding_window(self, nums, k):
        """滑动窗口最大值：使用单调递减双端队列
        
        核心思想：
        - 维护一个存储索引的双端队列
        - 队列中的元素保持递减（队头是当前窗口最大值）
        - 队头索引超出窗口范围时移除
        
        参数:
            nums: 输入数组
            k: 窗口大小
        返回值:
            每个窗口的最大值列表
        
        时间复杂度: O(n)，每个元素最多入队和出队一次
        空间复杂度: O(k)
        
        AI应用：
        - 神经网络激活值峰值监控
        - 时序数据的滑动统计
        """
        if not nums or k == 0:
            return []
        
        result = []                    # 存储结果
        window = deque()               # 存储索引，保持递减
        
        for i, num in enumerate(nums):
            # 移除超出窗口范围的索引
            if window and window[0] <= i - k:
                window.popleft()
            
            # 移除比当前元素小的索引（不可能成为最大值）
            while window and nums[window[-1]] < num:
                window.pop()
            
            window.append(i)           # 当前元素入队
            
            # 窗口形成后开始记录最大值
            if i >= k - 1:
                result.append(nums[window[0]])
        
        return result


class PriorityQueue:
    """优先队列类：元素按优先级出队
    
    Python的heapq实现的是小顶堆（最小元素先出队）。
    如果需要大顶堆，可以存储元素的负数。
    
    时间复杂度：
    - push: O(log n)
    - pop: O(log n)
    - peek: O(1)
    
    AI应用：
    - A*寻路算法
    - Top-K采样
    - 事件驱动模拟
    """
    
    def __init__(self, reverse=False):
        """初始化优先队列
        
        参数:
            reverse: True表示大顶堆（值大的优先），False表示小顶堆
        """
        self.heap = []                 # 存储元素的列表
        self.reverse = reverse         # 是否反转（实现大顶堆）
    
    def push(self, item, priority=0):
        """入队：添加元素及其优先级
        
        参数:
            item: 要添加的元素
            priority: 优先级（值越小越先出队，除非reverse=True）
        """
        # 存储(优先级, 元素)的元组
        if self.reverse:
            # 大顶堆：存储负优先级
            heapq.heappush(self.heap, (-priority, item))
        else:
            heapq.heappush(self.heap, (priority, item))
    
    def pop(self):
        """出队：移除并返回优先级最高（值最小）的元素"""
        if not self.heap:
            return None
        priority, item = heapq.heappop(self.heap)
        return item
    
    def peek(self):
        """查看队头元素但不移除"""
        if not self.heap:
            return None
        return self.heap[0][1]
    
    def size(self):
        """返回队列大小"""
        return len(self.heap)


# BFS模板：广度优先搜索
def bfs(graph, start):
    """广度优先搜索模板
    
    参数:
        graph: 邻接表表示的图
        start: 起始节点
    返回值:
        从start可达的所有节点
    
    时间复杂度: O(V + E)，V为顶点数，E为边数
    空间复杂度: O(V)
    """
    visited = set([start])            # 标记已访问节点
    queue = deque([start])            # 使用双端队列作为队列
    result = []                       # 存储遍历结果
    
    while queue:
        node = queue.popleft()        # 队头出队
        result.append(node)
        
        # 遍历邻居节点
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)  # 邻居入队
    
    return result


if __name__ == "__main__":
    # 基本队列操作
    queue = Queue()
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    print("队头元素:", queue.front()) # 1
    print("出队元素:", queue.dequeue())# 1
    print("队列大小:", queue.size())  # 2
    
    # 滑动窗口最大値
    nums = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    deque_demo = DequeDemo()
    result = deque_demo.max_sliding_window(nums, k)
    print(f"滑动窗口最大值 (k={k}):", result)  # [3, 3, 5, 5, 6, 7]
    
    # 优先队列
    pq = PriorityQueue()
    pq.push("任务A", priority=3)
    pq.push("任务B", priority=1)
    pq.push("任务C", priority=2)
    print("优先队列弹出:", pq.pop())  # 任务B
    print("优先队列弹出:", pq.pop())  # 任务C
    
    # 大顶堆优先队列
    max_pq = PriorityQueue(reverse=True)
    max_pq.push("高优先级任务", priority=10)
    max_pq.push("低优先级任务", priority=1)
    print("大顶堆弹出:", max_pq.pop())  # 高优先级任务
    
    # BFS示例
    graph = {
        'A': ['B', 'C'],
        'B': ['D', 'E'],
        'C': ['F'],
        'D': [],
        'E': ['F'],
        'F': []
    }
    print("BFS遍历:", bfs(graph, 'A'))  # ['A', 'B', 'C', 'D', 'E', 'F']
