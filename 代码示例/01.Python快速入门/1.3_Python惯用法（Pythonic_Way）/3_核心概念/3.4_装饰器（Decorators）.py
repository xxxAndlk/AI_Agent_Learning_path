@timer
def slow_function():
    time.sleep(1)

# 等价于
slow_function = timer(slow_function)
