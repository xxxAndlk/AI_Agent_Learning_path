import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

# 陷阱1：在asyncio中运行CPU密集型代码
async def cpu_task():
    for i in range(10000000):  # 阻塞事件循环！
        pass
        
# 解决：使用run_in_executor（在协程内调用）
async def run_cpu_task(cpu_intensive_func):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, cpu_intensive_func)

# 陷阱2：创建过多线程
tasks = [threading.Thread(target=func) for _ in range(10000)]  # 内存爆炸

# 解决：使用线程池
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(func, items))
