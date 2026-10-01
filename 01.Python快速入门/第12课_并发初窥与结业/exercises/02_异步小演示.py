"""练习2参考答案：异步小演示
两个 async 函数各睡不同秒数，用 gather 并发跑，对比总耗时：
如果写成普通的顺序执行，2 + 1 = 3 秒；并发跑只要约 2 秒。
"""
import asyncio
import time


async def boil_water():
    print("烧水：开始（要 2 秒）")
    await asyncio.sleep(2)  # 等待期间，事件循环可以去跑切菜
    print("烧水：水开了")


async def cut_vegetables():
    print("切菜：开始（要 1 秒）")
    await asyncio.sleep(1)
    print("切菜：切好了")


async def main():
    start = time.perf_counter()
    # gather 把两个协程一起交给事件循环，谁在等就让谁先歇着
    await asyncio.gather(boil_water(), cut_vegetables())
    cost = time.perf_counter() - start
    print(f"总耗时 {cost:.2f} 秒（顺序执行要 3 秒，并发只用了约 2 秒）")


# async 函数直接调用不会跑，要用 asyncio.run 启动
asyncio.run(main())
