# 错误1: 循环导入
# a.py导入b.py，b.py又导入a.py
# 解决: 重构代码，或延迟导入

# 错误2: Python 2 vs 3兼容
# Python 2: import urllib2
# Python 3: import urllib.request
# 解决: 使用six库或from __future__ import

# 错误3: 相对导入错误
# from . import module  # 相对导入
# 解决: 使用绝对导入或调整PYTHONPATH
