# CPU密集型任务：多线程无加速效果
import threading
import time

def cpu_task():
    sum(range(10000000))

# 多线程版本
start = time.time()
threads = [threading.Thread(target=cpu_task) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"多线程: {time.time() - start:.2f}s")  # 无加速

# 多进程版本
from multiprocessing import Process
start = time.time()
processes = [Process(target=cpu_task) for _ in range(4)]
for p in processes: p.start()
for p in processes: p.join()
print(f"多进程: {time.time() - start:.2f}s")  # 有加速
