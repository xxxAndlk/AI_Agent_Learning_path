# LBYL更适合的场景
# 检查成本低于异常处理成本

import os

if os.path.exists(filename):
    with open(filename) as f:
        process(f)
else:
    handle_missing()

# EAFP更适合的场景
# 正常情况远多于异常情况
try:
    with open(filename) as f:
        process(f)
except FileNotFoundError:
    handle_missing()
