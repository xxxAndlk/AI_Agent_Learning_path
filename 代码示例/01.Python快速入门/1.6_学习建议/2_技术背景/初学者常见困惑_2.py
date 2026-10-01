# Python风格：EAFP——先尝试执行，出错再兜底（对比 LBYL：先检查再执行）
def do_task():
    try:
        result = do_something()
    except SomeError as e:
        logger.error(f"Failed: {e}")
        return None
    return result
