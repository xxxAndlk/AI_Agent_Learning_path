# 错误：参数顺序不对
@repeat(3)  # 期望重复3次
@log       # 期望记录日志
def process():
    pass
# 实际上：先执行log，再执行repeat(3)
# 想要的效果相反，应该调整顺序
