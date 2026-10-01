import itertools

# 基本用法：两个集合的笛卡尔积
colors = ['红', '绿']
sizes = ['S', 'M', 'L']

cartesian = list(itertools.product(colors, sizes))
print(cartesian)
# [('红', 'S'), ('红', 'M'), ('红', 'L'), 
#  ('绿', 'S'), ('绿', 'M'), ('绿', 'L')]

# repeat参数：等同于重复输入
digits = [0, 1]
two_digit = list(itertools.product(digits, repeat=2))
print(two_digit)  # [(0, 0), (0, 1), (1, 0), (1, 1)]

# 常用场景：生成所有可能的配置
cpu_options = ['i5', 'i7', 'i9']
ram_options = ['8G', '16G', '32G']
all_configs = list(itertools.product(cpu_options, ram_options))
print(f"总配置数: {len(all_configs)}")  # 9
