# 安装 Cython
# pip install cython

# 示例：hello.pyx
# 这是一个 .pyx 文件，使用 Cython 语法

def fibonacci(int n):
    """计算斐波那契数，返回 int"""
    cdef int a = 0
    cdef int b = 1
    cdef int i
    cdef int temp
    
    for i in range(n):
        temp = a + b
        a = b
        b = temp
    
    return a

# 编译
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="hello",
    ext_modules=cythonize("hello.pyx"),  # 编译 .pyx 文件
)

# 运行: python setup.py build_ext --inplace

# 使用编译后的模块
from hello import fibonacci
result = fibonacci(100)  # 比纯 Python 快几十倍
