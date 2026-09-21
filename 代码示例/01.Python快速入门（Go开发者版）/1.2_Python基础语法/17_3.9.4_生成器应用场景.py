# ============ 生成器协程（对比Go的goroutine） ============
# Go使用goroutine实现并发，Python使用asyncio + 生成器
# Python 3.5+推荐使用async/await，但生成器仍可用于协程

def async_worker(name):
    """模拟异步工作者 - 使用yield实现协程切换点"""
    print(f"[{name}] 启动")
    while True:
        task = yield  # 暂停等待任务
        if task is None:  # 收到None表示停止
            print(f"[{name}] 停止")
            break
        print(f"[{name}] 处理任务: {task}")
        yield f"完成: {task}"  # 返回结果

# 创建协程
worker1 = async_worker("Worker-1")
worker2 = async_worker("Worker-2")

# 启动协程到第一个yield
next(worker1)
next(worker2)

# 发送任务
print(worker1.send("任务A"))  # Worker-1处理，返回"完成: 任务A"
print(worker2.send("任务B"))  # Worker-2处理
print(worker1.send("任务C"))  # Worker-1处理

# 停止协程
worker1.send(None)  # 发送None停止
worker2.send(None)

# ============ 生产者-消费者模式 ============
def producer(consumer, items):
    """生产者：发送数据到消费者"""
    for item in items:
        result = consumer.send(item)
        print(f"生产者收到反馈: {result}")
    consumer.close()  # 关闭消费者

def consumer():
    """消费者：处理数据"""
    while True:
        item = yield
        if item is None:  # 收到结束信号
            break
        processed = f"[已处理]{item}"
        yield processed

# 使用
cons = consumer()
next(cons)  # 启动消费者
producer(cons, ["数据1", "数据2", "数据3"])
