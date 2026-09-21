# ============ 1. match-case 模式匹配 ============
def classify_command(command: str) -> str:
    """命令分类：使用match-case进行模式匹配
    
    Python 3.10引入的match-case比传统if-elif-else更强大
    
    参数:
        command: 用户输入的命令
    返回:
        分类结果
    """
    match command.split():
        # 匹配单词命令
        case ["quit"]:
            return "退出程序"
        
        # 匹配带参数的命令
        case ["load", filename]:
            return f"加载文件: {filename}"
        
        case ["save", filename]:
            return f"保存文件: {filename}"
        
        # 匹配多个参数
        case ["compute", x, y]:
            return f"计算: {x} + {y} = {int(x) + int(y)}"
        
        # 使用守卫条件（guard）
        case ["process", n] if int(n) > 100:
            return f"处理大量数据: {n}条"
        
        case ["process", n]:
            return f"处理少量数据: {n}条"
        
        # 匹配任意内容
        case _:
            return "未知命令"

# ============ 2. 数据结构模式匹配 ============
def analyze_point(point: tuple) -> str:
    """分析点坐标：匹配不同类型的元组结构
    
    参数:
        point: (x, y) 或 (x, y, label) 格式的元组
    返回:
        分析结果
    """
    match point:
        case (0, 0):
            return "原点"
        
        case (x, 0):
            return f"X轴上的点: ({x}, 0)"
        
        case (0, y):
            return f"Y轴上的点: (0, {y})"
        
        case (x, y, label):
            return f"带标签的点: ({x}, {y}), 标签={label}"
        
        case (x, y):
            return f"平面点: ({x}, {y})"
        
        case _:
            return "无效坐标"

# ============ 3. 联合类型 ============
# Python 3.10前：Union[int, str]
# Python 3.10后：int | str

def process_value(value: int | str | float) -> str:
    """处理不同类型的值
    
    使用联合类型简化类型提示
    
    参数:
        value: 整数、字符串或浮点数
    返回:
        格式化后的字符串
    """
    match value:
        case int():
            return f"整数: {value}"
        case str() if value.isdigit():
            return f"数字字符串: {value}"
        case str():
            return f"普通字符串: {value}"
        case float():
            return f"浮点数: {value}"

# ============ 4. 类型别名 ============
# 使用type创建类型别名
type Vector2D = tuple[float, float]
type Vector3D = tuple[float, float, float]
type Matrix = list[list[float]]

def normalize_vector(v: Vector2D) -> Vector2D:
    """归一化二维向量"""
    import math
    x, y = v
    length = math.sqrt(x*x + y*y)
    if length == 0:
        return (0.0, 0.0)
    return (x/length, y/length)

# ============ 5. 改进的错误消息 ============
# Python 3.10提供了更精确的错误提示
# 之前: "SyntaxError: invalid syntax"
# 现在: "SyntaxError: expected ':'"

# 演示：尝试执行有语法错误的代码会得到更友好的错误消息

# ============ 6. 严格参数规范 ============
# Python 3.8+: 使用*分隔位置参数和关键字参数
def func(pos1, pos2, /, *, kwonly1, kwonly2):
    """严格参数规范函数
    
    / 左侧只能是位置参数
    * 右侧只能是关键字参数
    """
    return f"pos={pos1},{pos2}, kw={kwonly1},{kwonly2}"

# ============ 7. match-case 在AI中的应用 ============
def classify_prediction(prediction: dict) -> str:
    """AI模型预测结果分类
    
    实际AI应用中，可以用match-case处理不同的预测结果
    """
    match prediction:
        case {"class": "cat", "confidence": c} if c > 0.9:
            return "高置信度：猫"
        
        case {"class": "cat", "confidence": c}:
            return f"可能是猫 (置信度: {c:.2f})"
        
        case {"class": "dog", "confidence": c} if c > 0.9:
            return "高置信度：狗"
        
        case {"class": unknown, "confidence": c}:
            return f"未知类别: {unknown} (置信度: {c:.2f})"
        
        case _:
            return "无法识别"

# ============ 主程序入口 ============
if __name__ == "__main__":
    # 测试match-case
    print("命令分类:")
    print(classify_command("load data.csv"))
    print(classify_command("compute 10 20"))
    print(classify_command("unknown"))
    
    print("\n点分析:")
    print(analyze_point((0, 0)))
    print(analyze_point((5, 0)))
    print(analyze_point((3, 4, "important")))
    
    print("\n值处理:")
    print(process_value(42))
    print(process_value("123"))
    print(process_value(3.14))
    
    print("\n向量归一化:")
    v = (3.0, 4.0)
    normalized = normalize_vector(v)
    print(f"原始: {v} -> 归一化: {normalized}")
    
    print("\n函数调用:")
    # 使用关键字参数
    result = func(1, 2, kwonly1=3, kwonly2=4)
    print(result)
    
    print("\nAI预测分类:")
    pred1 = {"class": "cat", "confidence": 0.95}
    pred2 = {"class": "dog", "confidence": 0.6}
    print(classify_prediction(pred1))
    print(classify_prediction(pred2))
