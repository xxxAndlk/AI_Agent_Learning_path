# 13. 字符串方法链
text = "  Hello, World!  "
# 不推荐
# text = text.strip()
# text = text.lower()
# text = text.replace('!', '?')

# 推荐（Pythonic）
cleaned = text.strip().lower().replace('!', '?')
