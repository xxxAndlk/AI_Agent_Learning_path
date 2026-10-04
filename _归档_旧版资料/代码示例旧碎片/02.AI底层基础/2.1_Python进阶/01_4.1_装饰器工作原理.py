@decorator_a      # 第三层包装（最先装饰，最后执行）
@decorator_b      # 第二层包装
@decorator_c      # 第一层包装（最后装饰，最先执行）
def func():
    pass

# 等价于：func = decorator_a(decorator_b(decorator_c(func)))
