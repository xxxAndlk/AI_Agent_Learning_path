from collections import defaultdict, Counter, deque, namedtuple

# defaultdict: 带默认值的字典
# Go: 需要手动检查
word_count = defaultdict(int)
for word in ["apple", "banana", "apple"]:
    word_count[word] += 1  # 不存在时默认值为0

# Counter: 计数器
# Go: 需要map[string]int手动实现
counter = Counter(["red", "blue", "red", "green", "red"])
print(counter.most_common(2))  # [('red', 3), ('blue', 1)]

# deque: 双端队列（O(1)两端操作）
# Go: container/list包
d = deque(maxlen=3)
d.append(1)
d.append(2)
d.appendleft(0)  # 左添加
print(list(d))  # [0, 1, 2]
