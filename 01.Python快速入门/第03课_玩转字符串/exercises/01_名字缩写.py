# 01_名字缩写.py —— 输入英文全名，输出首字母缩写（如 zhang san feng -> ZSF）
# 思路：split() 按空格切成一个个词，每个词的 [0] 号字符是首字母，upper() 变大写
# 注意：这里假设名字正好三个词。更通用的写法要等第 6 课的 for 循环。

full_name = input("请输入你的英文全名：")
words = full_name.split()             # 不写分隔符，默认按空格切

initials = words[0][0].upper() + words[1][0].upper() + words[2][0].upper()
print("你的名字缩写是：" + initials)
