# 问题: 中文乱码
with open("file.txt") as f:  # 默认编码可能不是utf-8
    content = f.read()

# 解决: 始终指定编码
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 不知道编码时，使用chardet检测（第三方库）
# pip install chardet
import chardet
with open("file.txt", "rb") as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']
