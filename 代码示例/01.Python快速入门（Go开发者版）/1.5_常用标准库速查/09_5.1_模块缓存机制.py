import sys

# 查看已缓存的模块
print('json' in sys.modules)  # False

import json

print('json' in sys.modules)  # True
print(sys.modules['json'])    # <module 'json' from '...'>
