# 问题代码
gen = (x for x in range(3))
print(list(gen))  # [0, 1, 2]
print(list(gen))  # [] - 第二次为空！

# 解决方案：重新创建生成器或使用列表
data = list(gen)  # 如果需要多次迭代，转为列表
