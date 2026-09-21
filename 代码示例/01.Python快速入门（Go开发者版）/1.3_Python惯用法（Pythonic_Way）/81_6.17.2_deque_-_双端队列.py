from collections import deque

# 创建空队列
dq = deque()

# 从可迭代对象创建
dq = deque([1, 2, 3, 4, 5])

# 限制最大长度（超出时自动丢弃对端元素）
dq_max = deque(maxlen=3)
dq_max.extend([1, 2, 3])
dq_max.append(4)  # 自动丢弃最左边的1
print(list(dq_max))  # [2, 3, 4]

# 右侧操作（append/extend/pop）
dq = deque([1, 2, 3])
dq.append(4)        # 右侧添加: [1, 2, 3, 4]
dq.extend([5, 6])   # 右侧扩展: [1, 2, 3, 4, 5, 6]
val = dq.pop()      # 右侧弹出: 返回6，dq变为[1, 2, 3, 4, 5]

# 左侧操作（appendleft/extendleft/popleft）
dq = deque([1, 2, 3])
dq.appendleft(0)        # 左侧添加: [0, 1, 2, 3]
dq.extendleft([-2, -1]) # 左侧扩展: [-2, -1, 0, 1, 2, 3]
val = dq.popleft()      # 左侧弹出: 返回-2，dq变为[-1, 0, 1, 2, 3]

# 旋转队列
dq = deque([1, 2, 3, 4, 5])
dq.rotate(2)    # 向右旋转2位: [4, 5, 1, 2, 3]
dq.rotate(-1)   # 向左旋转1位: [5, 1, 2, 3, 4]

# 清空队列
dq.clear()

# 查看元素（不删除）
dq = deque([1, 2, 3])
print(dq[0])   # 查看左侧第一个: 1
print(dq[-1])  # 查看右侧最后一个: 3
