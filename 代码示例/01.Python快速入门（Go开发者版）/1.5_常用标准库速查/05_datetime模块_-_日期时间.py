from datetime import datetime, timedelta
import time

# 当前时间
# Go: time.Now()
now = datetime.now()
print(now)  # 2024-01-15 10:30:00.123456

# 时间戳
# Go: time.Now().Unix()
timestamp = time.time()  # 1705312200.123

# 格式化
# Go: time.Format("2006-01-02 15:04:05")
formatted = now.strftime("%Y-%m-%d %H:%M:%S")

# 解析时间
# Go: time.Parse()
parsed = datetime.strptime("2024-01-15", "%Y-%m-%d")

# 时间运算
# Go: now.Add(24 * time.Hour)
future = now + timedelta(days=7)
