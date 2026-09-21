# GIL示例：多线程不能加速CPU密集型任务
import threading

def cpu_bound_task():
    count = 0
    for i in range(10_000_000):
        count += 1
    return count

# 多线程版本（比单线程还慢！因为GIL切换开销）
threads = []
for _ in range(4):
    t = threading.Thread(target=cpu_bound_task)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
