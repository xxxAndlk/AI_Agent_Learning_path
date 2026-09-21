import heapq                        # 导入堆操作库，提供小顶堆实现

class HashTable:
    """哈希表类：使用链地址法解决冲突"""
    def __init__(self, size=100):
        """初始化哈希表
        
        参数:
            size: 哈希表的大小（桶的数量）
        """
        self.size = size              # 哈希表大小
        # 创建size个空列表，每个列表是一个桶（用于解决哈希冲突）
        self.table = [[] for _ in range(size)]
    
    def _hash(self, key):
        """私有方法：计算键的哈希值
        
        使用Python内置hash函数，然后取模映射到表的索引范围
        """
        return hash(key) % self.size  # hash()计算哈希值，%取模映射到[0, size-1]
    
    def put(self, key, value):
        """向哈希表中插入或更新键值对"""
        hash_key = self._hash(key)    # 计算键的哈希值（桶索引）
        # 遍历该桶，检查键是否已存在
        for item in self.table[hash_key]:
            if item[0] == key:        # 如果键已存在
                item[1] = value       # 更新值
                return                # 结束函数
        # 键不存在，添加到桶的末尾
        self.table[hash_key].append([key, value])
    
    def get(self, key):
        """根据键获取值"""
        hash_key = self._hash(key)    # 计算哈希值
        # 在对应桶中查找键
        for item in self.table[hash_key]:
            if item[0] == key:        # 找到键
                return item[1]        # 返回值
        return None                   # 键不存在返回None
    
    def remove(self, key):
        """删除键值对"""
        hash_key = self._hash(key)    # 计算哈希值
        # 遍历桶查找键
        for i, item in enumerate(self.table[hash_key]):
            if item[0] == key:        # 找到键
                del self.table[hash_key][i]  # 删除该键值对
                return True           # 删除成功
        return False                  # 键不存在

def heap_example():
    """堆操作示例函数"""
    # ========== 小顶堆示例 ==========
    min_heap = []                     # 初始化空堆
    heapq.heappush(min_heap, 3)       # 推入3，堆: [3]
    heapq.heappush(min_heap, 1)       # 推入1，堆会调整，堆: [1, 3]
    heapq.heappush(min_heap, 2)       # 推入2，堆: [1, 3, 2]
    # heappop弹出最小值，堆会自动调整保持性质
    print("小顶堆弹出:", heapq.heappop(min_heap))  # 输出1
    
    # ========== 大顶堆示例 ==========
    # Python的heapq只支持小顶堆，通过存储负数模拟大顶堆
    max_heap = []
    heapq.heappush(max_heap, -3)      # 存储-3
    heapq.heappush(max_heap, -1)      # 存储-1
    heapq.heappush(max_heap, -2)      # 存储-2
    # 弹出最小负数（即最大正数的负数），再取负还原
    print("大顶堆弹出:", -heapq.heappop(max_heap))  # 输出3

if __name__ == "__main__":
    # 哈希表示例
    ht = HashTable()
    ht.put("name", "AI工程师")         # 插入键值对
    ht.put("age", 25)
    print("哈希表获取name:", ht.get("name"))  # AI工程师
    print("哈希表获取age:", ht.get("age"))    # 25
    ht.remove("age")                  # 删除键
    print("哈希表删除后获取age:", ht.get("age"))  # None
    
    heap_example()                    # 运行堆示例

#### 2.2.4 栈（Stack）
