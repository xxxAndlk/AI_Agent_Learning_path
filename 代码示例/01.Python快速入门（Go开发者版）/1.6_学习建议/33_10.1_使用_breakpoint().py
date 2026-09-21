# Python 3.7+ 引入了 breakpoint() 内置函数
# 默认调用 pdb，但可以配置其他调试器

def process_data(data: list[dict]) -> dict:
    """处理数据的函数"""
    result = {}
    
    for item in data:
        key = item.get("category", "unknown")
        value = item.get("value", 0)
        
        # 在这里设置断点
        breakpoint()  # 代码执行到这里会暂停，进入调试模式
        
        if key in result:
            result[key] += value
        else:
            result[key] = value
    
    return result

# 使用方法：
# 1. 运行脚本
# 2. 代码执行到 breakpoint() 时会暂停
# 3. 在 (Pdb) 提示符下输入命令进行调试
