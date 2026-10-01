import threading
import time
import random

class AsyncTaskRunner:
    """异步任务运行器 - 演示Event事件通知"""
    
    def __init__(self):
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.completion_event = threading.Event()
        self.results = []
        self.lock = threading.Lock()
    
    def start_worker(self, worker_id):
        """工作线程 - 等待开始事件"""
        print(f"[Worker-{worker_id}] 等待开始信号...")
        self.start_event.wait()  # 阻塞等待开始事件
        
        print(f"[Worker-{worker_id}] 开始执行任务...")
        # 模拟工作
        time.sleep(random.uniform(0.5, 1.5))
        
        with self.lock:
            self.results.append(f"Worker-{worker_id}完成")
        
        # 标记完成
        if len(self.results) >= 3:  # 假设有3个worker
            self.completion_event.set()
        
        print(f"[Worker-{worker_id}] 任务完成")
    
    def start_all(self):
        """启动所有worker"""
        print("发出开始信号...")
        self.start_event.set()  # 发出开始信号
    
    def wait_completion(self, timeout=5):
        """等待所有任务完成"""
        print("等待任务完成...")
        success = self.completion_event.wait(timeout=timeout)
        return success

# 测试事件通知
runner = AsyncTaskRunner()

# 创建3个工作线程
workers = []
for i in range(3):
    t = threading.Thread(target=runner.start_worker, args=(i,))
    workers.append(t)
    t.start()

# 等待一下确保所有worker都启动并等待
time.sleep(0.5)

# 发出开始信号
runner.start_all()

# 等待完成
if runner.wait_completion():
    print(f"所有任务完成，结果: {runner.results}")
else:
    print("任务超时")

# 演示事件清除和重置
runner.start_event.clear()  # 清除开始事件
runner.completion_event.clear()  # 清除完成事件
print("事件已重置")
