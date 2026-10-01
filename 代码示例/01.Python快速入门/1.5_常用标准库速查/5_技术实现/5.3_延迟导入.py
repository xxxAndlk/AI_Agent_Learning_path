# 不推荐：在模块级别导入
def process_data():
    import heavy_module  # 延迟到函数调用时导入
    return heavy_module.process()
