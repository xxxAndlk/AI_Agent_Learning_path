funcs = [lambda i=i: i for i in range(3)]  # 默认参数绑定当前值
for f in funcs:
    print(f())  # 0, 1, 2
