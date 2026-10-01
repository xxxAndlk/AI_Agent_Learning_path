# 01_问候函数.py —— 练习 1 参考答案
# 带默认参数的问候函数：word 不传就用默认的，传了就用你给的

def greet(name, word="你好"):
    print(word + "，" + name + "！")


# 不传 word：用默认的"你好"
greet("小明")

# 传了 word：默认值被顶掉，用新词
greet("小红", "早上好")

greet("未来的程序员", "加油")
