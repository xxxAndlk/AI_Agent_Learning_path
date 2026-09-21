# match-case不进行类型检查，只进行结构匹配
match value:
    case int():  # 检查是否为int类型
        # 但不保证是int，可能是bool（bool是int子类）
        pass

# 显式检查bool
match value:
    case bool():
        return "是布尔值"
    case int():
        return "是整数"
