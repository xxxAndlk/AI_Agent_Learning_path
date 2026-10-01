# 14. 使用setdefault和defaultdict
# 不推荐
# if key not in d:
#     d[key] = []
# d[key].append(value)

# 推荐
from collections import defaultdict
d = defaultdict(list)
d['key'].append('value')  # 自动创建空列表

# 或使用setdefault
d = {}
d.setdefault('key', []).append('value')
