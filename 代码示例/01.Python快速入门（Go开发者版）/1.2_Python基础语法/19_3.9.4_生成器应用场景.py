# ============ 内存优化对比 ============
import sys

# 场景：处理100万个用户数据

# 方法1：一次性加载到列表
def load_all_users_list():
    """所有用户加载到列表 - 占用大量内存"""
    return [{"id": i, "name": f"User{i}"} for i in range(1000000)]

# 方法2：使用生成器（内存友好）
def load_users_generator():
    """按需生成用户 - 极小内存占用"""
    for i in range(1000000):
        yield {"id": i, "name": f"User{i}"}

# 对比内存占用
all_users = load_all_users_list()
users_gen = load_users_generator()

print(f"列表内存: {sys.getsizeof(all_users)} bytes")
print(f"生成器内存: {sys.getsizeof(users_gen)} bytes")

# 实际处理：只需要前10个用户
users_gen2 = load_users_generator()
first_10 = []
for i, user in enumerate(users_gen2):
    if i >= 10:
        break
    first_10.append(user)

# 只有前10个用户被"实例化"，其余仍是惰性状态
print(f"实际处理: {len(first_10)} 个用户")
print(f"可用内存: {first_10}")

# ============ 大数据处理管道 ============
def process_large_dataset():
    """
    大数据处理管道的理想模式：
    1. 生成器读取数据（不占内存）
    2. 生成器过滤数据
    3. 生成器转换数据
    4. 最终才聚合结果
    """
    # 模拟读取1000万条记录
    raw_data = ({"id": i, "value": i*2} for i in range(10000000))
    
    # 过滤：只保留value > 1000的
    filtered = (r for r in raw_data if r["value"] > 1000)
    
    # 转换：添加新字段
    transformed = ({**r, "doubled": r["value"]*2} for r in filtered)
    
    # 取前1000条
    limited = []
    for i, item in enumerate(transformed):
        if i >= 1000:
            break
        limited.append(item)
    
    return limited

# 即使处理1000万条数据，内存占用也很小
result = process_large_dataset()
print(f"处理完成，结果数量: {len(result)}")
