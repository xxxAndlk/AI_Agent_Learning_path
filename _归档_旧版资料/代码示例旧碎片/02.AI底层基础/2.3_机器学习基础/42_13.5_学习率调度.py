import matplotlib.pyplot as plt
import numpy as np

# 不同调度策略
epochs = np.arange(100)

# 1. 固定学习率
def fixed_schedule(epoch, initial_lr=0.1):
    return initial_lr

# 2. 阶跃衰减
def step_decay(epoch, initial_lr=0.1, drop_every=10, drop_rate=0.5):
    return initial_lr * (drop_rate ** (epoch // drop_every))

# 3. 指数衰减
def exponential_decay(epoch, initial_lr=0.1, decay_rate=0.95):
    return initial_lr * (decay_rate ** epoch)

# 4. 余弦退火
def cosine_annealing(epoch, initial_lr=0.1, T_max=100):
    return initial_lr * (1 + np.cos(np.pi * epoch / T_max)) / 2

plt.figure(figsize=(12, 6))
plt.plot(epochs, [fixed_schedule(e) for e in epochs], label='固定学习率')
plt.plot(epochs, [step_decay(e) for e in epochs], label='阶跃衰减')
plt.plot(epochs, [exponential_decay(e) for e in epochs], label='指数衰减')
plt.plot(epochs, [cosine_annealing(e) for e in epochs], label='余弦退火')
plt.xlabel('Epoch')
plt.ylabel('学习率')
plt.title('学习率调度策略对比')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('learning_rate_schedules.png', dpi=150)
plt.show()
