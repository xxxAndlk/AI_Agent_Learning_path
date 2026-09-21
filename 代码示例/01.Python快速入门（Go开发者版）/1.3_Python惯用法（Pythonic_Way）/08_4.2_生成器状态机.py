def gen():
    yield 1  # 状态1：产生1，暂停
    yield 2  # 状态2：产生2，暂停
    yield 3  # 状态3：产生3，结束

g = gen()
# 内部状态：GEN_CREATED（刚创建）
next(g)  # 执行到yield 1，返回1，状态变为GEN_SUSPENDED
next(g)  # 从上次暂停处继续，到yield 2
next(g)  # 到yield 3
next(g)  # 抛出StopIteration
