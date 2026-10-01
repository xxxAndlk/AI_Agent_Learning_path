import itertools

# 基本用法：按条件过滤
data = ['A', 'B', 'C', 'D', 'E']
selectors = [True, False, True, False, True]

result = list(itertools.compress(data, selectors))
print(result)  # ['A', 'C', 'E']

# 常用场景：根据多个条件筛选
names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
scores = [85, 92, 78, 90, 88]
passed = [s >= 80 for s in scores]

passed_names = list(itertools.compress(names, passed))
print(passed_names)  # ['Alice', 'Bob', 'David', 'Eve']
