# 极简梯度下降演示：亲眼看 x 一步步走到谷底
# 运行前先安装 numpy：pip install numpy
# 我们的"山谷"是最简单的损失函数 f(x) = (x-3)**2，谷底在 x=3
# 试一试：把 LEARNING_RATE 改成 1.0 再跑（来回蹦）；改成 1.01（越蹦越高，发散）
import numpy as np

LEARNING_RATE = 0.2   # 学习率：每步迈多大
STEPS = 15            # 总共走多少步


def f(x):
    # 损失函数：x 离 3 越远，损失越大
    return (x - 3) ** 2


def gradient(x):
    # 梯度：当前位置的"坡度"。f(x) = (x-3)^2 的坡度是 2*(x-3)
    # x 在 3 左边时它是负数（右边是下坡），在右边时是正数（左边是下坡）
    return 2 * (x - 3)


x = 0.0  # 起点：蒙着眼被放在山坡上
print(f"起点      x={x:.4f}  损失 f(x)={f(x):.4f}")
for step in range(1, STEPS + 1):
    # 每步只做一件事：探出当前坡度，朝它的反方向（下坡）挪一小步
    # "梯度乘学习率"就是这一步的长度和方向
    x = x - LEARNING_RATE * gradient(x)
    print(f"第{step:2d}步    x={x:.4f}  损失 f(x)={f(x):.6f}")

print("\nx 一路逼近 3、损失一路逼近 0 —— 这个循环，就是训练的全部秘密。")
