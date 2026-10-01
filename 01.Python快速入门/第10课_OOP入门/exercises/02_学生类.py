# 练习2参考答案：学生类
# 易错点：average() 要用 return 把平均分交回去，光 print 别的代码拿不到这个数

class Student:
    def __init__(self, name):
        self.name = name
        self.scores = []   # 成绩列表，出厂时一门都没有

    def add_score(self, score):
        self.scores.append(score)

    def average(self):
        # 一门成绩都没有就做除法，程序会崩，先挡住
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)


stu = Student("小明")
stu.add_score(90)
stu.add_score(85)
stu.add_score(78)

print(stu.name, "的平均分：", stu.average())
