# 练习 2 参考答案：摔不坏的计算器
# 两种事故分别接：文字转不成数字是 ValueError，除数是 0 是 ZeroDivisionError。
# 注意 except 写了具体类型，别用光秃秃的 except 把所有错误都吞掉。

text_a = input("被除数：")
text_b = input("除数：")

try:
    a = int(text_a)
    b = int(text_b)
    print("结果是", a / b)
except ValueError:
    print("这两个格子里得填整数，比如 8 和 2。")
except ZeroDivisionError:
    print("除数不能是 0，这个数学老师也帮不了。")
