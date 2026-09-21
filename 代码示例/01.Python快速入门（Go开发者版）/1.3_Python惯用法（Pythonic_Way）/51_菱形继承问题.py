# 菱形继承示例
class Animal:
    def speak(self):
        print("Animal speaks")

class Dog(Animal):
    def speak(self):
        print("Dog barks")

class Cat(Animal):
    def speak(self):
        print("Cat meows")

class Pet(Dog, Cat):  # 菱形继承
    pass

pet = Pet()
pet.speak()  # 输出什么？

# 查看MRO顺序
print(Pet.__mro__)
# 输出: (<class '__main__.Pet'>, <class '__main__.Dog'>, 
#       <class '__main__.Cat'>, <class '__main__.Animal'>, <class 'object'>)
