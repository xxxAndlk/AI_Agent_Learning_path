# Python风格
try:
    result = do_something()
except SomeError as e:
    logger.error(f"Failed: {e}")
    return None
