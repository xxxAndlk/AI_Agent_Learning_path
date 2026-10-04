class DListNode:
    """双向链表节点
    
    用于实现LRU缓存淘汰策略
    """
    def __init__(self, key=0, value=0):
        self.key = key                 # 存储键（用于删除时从哈希表移除）
        self.value = value             # 存储值
        self.prev = None               # 前驱节点
        self.next = None               # 后继节点


class LRUCache:
    """LRU缓存（最近最少使用）手动实现
    
    设计原理：
    - 使用双向链表维护访问顺序：头部是最久未使用的，尾部是最近使用的
    - 使用哈希表存储键到节点的映射，实现O(1)时间复杂度的查找
    
    操作：
    - get(key): 访问元素，移动到尾部，返回值
    - put(key, value): 插入/更新元素，可能淘汰头部
    
    时间复杂度: O(1)
    空间复杂度: O(capacity)
    
    AI应用：
    - 神经网络激活值缓存
    - KV缓存（Transformer）
    - 特征缓存
    - 模型推理缓存
    """
    
    def __init__(self, capacity: int):
        """初始化LRU缓存
        
        参数:
            capacity: 缓存容量（最大存储的键值对数量）
        """
        self.capacity = capacity        # 缓存容量
        self.cache = {}                 # 哈希表：key -> DListNode
        
        # 虚拟头尾节点（简化边界处理）
        self.head = DListNode()         # 头节点（最久未使用）
        self.tail = DListNode()         # 尾节点（最近使用）
        self.head.next = self.tail      # 初始化连接
        self.tail.prev = self.head
    
    def _remove(self, node: DListNode):
        """删除节点（从双向链表中移除）
        
        时间复杂度: O(1)
        """
        node.prev.next = node.next      # 前节点指向后节点
        node.next.prev = node.prev      # 后节点指向前节点
    
    def _add_to_tail(self, node: DListNode):
        """将节点添加到尾部（最近使用位置）
        
        时间复杂度: O(1)
        """
        node.prev = self.tail.prev      # 新节点前驱指向原尾部前驱
        node.next = self.tail           # 新节点后继指向尾节点
        self.tail.prev.next = node      # 原尾部后继指向新节点
        self.tail.prev = node           # 尾节点前驱指向新节点
    
    def _move_to_tail(self, node: DListNode):
        """将已有节点移动到尾部（标记为最近使用）
        
        时间复杂度: O(1)
        """
        self._remove(node)              # 先从原位置删除
        self._add_to_tail(node)         # 再添加到尾部
    
    def get(self, key: int) -> int:
        """获取缓存中的值
        
        参数:
            key: 要查找的键
        返回值:
            键对应的值，如果不存在返回-1
        
        时间复杂度: O(1)
        """
        if key not in self.cache:
            return -1                   # 键不存在
        
        node = self.cache[key]          # 从哈希表获取节点
        self._move_to_tail(node)        # 移动到尾部（最近使用）
        return node.value               # 返回值
    
    def put(self, key: int, value: int):
        """插入或更新键值对
        
        参数:
            key: 键
            value: 值
        
        时间复杂度: O(1)
        """
        if key in self.cache:
            # 键已存在：更新值并移动到尾部
            node = self.cache[key]
            node.value = value
            self._move_to_tail(node)
        else:
            # 键不存在：创建新节点
            node = DListNode(key, value)
            self.cache[key] = node       # 哈希表添加
            self._add_to_tail(node)      # 链表添加
            
            # 检查容量，超出则淘汰最久未使用的
            if len(self.cache) > self.capacity:
                # 淘汰头部节点（最久未使用）
                removed_node = self.head.next
                self._remove(removed_node)
                del self.cache[removed_node.key]
    
    def print_cache(self):
        """打印缓存内容（用于调试）"""
        print("Cache content (head -> tail):")
        current = self.head.next
        items = []
        while current != self.tail:
            items.append(f"({current.key}:{current.value})")
            current = current.next
        print(" <-> ".join(items) if items else "(empty)")


# 使用Python OrderedDict的简洁实现（了解原理后推荐使用）
from collections import OrderedDict


class LRUCacheOrderedDict:
    """使用OrderedDict的LRU缓存实现
    
    OrderedDict内部维护了插入顺序，
    move_to_end()可以将元素移到末尾，
    popitem(last=False)可以删除最前面的元素。
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # 移到末尾表示最近使用
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # 超过容量删除最旧的
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 删除最前面的


# 实战：Transformer KV缓存模拟
class KVCache:
    """模拟Transformer的Key-Value缓存
    
    在自注意力机制中，需要缓存之前位置的K和V向量
    以避免重复计算，提高推理效率
    """
    
    def __init__(self, max_length: int = 512):
        self.max_length = max_length
        self.k_cache = []               # 存储key向量序列
        self.v_cache = []               # 存储value向量序列
    
    def append(self, k_vec, v_vec):
        """追加新的key-value对
        
        参数:
            k_vec: 新的key向量
            v_vec: 新的value向量
        """
        # 使用LRU策略管理缓存长度
        if len(self.k_cache) >= self.max_length:
            self.k_cache.pop(0)         # 淘汰最旧的
            self.v_cache.pop(0)
        
        self.k_cache.append(k_vec)
        self.v_cache.append(v_vec)
    
    def get_cache(self):
        """获取当前所有缓存的KV"""
        return self.k_cache, self.v_cache
    
    def clear(self):
        """清空缓存"""
        self.k_cache = []
        self.v_cache = []


if __name__ == "__main__":
    # 手动实现测试
    print("=== 手动实现LRU缓存 ===")
    cache = LRUCache(3)                 # 容量为3
    
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    print("初始状态:")
    cache.print_cache()                 # 1<->2<->3
    
    print(f"\nget(1) = {cache.get(1)}")  # 1，1移到尾部
    print("访问1后:")
    cache.print_cache()                 # 2<->3<->1
    
    cache.put(4, 4)                     # 插入4，淘汰2
    print("插入4后:")
    cache.print_cache()                 # 3<->1<->4
    
    print(f"get(2) = {cache.get(2)}")   # -1（已被淘汰）
    
    # OrderedDict版本测试
    print("\n=== OrderedDict实现 ===")
    cache2 = LRUCacheOrderedDict(2)
    cache2.put(1, 1)
    cache2.put(2, 2)
    print(f"get(1) = {cache2.get(1)}")
    cache2.put(3, 3)
    print(f"get(2) = {cache2.get(2)}")  # -1
    
    # KV缓存测试
    print("\n=== Transformer KV缓存 ===")
    kv = KVCache(max_length=3)
    for i in range(5):
        kv.append(f"k_{i}", f"v_{i}")
        k, v = kv.get_cache()
        print(f"Step {i}: keys = {k}")
