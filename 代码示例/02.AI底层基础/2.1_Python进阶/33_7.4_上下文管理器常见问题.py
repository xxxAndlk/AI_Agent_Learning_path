# 简化嵌套写法
# 之前：
with open("a") as f1:
    with open("b") as f2:
        process(f1, f2)

# Python 3.10+:
with open("a") as f1, open("b") as f2:
    process(f1, f2)
