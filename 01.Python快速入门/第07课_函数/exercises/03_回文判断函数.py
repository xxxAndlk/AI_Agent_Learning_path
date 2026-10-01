# 03_回文判断函数.py —— 练习 3 参考答案
# 函数只回答"是不是"（True/False），怎么说话是外面的事——各干各的

def is_palind(text):
    # [::-1] 是第 3 课见过的反转写法：倒着念一遍，和原词比
    return text == text[::-1]


word = input("输入一个词，我看看它是不是回文：")

if is_palind(word):
    print(word + " 是回文！倒着念也一模一样。")
else:
    print(word + " 不是回文，倒过来是 " + word[::-1] + "。")
