funcs = [lambda: i for i in range(3)]
for f in funcs:
    print(f())  # 2, 2, 2  不是0, 1, 2！
