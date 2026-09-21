"""
asyncio.wait() 示例 - 等待多个任务完成
"""
import asyncio

async def task_a():
    """模拟耗时任务A（2秒）"""
    print("Task A: 开始执行")
    await asyncio.sleep(2)
    print("Task A: 执行完成")
    return "Result A"

async def task_b():
    """模拟耗时任务B（1秒）"""
    print("Task B: 开始执行")
    await asyncio.sleep(1)
    print("Task B: 执行完成")
    return "Result B"

async def task_c():
    """模拟耗时任务C（3秒）"""
    print("Task C: 开始执行")
    await asyncio.sleep(3)
    print("Task C: 执行完成")
    return "Result C"

async def main():
    # 创建多个任务（类似Go的go关键字）
    # 区别：Python创建的是协程，需要放入事件循环调度
    task1 = asyncio.create_task(task_a())
    task2 = asyncio.create_task(task_b())
    task3 = asyncio.create_task(task_c())
    
    # asyncio.wait() 等待所有任务完成
    # 返回两个集合：(已完成任务, 未完成任务)
    # 注意：默认会等待所有任务完成
    done, pending = await asyncio.wait([task1, task2, task3])
    
    # 收集结果
    for t in done:
        print(f"完成: {t.result()}")

# 运行
asyncio.run(main())
