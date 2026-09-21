import threading
import time

class BoundedResourcePool:
    """有界资源池 - 演示BoundedSemaphore防止过度释放"""
    
    def __init__(self, max_size=2):
        # 有界信号量：计数不会超过max_size
        self.semaphore = threading.BoundedSemaphore(max_size)
        self.active_count = 0
        self.lock = threading.Lock()
    
    def acquire(self, name):
        """获取资源"""
        print(f"[{name}] 等待获取资源...")
        self.semaphore.acquire()
        
        with self.lock:
            self.active_count += 1
            print(f"[{name}] 获取成功 | 活跃资源: {self.active_count}/{max_size}")
    
    def release(self, name):
        """释放资源（有界版本会检测重复释放）"""
        with self.lock:
            if self.active_count > 0:
                self.active_count -= 1
                print(f"[{name}] 释放资源 | 剩余活跃: {self.active_count}")
                self.semaphore.release()
            else:
                # BoundedSemaphore会抛出ValueError
                print(f"[{name}] 警告：资源已全部释放，不可重复释放！")

# 测试有界信号量
pool = BoundedResourcePool(max_size=2)

# 正常获取和释放
pool.acquire("User-1")
time.sleep(0.5)
pool.release("User-1")

# 尝试过度释放 - BoundedSemaphore会检测到
pool.acquire("User-2")
pool.release("User-2")

# 这会抛出ValueError（演示用try-except捕获）
try:
    pool.release("User-2")  # 再次释放
except ValueError as e:
    print(f"检测到过度释放: {e}")
