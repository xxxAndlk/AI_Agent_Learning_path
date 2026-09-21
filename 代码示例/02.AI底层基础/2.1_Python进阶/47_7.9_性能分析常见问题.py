# 问题：单次测量不可靠
timeit("x = [i**2 for i in range(1000)]", number=1)

# 解决方案：多次测量取平均
timeit(..., number=1000, repeat=5)
