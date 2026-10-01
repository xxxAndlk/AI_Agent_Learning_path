# 简单映射用推导
squares = {x: x*x for x in range(10)}

# 复杂逻辑用循环
result = {}
for x in data:
    if is_valid(x):
        key = transform(x)
        value = expensive_computation(x)
        result[key] = value
