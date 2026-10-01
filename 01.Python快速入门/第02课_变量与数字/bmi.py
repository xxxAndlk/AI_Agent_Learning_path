# bmi.py —— 输入身高体重，算出 BMI
# 运行方法（在终端里）：python bmi.py

print("BMI 计算器")
print("-" * 20)  # 文字乘数字 = 重复 20 遍，拼出一条分隔线

# input 读进来的永远是文字，身高体重都要参与运算，
# 所以直接在 input 外面套一层 float，读进来立刻转成小数
height = float(input("你的身高是多少米？（例如 1.75）"))
weight = float(input("你的体重是多少公斤？（例如 65）"))

# 括号不能省：先算身高的平方，再做除法
bmi = weight / (height ** 2)

# bmi 是数字，拼进一句话前要用 str() 变身
print("你的 BMI 是：" + str(bmi))
print("一般来说，BMI 在 18.5 到 24 之间属于正常范围。")

# 学完第 6 课回来改：用 if 让程序根据 bmi 的值
# 自动说出"偏瘦/正常/偏胖"，这里故意先不写
