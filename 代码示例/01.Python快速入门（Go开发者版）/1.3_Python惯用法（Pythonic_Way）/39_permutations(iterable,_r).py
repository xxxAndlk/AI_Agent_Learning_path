import itertools

# 基本用法：获取所有2元素排列
letters = ['A', 'B', 'C']
perm = list(itertools.permutations(letters, 2))
print(perm)
# [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

# 全排列
full_perm = list(itertools.permutations(letters))
print(full_perm)
# [('A', 'B', 'C'), ('A', 'C', 'B'), ('B', 'A', 'C'), 
#  ('B', 'C', 'A'), ('C', 'A', 'B'), ('C', 'B', 'A')]
