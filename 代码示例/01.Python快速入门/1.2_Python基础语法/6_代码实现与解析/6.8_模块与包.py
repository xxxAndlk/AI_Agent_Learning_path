# ============ 模块导入 ============
# import "fmt"
# import "github.com/gin-gonic/gin"

# 
# 导入整个模块
import os
import sys

# 从模块导入特定函数/类
# 
from datetime import datetime, timedelta
from math import sqrt, pi

# 使用别名
# 
import numpy as np
import pandas as pd

# 使用
print(np.array([1, 2, 3]))

# ============ 创建自己的模块 ============
# 一个.py文件就是一个模块

# mymath.py 文件内容：
"""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
"""

# 使用自己的模块
# 
# from mymath import add, multiply, PI
# result = add(3, 5)

# ============ 包结构 ============
# 类似，通过目录+__init__.py

# mypackage/
#     __init__.py      # 标记这是一个包
#     module1.py
#     module2.py
#     subpackage/
#         __init__.py
#         module3.py

# 使用
# from mypackage import module1
# from mypackage.subpackage import module3
