# match-case 模式匹配
def classify_point(point: tuple[int, int]) -> str:
    match point:
        case (0, 0):
            return "原点"
        case (x, 0) if x > 0:
            return "正X轴"
        case (0, y) if y > 0:
            return "正Y轴"
        case (x, y) if x > 0 and y > 0:
            return "第一象限"
        case _:
            return "其他位置"

# 联合类型
def process_value(value: int | str) -> str:
    match value:
        case int():
            return f"整数: {value}"
        case str():
            return f"字符串: {value}"

# 改进的错误消息（Python 3.10+自动提供）
# 之前：SyntaxError: invalid syntax
# 现在：SyntaxError: expected ':'
