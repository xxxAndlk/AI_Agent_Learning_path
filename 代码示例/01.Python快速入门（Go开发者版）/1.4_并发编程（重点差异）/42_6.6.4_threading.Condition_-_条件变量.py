import threading
import time
import queue

class ThreadSafeQueue:
    """线程安全的条件变量队列 - 演示生产者-消费者模式"""
    
    def __init__(self, maxsize=5):
        self.queue = queue.Queue(maxsize=maxsize)
        self.condition = threading.Condition()
    
    def put(self, item):
        """生产者：放入数据（队列满时等待）"""
        with self.condition:
            # 队列满时等待消费者消费
            while self.queue.full():
                print(f"[Producer] 队列满，等待消费...")
                self.condition.wait()  # 释放锁，等待通知
            
            self.queue.put(item)
            print(f"[Producer] 生产: {item} | 队列大小: {self.queue.qsize()}")
            
            # 通知等待的消费者
            self.condition.notify()  # 唤醒一个等待线程
            # 或 notify_all() 唤醒所有等待线程
    
    def get(self):
        """消费者：取出数据（队列空时等待）"""
        with self.condition:
            # 队列空时等待生产者生产
            while self.queue.empty():
                print(f"[Consumer] 队列空，等待生产...")
                self.condition.wait()  # 释放锁，等待通知
            
            item = self.queue.get()
            print(f"[Consumer] 消费: {item} | 剩余: {self.queue.qsize()}")
            
            # 通知等待的生产者
            self.condition.notify()
            
        return item

# 测试条件变量
safe_queue = ThreadSafeQueue(maxsize=3)

def producer(producer_id, count):
    """生产者线程"""
    for i in range(count):
        safe_queue.put(f"P{producer_id}-Item{i}")
        time.sleep(0.3)

def consumer(consumer_id, count):
    """消费者线程"""
    for _ in range(count):
        item = safe_queue.get()
        time.sleep(0.5)

# 启动生产者和消费者
threads = [
    threading.Thread(target=producer, args=(1, 3)),
    threading.Thread(target=producer, args=(2, 3)),
    threading.Thread(target=consumer, args=(1, 3)),
    threading.Thread(target=consumer, args=(2, 3)),
]

for t in threads:
    t.start()

for t in threads:
    t.join()

print("生产者-消费者测试完成")
