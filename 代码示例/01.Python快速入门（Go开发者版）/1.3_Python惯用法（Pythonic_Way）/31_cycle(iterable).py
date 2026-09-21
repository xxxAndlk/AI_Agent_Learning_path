import itertools

# 循环遍历颜色
colors = ['红', '绿', '蓝']
color_cycle = itertools.cycle(colors)

# 获取前7个颜色
for i in range(7):
    print(next(color_cycle), end=' ')  # 输出: 红 绿 蓝 红 绿 蓝 红
print()

# 常用场景：轮询调度
tasks = ['taskA', 'taskB', 'taskC']
scheduler = itertools.cycle(tasks)

for _ in range(5):
    print(f"执行: {next(scheduler)}")
# 输出:
# 执行: taskA
# 执行: taskB
# 执行: taskC
# 执行: taskA
# 执行: taskB
