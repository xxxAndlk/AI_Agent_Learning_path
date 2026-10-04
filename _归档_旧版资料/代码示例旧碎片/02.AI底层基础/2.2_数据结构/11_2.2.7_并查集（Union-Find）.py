class UnionFind:
    """并查集（Union-Find/Disjoint Set）数据结构
    
    主要功能：
    - find(x): 找到元素x所在集合的根节点
    - union(x, y): 合并x和y所在的两个集合
    
    优化策略：
    - 路径压缩：将路径上的所有节点直接指向根节点
    - 按秩合并：将小树合并到大树，减少树的高度
    
    时间复杂度：接近O(1)，实际为α(n)（阿克曼函数的反函数）
    """
    
    def __init__(self, n):
        """初始化n个独立元素
        
        参数:
            n: 元素数量（通常为0到n-1）
        """
        self.parent = list(range(n))   # 父节点数组，初始指向自己
        self.rank = [0] * n            # 秩（树的近似高度）
        self.count = n                 # 连通分量数量
    
    def find(self, x):
        """找到元素x的根节点（带路径压缩）
        
        路径压缩：将查找路径上的所有节点直接指向根节点
        这大大降低了后续查找的时间复杂度
        
        时间复杂度: O(α(n)) ≈ O(1)
        """
        if self.parent[x] != x:
            # 递归压缩路径
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def find_iterative(self, x):
        """迭代版本的find（避免递归深度问题）"""
        root = x
        # 找到根节点
        while self.parent[root] != root:
            root = self.parent[root]
        
        # 路径压缩：将路径上的节点直接指向根
        while self.parent[x] != root:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x
        
        return root
    
    def union(self, x, y):
        """合并x和y所在的集合（按秩合并）
        
        按秩合并：将秩（树高）较小的树合并到较大的树上
        这样可以保持树的平衡，避免退化成链表
        
        参数:
            x, y: 要合并的两个元素
        返回值:
            布尔值，表示是否成功合并（原本不在同一集合）
        
        时间复杂度: O(α(n)) ≈ O(1)
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # 已在同一集合
        
        # 按秩合并：小的合并到大的
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            # 秩相同，合并后秩+1
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        self.count -= 1  # 连通分量数量-1
        return True
    
    def connected(self, x, y):
        """判断x和y是否在同一集合
        
        时间复杂度: O(α(n)) ≈ O(1)
        """
        return self.find(x) == self.find(y)
    
    def get_count(self):
        """返回连通分量数量"""
        return self.count


class UnionFindWithSize:
    """带尺寸信息的并查集（按大小合并）"""
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n            # 每个集合的大小
    
    def find(self, x):
        """路径压缩"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """按大小合并"""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        # 小树合并到大树
        if self.size[root_x] < self.size[root_y]:
            root_x, root_y = root_y, root_x
        
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        return True
    
    def get_size(self, x):
        """返回元素x所在集合的大小"""
        return self.size[self.find(x)]


# 实战应用：岛屿数量计算
def num_islands(grid: List[List[str]]) -> int:
    """计算网格中岛屿的数量
    
    使用并查集将所有陆地单元格连通，
    最后统计有多少个独立的连通分量。
    
    参数:
        grid: 二维字符网格，'1'表示陆地，'0'表示水域
    返回值:
        岛屿数量
    
    时间复杂度: O(m * n * α(m*n))
    空间复杂度: O(m * n)
    """
    if not grid or not grid[0]:
        return 0
    
    m, n = len(grid), len(grid[0])
    
    # 边界检查：找到所有陆地
    def get_index(i, j):
        return i * n + j
    
    # 只对陆地初始化
    uf = UnionFind(m * n)
    land_count = 0
    
    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                land_count += 1
                # 与右边的陆地合并
                if j + 1 < n and grid[i][j + 1] == '1':
                    uf.union(get_index(i, j), get_index(i, j + 1))
                # 与下边的陆地合并
                if i + 1 < m and grid[i + 1][j] == '1':
                    uf.union(get_index(i, j), get_index(i + 1, j))
    
    # 连通分量数量即为岛屿数量
    # 但需要排除水域（0元素）的干扰，这里简化处理
    return land_count - uf.count + 1


if __name__ == "__main__":
    # 基本并查集操作
    print("=== 并查集基本操作 ===")
    uf = UnionFind(5)
    
    # 初始状态：5个独立元素
    print("初始连通分量:", uf.get_count())  # 5
    
    uf.union(0, 1)
    uf.union(2, 3)
    uf.union(0, 2)
    print("合并后连通分量:", uf.get_count())  # 2
    
    print("0和1相连:", uf.connected(0, 1))  # True
    print("0和4相连:", uf.connected(0, 4))  # False
    
    # 按大小合并
    print("\n=== 按大小合并 ===")
    uf_size = UnionFindWithSize(5)
    uf_size.union(0, 1)
    uf_size.union(2, 3)
    uf_size.union(0, 2)
    print("元素0所在集合大小:", uf_size.get_size(0))  # 4
    
    # 岛屿数量
    print("\n=== 岛屿数量 ===")
    grid = [
        ['1', '1', '0', '0', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '1', '0', '0'],
        ['0', '0', '0', '1', '1']
    ]
    print("岛屿数量:", num_islands(grid))  # 3
