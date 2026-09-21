# 根据需求调整装饰器顺序
@log        # 外层：先记录日志
@repeat(3)  # 内层：重复执行
def process():
    pass
