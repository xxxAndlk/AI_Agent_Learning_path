# 非Pythonic - 像C/Java风格
result = []
for i in range(10):
    if i % 2 == 0:
        result.append(i * i)

# Pythonic - 简洁优雅
result = [i * i for i in range(10) if i % 2 == 0]
