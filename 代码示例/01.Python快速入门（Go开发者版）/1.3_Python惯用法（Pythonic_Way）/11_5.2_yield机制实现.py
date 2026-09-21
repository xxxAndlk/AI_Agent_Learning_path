# yield在底层通过帧栈保存和恢复实现

def coroutine_example():
    print("启动")
    x = yield "准备接收"
    print(f"收到: {x}")
    y = yield "继续"
    print(f"再次收到: {y}")
    return "结束"

# 执行流程
co = coroutine_example()  # 创建生成器，不执行任何代码
result = next(co)         # 执行到第一个yield，返回"准备接收"
# 输出: 启动
print(result)             # "准备接收"

result = co.send("Hello") # 从第一个yield处恢复，x="Hello"，执行到第二个yield
# 输出: 收到: Hello
print(result)             # "继续"
