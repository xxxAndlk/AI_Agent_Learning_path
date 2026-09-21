# 3. 字典默认值
# Go: if val, ok := m["key"]; !ok { val = default }
# Python:
counts = {}
# 不推荐：
# if "apple" in counts:
#     counts["apple"] += 1
# else:
#     counts["apple"] = 1

# 推荐：
counts["apple"] = counts.get("apple", 0) + 1

# 或使用collections.Counter
from collections import Counter
counts = Counter(["apple", "banana", "apple", "cherry"])
print(counts["apple"])      # 输出: 2
