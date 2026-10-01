from datetime import datetime, timedelta
import time

# 当前时间
now = datetime.now()
print(now)  # 2024-01-15 10:30:00.123456

# 时间戳
timestamp = time.time()  # 1705312200.123

# 格式化
formatted = now.strftime("%Y-%m-%d %H:%M:%S")

# 解析时间
parsed = datetime.strptime("2024-01-15", "%Y-%m-%d")

# 时间运算
future = now + timedelta(days=7)
