"""
asyncio.as_completed() 示例 - 谁先完成先处理
"""
import asyncio
import random

async def random_task(name, duration):
    """模拟随机时长的任务"""
    # 随机等待0.1到2秒
    wait_time = random.uniform(0.1, 2.0)
    await asyncio.sleep(wait_time)
    return f"{name} 耗时 {wait_time:.2f}秒"

async def main():
    # 创建多个任务（耗时不同）
    tasks = [
        asyncio.create_task(random_task("任务A", None)),
        asyncio.create_task(random_task("任务B", None)),
        asyncio.create_task(random_task("任务C", None)),
        asyncio.create_task(random_task("任务D", None)),
    ]
    
    # as_completed() 返回一个迭代器
    # 按照完成顺序逐个返回已完成的任务
    # 这正是Go select的核心行为："谁先完成先处理"
    print("任务执行顺序（按照完成先后）：\n")
    
    for coro in asyncio.as_completed(tasks):
        # 等待下一个完成的任务
        result = await coro
        print(f"✓ {result}")

# 运行多次观察不同结果
for i in range(3):
    print(f"=== 第{i+1}次运行 ===")
    asyncio.run(main())
    print()
