# 练习1参考答案：狗狗类
# 易错点：bark 定义时别忘了 self——Python 调用时会偷偷把对象塞进第一个参数

class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def bark(self):
        print(f"汪汪，我是{self.name}！")


dog1 = Dog("旺财", "柴犬")
dog2 = Dog("豆豆", "柯基")

dog1.bark()
dog2.bark()

# 属性各归各的：改这只不影响那只
print(dog1.name, "是一只", dog1.breed)
print(dog2.name, "是一只", dog2.breed)
