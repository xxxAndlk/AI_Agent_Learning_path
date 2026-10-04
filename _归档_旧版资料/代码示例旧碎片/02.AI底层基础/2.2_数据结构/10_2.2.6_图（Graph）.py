from collections import deque
from typing import List, Dict, Set, Optional


class GraphAdjacencyList:
    """图的邻接表表示
    
    邻接表：为每个顶点维护一个列表，存储其相邻顶点
    适用场景：稀疏图（边数远小于顶点数平方）
    
    空间复杂度: O(V + E)
    """
    
    def __init__(self):
        """初始化空图"""
        self.adj = {}                  # 字典，键为顶点，值为邻接列表
    
    def add_vertex(self, v):
        """添加顶点"""
        if v not in self.adj:
            self.adj[v] = []
    
    def add_edge(self, v1, v2, directed=False):
        """添加边
        
        参数:
            v1, v2: 要连接的两个顶点
            directed: 是否为有向图
        """
        self.add_vertex(v1)
        self.add_vertex(v2)
        self.adj[v1].append(v2)
        if not directed:
            self.adj[v2].append(v1)
    
    def bfs(self, start) -> List:
        """广度优先搜索（BFS）
        
        适用场景：最短路径、层次遍历、连通性检测
        
        时间复杂度: O(V + E)
        空间复杂度: O(V)
        """
        if start not in self.adj:
            return []
        
        visited = set([start])
        queue = deque([start])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    def dfs(self, start) -> List:
        """深度优先搜索（DFS）
        
        适用场景：拓扑排序、连通分量、路径搜索
        
        时间复杂度: O(V + E)
        空间复杂度: O(V)
        """
        visited = set()
        result = []
        
        def dfs_helper(node):
            if node in visited:
                return
            visited.add(node)
            result.append(node)
            for neighbor in self.adj.get(node, []):
                dfs_helper(neighbor)
        
        dfs_helper(start)
        return result


class GraphAdjacencyMatrix:
    """图的邻接矩阵表示
    
    适用场景：稠密图、需要快速判断两点是否相邻
    优点：O(1)判断两点是否相连
    缺点：空间复杂度O(V^2)
    
    空间复杂度: O(V^2)
    """
    
    def __init__(self, n):
        """初始化n个顶点的图"""
        self.n = n                     # 顶点数
        # 创建n x n矩阵，初始化为0（无边）
        self.matrix = [[0] * n for _ in range(n)]
        self.vertex_map = {}           # 顶点到索引的映射
        self.index_map = {}            # 索引到顶点的映射
    
    def add_vertex(self, v):
        """添加顶点"""
        if v not in self.vertex_map:
            idx = len(self.vertex_map)
            self.vertex_map[v] = idx
            self.index_map[idx] = v
    
    def add_edge(self, v1, v2, weight=1):
        """添加边（带权重）"""
        self.add_vertex(v1)
        self.add_vertex(v2)
        idx1 = self.vertex_map[v1]
        idx2 = self.vertex_map[v2]
        self.matrix[idx1][idx2] = weight
        self.matrix[idx2][idx1] = weight  # 无向图
    
    def has_edge(self, v1, v2) -> bool:
        """判断两点是否有边"""
        if v1 not in self.vertex_map or v2 not in self.vertex_map:
            return False
        return self.matrix[self.vertex_map[v1]][self.vertex_map[v2]] > 0


class TopologicalSort:
    """拓扑排序算法
    
    适用场景：任务调度、依赖排序、课程安排
    要求：图必须是有向无环图（DAG）
    
    算法：Kahn算法（基于BFS+入度计数）
    """
    
    def __init__(self):
        self.graph = {}                # 邻接表
        self.in_degree = {}            # 入度表
    
    def add_edge(self, from_node, to_node):
        """添加有向边 from -> to"""
        if from_node not in self.graph:
            self.graph[from_node] = []
        if to_node not in self.in_degree:
            self.in_degree[to_node] = 0
        
        self.graph[from_node].append(to_node)
        self.in_degree[from_node] = self.in_degree.get(from_node, 0)
        self.in_degree[to_node] += 1
    
    def sort(self) -> Optional[List]:
        """执行拓扑排序
        
        返回值:
            排序后的节点列表，如果存在环则返回None
        
        时间复杂度: O(V + E)
        空间复杂度: O(V)
        """
        # 初始化队列，入度为0的节点入队
        queue = deque([node for node, degree in self.in_degree.items() 
                      if degree == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # 减少相邻节点的入度
            for neighbor in self.graph.get(node, []):
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 如果结果数量不等于节点数，说明存在环
        if len(result) != len(self.graph):
            return None
        
        return result
    
    def has_cycle(self) -> bool:
        """判断是否存在环"""
        return self.sort() is None


if __name__ == "__main__":
    # 邻接表表示图
    print("=== 邻接表 BFS/DFS ===")
    g = GraphAdjacencyList()
    g.add_edge('A', 'B')
    g.add_edge('A', 'C')
    g.add_edge('B', 'D')
    g.add_edge('C', 'D')
    print("BFS:", g.bfs('A'))  # ['A', 'B', 'C', 'D']
    print("DFS:", g.dfs('A'))  # ['A', 'B', 'D', 'C'] 或类似
    
    # 邻接矩阵
    print("\n=== 邻接矩阵 ===")
    gm = GraphAdjacencyMatrix(3)
    gm.add_edge('A', 'B')
    gm.add_edge('B', 'C')
    print("A-B相连:", gm.has_edge('A', 'B'))  # True
    print("A-C相连:", gm.has_edge('A', 'C'))  # False
    
    # 拓扑排序
    print("\n=== 拓扑排序 ===")
    ts = TopologicalSort()
    # 课程依赖：数据结构 -> 算法 -> 编译原理
    ts.add_edge('数据结构', '算法')
    ts.add_edge('算法', '编译原理')
    ts.add_edge('离散数学', '算法')
    ts.add_edge('数据结构', '操作系统')
    
    result = ts.sort()
    print("课程学习顺序:", result)
    # 示例输出: ['离散数学', '数据结构', '算法', '操作系统', '编译原理']
