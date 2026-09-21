"""
实际场景：多数据源聚合（类似Go的fan-in模式）
"""
import asyncio
from asyncio import Queue
import random

async def fetch_from_api(api_name, delay):
    """模拟从不同API获取数据"""
    await asyncio.sleep(delay)
    return {"source": api_name, "data": f"数据 from {api_name}"}

async def aggregator():
    """
    聚合器：谁先返回先处理
    类似于Go的select fan-in模式
    """
    # 创建多个API调用任务
    tasks = [
        asyncio.create_task(fetch_from_api("用户API", random.uniform(0.5, 2.0))),
        asyncio.create_task(fetch_from_api("订单API", random.uniform(0.5, 2.0))),
        asyncio.create_task(fetch_from_api("商品API", random.uniform(0.5, 2.0))),
        asyncio.create_task(fetch_from_api("通知API", random.uniform(0.5, 2.0))),
    ]
    
    results = []
    received = 0
    total = len(tasks)
    
    print(f"开始等待 {total} 个数据源...\n")
    
    # 使用as_completed实现fan-in
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        received += 1
        print(f"[{received}/{total}] 收到: {result['source']}")
        
        # 可以在这里立即处理，而不用等待所有数据
        # 例如：流式处理、实时推送等
    
    return results

# 运行
results = asyncio.run(aggregator())
print(f"\n最终聚合结果: {len(results)} 条数据")
