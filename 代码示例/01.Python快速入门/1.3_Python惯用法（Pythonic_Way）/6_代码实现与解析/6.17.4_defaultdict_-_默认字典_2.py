# 实际案例：图的邻接表
from collections import defaultdict
from collections import deque

class Graph:
    def __init__(self):
        self.adj = defaultdict(list)
    
    def add_edge(self, u, v):
        self.adj[u].append(v)
    
    def bfs(self, start):
        visited = set()
        queue = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            print(node, end=' ')
            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

# 使用
g = Graph()
g.add_edge(1, 2)
g.add_edge(1, 3)
g.add_edge(2, 4)
g.add_edge(2, 5)
g.bfs(1)  # 1 2 3 4 5
