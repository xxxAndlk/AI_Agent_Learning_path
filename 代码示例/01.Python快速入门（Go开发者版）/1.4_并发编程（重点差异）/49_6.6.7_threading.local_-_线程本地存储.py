import threading
import time

# 创建线程局部存储对象
thread_local = threading.local()

class RequestHandler:
    """请求处理器 - 使用线程本地存储保存请求上下文"""
    
    def __init__(self):
        self.name = "Handler"
    
    def process_request(self, request_id):
        """处理请求 - 每个线程独立的请求上下文"""
        # 为当前线程设置独立的请求ID
        thread_local.request_id = request_id
        thread_local.start_time = time.time()
        
        print(f"[{self.name}] 线程{threading.current_thread().name} 处理请求 {request_id}")
        
        # 调用业务逻辑
        self._do_processing()
        
        # 访问当前线程的局部数据
        elapsed = time.time() - thread_local.start_time
        print(f"[{self.name}] 请求 {thread_local.request_id} 处理完成，耗时: {elapsed:.3f}s")
    
    def _do_processing(self):
        """模拟业务处理 - 使用线程局部数据"""
        # 模拟不同线程处理速度不同
        time.sleep(0.1)
        
        # 在这里可以访问当前线程的局部数据
        current_id = thread_local.request_id
        print(f"  -> 线程{threading.current_thread().name} 正在处理请求 {current_id}")

# 数据库连接示例
class DatabaseManager:
    """数据库管理器 - 每个线程独立连接"""
    
    def __init__(self):
        self.connection_string = "mysql://localhost:3306/testdb"
        # 线程本地存储：每个线程独立的数据库连接
        self.local = threading.local()
    
    def get_connection(self):
        """获取当前线程的数据库连接"""
        if not hasattr(self.local, 'connection'):
            # 模拟创建新连接（首次访问时创建）
            self.local.connection = f"Connection({self.connection_string})-{threading.current_thread().name}"
            print(f"  创建新连接: {self.local.connection}")
        else:
            print(f"  复用已有连接: {self.local.connection}")
        
        return self.local.connection
    
    def execute_query(self, query):
        """执行查询"""
        conn = self.get_connection()
        print(f"[{conn}] 执行: {query}")

# 测试线程本地存储
handler = RequestHandler()
db = DatabaseManager()

def handle_requests(request_ids):
    """处理一组请求"""
    for req_id in request_ids:
        handler.process_request(req_id)
        db.execute_query(f"SELECT * FROM table_{req_id}")

# 启动多个线程处理请求
threads = []
requests_per_thread = [range(1, 4), range(4, 7), range(7, 10)]

for i, reqs in enumerate(requests_per_thread):
    t = threading.Thread(target=handle_requests, args=(reqs,), name=f"Worker-{i}")
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n线程本地存储演示完成")
print("注意：每个线程的request_id和connection是独立的")
