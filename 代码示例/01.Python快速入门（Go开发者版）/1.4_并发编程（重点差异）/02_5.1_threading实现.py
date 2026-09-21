import threading
import queue
import time

class ThreadPool:
    """线程池实现（类似Go的Worker Pool）"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def start(self):
        """启动工作线程"""
        self.running = True
        for i in range(self.max_workers):
            t = threading.Thread(target=self._worker, args=(i,))
            t.daemon = True
            t.start()
            self.workers.append(t)
    
    def _worker(self, worker_id):
        """工作线程（类似Go的goroutine）"""
        while self.running:
            try:
                func, args, kwargs, result_queue = self.task_queue.get(timeout=1)
                try:
                    result = func(*args, **kwargs)
                    result_queue.put(('success', result))
                except Exception as e:
                    result_queue.put(('error', str(e)))
                self.task_queue.task_done()
            except queue.Empty:
                continue
    
    def submit(self, func, *args, **kwargs):
        """提交任务（类似Go的go func()）"""
        result_queue = queue.Queue()
        self.task_queue.put((func, args, kwargs, result_queue))
        return result_queue
    
    def shutdown(self):
        """关闭线程池"""
        self.running = False
        self.task_queue.join()
        for w in self.workers:
            w.join()
