import re

# 编译正则（推荐，可复用）
pattern = re.compile(r"\d+")

# 查找所有匹配
matches = pattern.findall("abc123def456")  # ['123', '456']

# 替换
result = pattern.sub("X", "abc123def456")  # abcXdefX

# 匹配判断
if pattern.search("contains123"):
    print("包含数字")
