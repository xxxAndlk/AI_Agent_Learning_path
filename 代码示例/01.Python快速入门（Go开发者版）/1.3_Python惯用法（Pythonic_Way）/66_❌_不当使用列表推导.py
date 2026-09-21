# 反模式：列表推导用于副作用
[print(x) for x in range(10)]  # 创建无用的[None, None, ...]列表

# 正确做法：使用普通循环
for x in range(10):
    print(x)
