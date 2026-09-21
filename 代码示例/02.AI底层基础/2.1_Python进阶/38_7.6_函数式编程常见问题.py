# 问题
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]  # [2, 2, 2]

# 解决方案：默认参数捕获
funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]  # [0, 1, 2]
