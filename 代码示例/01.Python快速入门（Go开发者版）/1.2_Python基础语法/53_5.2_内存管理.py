import sys

a = [1, 2, 3]
print(sys.getrefcount(a))  # 引用计数（比实际多1，因为getrefcount本身也引用）

# 循环引用问题
class Node:
    def __init__(self):
        self.next = None

n1 = Node()
n2 = Node()
n1.next = n2  # n1引用n2
n2.next = n1  # n2引用n1 → 循环引用
# 引用计数无法处理，需要GC介入
