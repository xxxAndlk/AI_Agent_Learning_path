# 问题：复杂reduce难以理解
result = reduce(lambda x, y: (x[0]+y, x[1]+1), data, (0, 0))

# 解决方案：使用显式循环或命名函数
def compute_sum_and_count(data):
    total = 0
    count = 0
    for item in data:
        total += item
        count += 1
    return (total, count)
