# ============ 错误处理对比 ============
# Go: if err != nil { return err }
# Python: try/except
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        print(f"错误: {e}")
        return None
