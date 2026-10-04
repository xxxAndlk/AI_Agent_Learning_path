from concurrent.futures import (                      # 导入并发编程相关类
    ThreadPoolExecutor, ProcessPoolExecutor, as_completed
)
import time
import threading
import multiprocessing as mp
from typing import List

# ============ 1. ThreadPoolExecutor - IO密集型任务 ============
def download_file(url: str) -> dict:
    """模拟文件下载（IO密集型）
    
    在实际应用中，这里会是真实的网络请求
    
    参数:
        url: 文件URL
    返回:
        包含URL和下载状态的字典
    """
    # 模拟网络延迟
    time.sleep(0.5)
    return {"url": url, "status": "success", "thread": threading.current_thread().name}

# ============ 2. ProcessPoolExecutor - CPU密集型任务 ============
def matrix_multiply(size: int) -> int:
    """矩阵乘法计算（CPU密集型）
    
    使用numpy进行矩阵乘法，模拟深度学习中的前向传播
    
    参数:
        size: 矩阵大小
    返回:
        矩阵元素总和（用于验证计算完成）
    """
    import numpy as np
    
    # 创建随机矩阵
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    
    # 矩阵乘法（模拟深度学习中的前向传播）
    result = np.dot(a, b)
    
    return int(result.sum())

# ============ 3. 线程池使用示例 ============
def use_thread_pool():
    """线程池示例：并发下载多个文件"""
    urls = [
        "https://example.com/file1.jpg",
        "https://example.com/file2.jpg",
        "https://example.com/file3.jpg",
        "https://example.com/file4.jpg",
        "https://example.com/file5.jpg",
    ]
    
    # 创建线程池，最大工作线程数为3
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交所有任务，获取Future对象列表
        futures = [executor.submit(download_file, url) for url in urls]
        
        # 等待所有任务完成
        for future in as_completed(futures):
            result = future.result()                 # 获取任务结果
            print(f"下载完成: {result['url']} (线程: {result['thread']})")

# ============ 4. 进程池使用示例 ============
def use_process_pool():
    """进程池示例：并发计算多个矩阵乘法"""
    sizes = [100, 200, 300, 400, 500]
    
    # 创建进程池，最大工作进程数为CPU核心数
    # 注意：Windows上必须使用if __name__ == "__main__"保护
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # 使用map提交任务（保持顺序）
        results = list(executor.map(matrix_multiply, sizes))
        
        for size, result in zip(sizes, results):
            print(f"矩阵 {size}x{size} 计算完成，结果和: {result}")

# ============ 5. 回调机制 ============
def process_with_callback():
    """使用回调处理任务完成事件"""
    def callback(future):
        """回调函数：当任务完成时调用"""
        result = future.result()
        print(f"任务完成，结果: {result}")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(lambda: time.sleep(1) or "Done")
        future.add_done_callback(callback)           # 添加回调
        time.sleep(1.5)                              # 等待回调执行

# ============ 6. 等待多个 futures ============
def wait_multiple_futures():
    """等待多个Future对象的不同方式"""
    with ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(time.sleep, 1)
        f2 = executor.submit(time.sleep, 2)
        f3 = executor.submit(time.sleep, 0.5)
        
        # as_completed: 按完成顺序返回
        print("按完成顺序:")
        for future in as_completed([f1, f2, f3]):
            print(f"  任务完成")
        
        # wait: 等待所有（或任意一个）完成
        done, not_done = ([f1, f2, f3], [])
        print(f"\n已完成: {len(done)}, 未完成: {len(not_done)}")

# ============ 主程序入口 ============
if __name__ == "__main__":
    print("=" * 50)
    print("线程池示例（IO密集型）:")
    print("=" * 50)
    start = time.time()
    use_thread_pool()
    print(f"总耗时: {time.time() - start:.2f}秒")
    
    print("\n" + "=" * 50)
    print("进程池示例（CPU密集型）:")
    print("=" * 50)
    start = time.time()
    use_process_pool()
    print(f"总耗时: {time.time() - start:.2f}秒")
    
    print("\n" + "=" * 50)
    print("回调机制示例:")
    print("=" * 50)
    process_with_callback()
    
    print("\n" + "=" * 50)
    print("等待多个Future:")
    print("=" * 50)
    wait_multiple_futures()
