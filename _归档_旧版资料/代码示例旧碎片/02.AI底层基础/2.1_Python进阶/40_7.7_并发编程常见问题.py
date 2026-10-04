# 问题：CPU密集型任务无法利用多线程
def cpu_task():
    return sum(i**2 for i in range(1000000))

with ThreadPoolExecutor() as executor:
    # 多个线程实际上无法并行执行
    results = list(executor.map(lambda _: cpu_task(), range(4)))

# 解决方案：使用ProcessPoolExecutor
with ProcessPoolExecutor() as executor:
    results = list(executor.map(lambda _: cpu_task(), range(4)))
