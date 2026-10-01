# 解释器启动速度提升约10%
# 典型操作如 dict 操作、属性访问更快

# 原地操作优化
lst = [1, 2, 3]
lst.extend([4, 5, 6])  # 比 lst += [4, 5, 6] 更快

# f-string 解析优化
# 大量 f-string 场景下性能提升明显
name = "test"
result = f"{name}_{name}_{name}"  # 更快
