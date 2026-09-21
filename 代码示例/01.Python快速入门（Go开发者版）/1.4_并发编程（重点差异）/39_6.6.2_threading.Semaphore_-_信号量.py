import threading
import time

class ConnectionPool:
    """连接池实现 - 使用Semaphore控制并发连接数"""
    
    def __init__(self, max_connections=3):
        # 信号量控制最大并发数
        self.semaphore = threading.Semaphore(max_connections)
        self.connections = []
        self.lock = threading.Lock()
    
    def acquire_connection(self, name):
        """获取连接（最多max_connections个并发）"""
        # 获取信号量（计数-1，如果为0则阻塞等待）
        self.semaphore.acquire()
        
        # 模拟获取数据库连接
        with self.lock:
            conn = f"Connection-{name}"
            self.connections.append(conn)
            print(f"[{conn}] 已获取 | 当前活跃: {len(self.connections)}")
        
        return conn
    
    def release_connection(self, conn):
        """释放连接"""
        # 释放信号量（计数+1，唤醒等待线程）
        with self.lock:
            if conn in self.connections:
                self.connections.remove(conn)
                print(f"[{conn}] 已释放 | 剩余活跃: {len(self.connections)}")
        
        self.semaphore.release()
    
    def use_connection(self, name, duration=1):
        """使用连接的业务逻辑"""
        conn = self.acquire_connection(name)
        try:
            time.sleep(duration)  # 模拟使用连接
        finally:
            self.release_connection(conn)

# 测试信号量
pool = ConnectionPool(max_connections=3)

# 创建6个线程，但最多同时3个获取连接
threads = []
for i in range(6):
    t = threading.Thread(target=pool.use_connection, args=(f"User-{i}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("所有连接已归还")
