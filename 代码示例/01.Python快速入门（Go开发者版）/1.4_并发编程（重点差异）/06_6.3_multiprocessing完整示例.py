"""
Python multiprocessing示例 - 对比Go的并行Goroutine
"""
import multiprocessing as mp
from multiprocessing import Pool, Queue, Process
import time
import os

# Go: go func()（并行执行）
# Python: Process（真正并行，绕过GIL）

def cpu_bound_task(n):
    """CPU密集型任务"""
    print(f"Process {os.getpid()} working on {n}")
    count = 0
    for i in range(n):
        count += i * i
    return count

# 使用Pool（推荐）
if __name__ == '__main__':
    with Pool(processes=4) as pool:
        results = pool.map(cpu_bound_task, [1000000, 2000000, 3000000, 4000000])
        print(f"Results: {results}")
