# 陷阱1：动态类型的隐式转换
x = "10"
y = 5
# x + y  # TypeError! Python不会自动转换

# Go中 string + int 是编译错误
# Python中也是错误，但在运行时发现

# 陷阱2：可变默认参数
def append_item(item, lst=[]):  # 危险！
    lst.append(item)
    return lst

# 正确写法
def append_item_safe(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
