# 安装 Numba
# pip install numba

from numba import jit
import numpy as np
import time

# 纯 Python 版本
def python_sum(arr):
    total = 0.0
    for i in range(len(arr)):
        total += arr[i]
    return total

# Numba JIT 编译版本
@jit(nopython=True)  # 无 Python 解释器开销
def numba_sum(arr):
    total = 0.0
    for i in range(len(arr)):
        total += arr[i]
    return total

# 预热 JIT 编译器
arr = np.random.rand(1000000)
numba_sum(arr)

# 性能对比
start = time.time()
result1 = python_sum(arr)
python_time = time.time() - start

start = time.time()
result2 = numba_sum(arr)
numba_time = time.time() - start

print(f"Python: {python_time:.4f}秒")
print(f"Numba:  {numba_time:.4f}秒")
print(f"加速比: {python_time/numba_time:.1f}x")

# Numba 的优势：
# 1. 自动向量化 SIMD 指令
# 2. 支持并行计算
# 3. 适合数值计算密集型代码

# 更多 Numba 示例
@jit(nopython=True, parallel=True)  # 并行化
def parallel_sum(arr):
    total = 0.0
    for i in prange(len(arr)):  # prange 并行范围
        total += arr[i]
    return total

@jit(nopython=True)
def matrix_multiply(A, B, C):
    """矩阵乘法"""
    m, n = A.shape
    n2, k = B.shape
    for i in range(m):
        for j in range(k):
            for l in range(n):
                C[i, j] += A[i, l] * B[l, j]
