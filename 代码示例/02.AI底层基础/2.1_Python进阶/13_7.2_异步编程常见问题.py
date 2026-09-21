# 问题代码
async def fetch_data():
    return "data"

async def main():
    data = fetch_data()  # ❌ 忘记await，data是协程对象
    print(data)  # 输出: <coroutine object fetch_data at ...>

# 解决方案
async def main():
    data = await fetch_data()  # ✅ 正确await
    print(data)  # 输出: data
