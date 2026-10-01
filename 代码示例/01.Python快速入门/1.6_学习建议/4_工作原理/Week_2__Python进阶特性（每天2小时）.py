# 列表推导
squares = [x**2 for x in range(10)]

# 字典推导
word_lengths = {word: len(word) for word in ["hello", "world"]}

# 生成器表达式
total = sum(x**2 for x in range(1000000))  # 内存高效
