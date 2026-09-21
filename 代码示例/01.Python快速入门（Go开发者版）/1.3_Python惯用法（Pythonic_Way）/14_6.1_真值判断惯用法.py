# 1. 真值判断（不需要显式比较）
# 不推荐：if x == True:
# 推荐：
x = True
if x:           # Pythonic
    print("True")

# 空值判断
# Go: if s != ""
# Python:
s = "hello"
if s:           # 非空字符串为True
    print("字符串非空")

items = []
if not items:   # 空列表为False
    print("列表为空")
