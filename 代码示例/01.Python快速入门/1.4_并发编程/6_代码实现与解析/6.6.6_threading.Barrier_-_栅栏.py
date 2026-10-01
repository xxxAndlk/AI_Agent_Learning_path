import threading
import time
import random

class ParallelProcessor:
    """并行处理器 - 演示Barrier阶段同步"""
    
    def __init__(self, num_workers=3):
        self.num_workers = num_workers
        # 创建栅栏：所有线程到达后一起继续
        self.barrier = threading.Barrier(num_workers)
        self.phase_results = {}
        self.lock = threading.Lock()
    
    def worker(self, worker_id):
        """工作线程 - 分阶段执行任务"""
        # 阶段1：初始化
        print(f"[Worker-{worker_id}] 阶段1: 初始化")
        time.sleep(random.uniform(0.1, 0.5))
        
        # 同步点1：等待所有worker完成初始化
        print(f"[Worker-{worker_id}] 等待其他人完成初始化...")
        self.barrier.wait()
        print(f"[Worker-{worker_id}] 阶段1完成，继续")
        
        # 阶段2：处理数据
        print(f"[Worker-{worker_id}] 阶段2: 处理数据")
        time.sleep(random.uniform(0.2, 0.8))
        
        with self.lock:
            self.phase_results[worker_id] = f"数据{worker_id}"
        
        # 同步点2：等待所有worker完成处理
        print(f"[Worker-{worker_id}] 等待其他人完成处理...")
        self.barrier.wait()
        print(f"[Worker-{worker_id}] 阶段2完成，汇总结果")
        
        # 阶段3：汇总（只有主线程执行）
        with self.lock:
            if len(self.phase_results) >= self.num_workers:
                print(f"所有数据: {list(self.phase_results.values())}")
    
    def run_all(self):
        """运行所有worker"""
        threads = []
        for i in range(self.num_workers):
            t = threading.Thread(target=self.worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

# 测试栅栏
processor = ParallelProcessor(num_workers=4)
processor.run_all()
