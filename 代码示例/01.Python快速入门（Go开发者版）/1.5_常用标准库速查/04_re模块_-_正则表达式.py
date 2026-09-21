import re

# 编译正则（推荐，可复用）
# Go: regexp.Compile()
pattern = re.compile(r"\d+")

# 查找所有匹配
# Go: FindAllString()
matches = pattern.findall("abc123def456")  # ['123', '456']

# 替换
# Go: ReplaceAllString()
result = pattern.sub("X", "abc123def456")  # abcXdefX

# 匹配判断
# Go: MatchString()
if pattern.search("contains123"):
    print("包含数字")
