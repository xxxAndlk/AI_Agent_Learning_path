# 问题：共享状态导致数据竞争
counter = 0
def increment():
    global counter
    for _ in range(100000):
        counter += 1  # 非原子操作

# 解决方案：使用线程锁
import threading
lock = threading.Lock()

def safe_increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1
