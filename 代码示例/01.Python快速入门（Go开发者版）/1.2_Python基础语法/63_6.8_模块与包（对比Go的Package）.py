# ============ 模块导入（对比Go的import） ============
# Go:
# import "fmt"
# import "github.com/gin-gonic/gin"

# Python:
# 导入整个模块（类似Go的import）
import os
import sys

# 从模块导入特定函数/类（类似Go的.操作）
# Go: import . "fmt"
# Python:
from datetime import datetime, timedelta
from math import sqrt, pi

# 使用别名（类似Go的import alias）
# Go: import f "fmt"
# Python:
import numpy as np
import pandas as pd

# 使用
print(np.array([1, 2, 3]))

# ============ 创建自己的模块 ============
# Go: 一个目录一个包，包含多个.go文件
# Python: 一个.py文件就是一个模块

# mymath.py 文件内容：
"""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
"""

# 使用自己的模块
# Go: import "mymodule/mymath"
# Python:
# from mymath import add, multiply, PI
# result = add(3, 5)

# ============ 包结构 ============
# Go: 通过目录结构组织包
# Python: 类似，通过目录+__init__.py

# mypackage/
#     __init__.py      # 标记这是一个包（Go没有对应文件）
#     module1.py
#     module2.py
#     subpackage/
#         __init__.py
#         module3.py

# 使用
# from mypackage import module1
# from mypackage.subpackage import module3
