# ============ 生成器函数（对比Go） ============
# Go: 使用channel实现类似功能
# func generatenums(ch chan int) {
#     for i := 1; i <= 5; i++ {
#         ch <- i  // 发送值到channel
#     }
#     close(ch)
# }

# Python: 使用yield关键字
def count_to_five():
    """生成1到5的计数器 - 每次调用yield暂停函数执行"""
    for i in range(1, 6):
        yield i  # yield类似Go的ch<-i，但更灵活
        # 函数在此暂停，等待下次迭代请求新值

# 创建生成器对象（函数不立即执行）
generator = count_to_five()
print(type(generator))  # <class 'generator'>

# 迭代获取值（类似Go的for range ch）
for num in generator:
    print(num)  # 输出: 1, 2, 3, 4, 5

# ============ yield的工作原理 ============
def simple_generator():
    """展示yield的执行流程"""
    print("开始执行")    # 第一次迭代时执行
    yield 1             # 返回1，暂停
    
    print("继续执行")    # 第二次迭代时执行
    yield 2             # 返回2，暂停
    
    print("最后执行")    # 第三次迭代时执行
    yield 3             # 返回3，完成

gen = simple_generator()
print(next(gen))  # 输出: 开始执行 然后 1
print(next(gen))  # 输出: 继续执行 然后 2
print(next(gen))  # 输出: 最后执行 然后 3
# print(next(gen))  # StopIteration异常

# ============ 生成器send方法 ============
def echo_generator():
    """接收发送的值并yield回去"""
    while True:
        received = yield  # 暂停并等待接收值
        print(f"收到: {received}")

gen = echo_generator()
next(gen)              # 启动生成器到第一个yield
gen.send("你好")       # 发送值，输出: 收到: 你好
gen.send("世界")       # 发送值，输出: 收到: 世界

# ============ throw和close方法 ============
def controlled_generator():
    """展示异常处理和关闭"""
    try:
        yield 1
        yield 2
        yield 3
    except ValueError:
        yield "捕获到ValueError"
    
    yield "完成"  # 这行不会执行，因为已关闭

gen = controlled_generator()
print(next(gen))          # 1
print(next(gen))          # 2
gen.throw(ValueError)     # 注入异常，输出: 捕获到ValueError
print(next(gen))          # StopIteration（生成器已关闭）

# 正确关闭生成器
gen2 = count_to_five()
print(next(gen2))  # 1
gen2.close()       # 关闭生成器
# print(next(gen2))  # StopIteration异常
