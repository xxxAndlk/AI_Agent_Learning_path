"""
Python threading示例 - 对比其他语言的协程
"""
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor

# 

def worker(name, duration):
    """工作函数"""
    print(f"[Thread] {name} started")
    time.sleep(duration)
    print(f"[Thread] {name} finished")

# 创建并启动线程
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(f"Worker-{i}", 1))
    t.start()
    threads.append(t)

# 等待所有线程完成
for t in threads:
    t.join()

# threading.Lock
counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(10000):
        with lock:  # 自动获取和释放锁
            counter += 1
