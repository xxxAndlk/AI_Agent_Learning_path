from datetime import datetime

# f-string 现在支持更复杂的格式说明符
now = datetime(2024, 1, 15, 10, 30, 0)

# 格式化日期
print(f"{now:%Y-%m-%d}")  # 输出: 2024-01-15

# 格式化数字
price = 1234.5678
print(f"{price:.2f}")  # 输出: 1234.57

# 组合使用
name = "Alice"
print(f"{name:>10}")  # 输出:      Alice (右对齐)
