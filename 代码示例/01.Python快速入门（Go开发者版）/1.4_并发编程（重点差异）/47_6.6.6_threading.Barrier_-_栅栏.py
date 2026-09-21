import threading
import time

def worker_with_abort(worker_id, barrier):
    """可中止的worker"""
    try:
        print(f"[Worker-{worker_id}] 开始执行")
        time.sleep(0.5)
        result = barrier.wait(timeout=1)  # 等待其他线程，带超时
        print(f"[Worker-{worker_id}] 栅栏通过，位置: {result}")
    except threading.BrokenBarrierError:
        print(f"[Worker-{worker_id}] 栅栏已被打破")

# 测试栅栏打破
barrier = threading.Barrier(3)

# 启动2个正常线程
threads = []
for i in range(2):
    t = threading.Thread(target=worker_with_abort, args=(i, barrier))
    threads.append(t)
    t.start()

time.sleep(1)

# 打破栅栏（让第3个线程无法通过）
print("打破栅栏...")
barrier.abort()

# 启动第3个线程，它会遇到BrokenBarrierError
t3 = threading.Thread(target=worker_with_abort, args=(2, barrier))
t3.start()

for t in threads + [t3]:
    t.join()
