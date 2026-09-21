import threading

class RecursiveCounter:
    """使用RLock的递归计数器 - 演示可重入特性"""
    
    def __init__(self):
        self.count = 0
        # 创建可重入锁 - 同一线程可多次获取
        self.lock = threading.RLock()
    
    def increment(self):
        """递增计数（递归调用展示可重入）"""
        with self.lock:  # 第一次获取锁
            self.count += 1
            # 内部调用仍然使用同一把锁
            self._internal_increment()
    
    def _internal_increment(self):
        """内部方法 - 演示在持有锁的情况下再次获取锁"""
        with self.lock:  # 第二次获取锁（可重入，不会死锁）
            self.count += 1
    
    def get_count(self):
        """获取当前计数"""
        with self.lock:
            return self.count

# 测试RLock
counter = RecursiveCounter()
threads = []

for i in range(5):
    t = threading.Thread(target=counter.increment)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"最终计数: {counter.get_count()}")  # 输出: 10 (5线程 * 2次递增)
