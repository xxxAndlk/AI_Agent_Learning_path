"""练习1参考答案：线程小演示
起两个线程各数各的，主线程 join 等它们收工，观察输出是交替的。
"""
import threading
import time


def count_animals(name, times):
    # time.sleep 模拟"等待"，也让出 CPU，两个线程的交替会更明显
    for i in range(1, times + 1):
        print(f"{name}: 第 {i} 只")
        time.sleep(0.2)


# 注意：Thread 的 target 传函数名，不带括号；带括号就变成立刻调用了
t1 = threading.Thread(target=count_animals, args=("小羊", 5))
t2 = threading.Thread(target=count_animals, args=("小牛", 5))

t1.start()
t2.start()

# join 的意思：主线程在这里等这两个线程干完再往下走
t1.join()
t2.join()

print("都数完了！多跑几次，你会发现两种输出的先后顺序并不固定。")
