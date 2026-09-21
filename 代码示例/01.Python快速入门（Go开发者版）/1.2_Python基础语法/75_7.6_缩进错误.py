# 错误：混合使用Tab和空格（若if/y两行改用Tab缩进，与空格混用将抛出IndentationError）
def func():
    x = 1
    if True:  # 此两行原为Tab缩进（演示Tab/空格混用错误）
        y = 2
