# ============ 类定义（对比Go的Struct + 方法） ============
# Go:
# type Person struct {
#     Name string
#     Age  int
# }
#
# func (p Person) Greet() string {
#     return "Hello, " + p.Name
# }

# Python:
class Person:
    """人类 - 类似Go的struct"""
    
    # 类属性（类似Go的struct字段）
    species = "Homo sapiens"    # 类变量（所有实例共享）
    
    # 构造函数（类似Go的工厂函数）
    def __init__(self, name, age):
        """
        __init__是构造函数
        self类似Go的this，但必须显式作为第一个参数
        """
        self.name = name        # 实例属性
        self.age = age
    
    # 方法定义
    def greet(self):
        """打招呼方法"""
        return f"你好，我是{self.name}"
    
    def have_birthday(self):
        """过生日，年龄+1"""
        self.age += 1
        return self.age

# 创建实例（类似Go的p := Person{Name: "张三", Age: 25}）
person = Person("张三", 25)

# 访问属性（Go用.，Python也用.）
print(person.name)          # 输出: 张三
print(person.greet())       # 输出: 你好，我是张三

# 调用方法
new_age = person.have_birthday()
print(f"现在{new_age}岁了")  # 输出: 现在26岁了

# ============ 继承（Go用组合，Python支持继承） ============
# Go:
# type Employee struct {
#     Person      // 嵌入（类似继承）
#     Company string
# }

# Python:
class Employee(Person):     # 继承Person
    """员工类"""
    
    def __init__(self, name, age, company, salary):
        # 调用父类构造函数（类似Go的嵌入struct初始化）
        super().__init__(name, age)
        self.company = company
        self.salary = salary
    
    # 方法重写（类似Go的方法重写）
    def greet(self):
        base = super().greet()      # 调用父类方法
        return f"{base}，我在{self.company}工作"

emp = Employee("李四", 30, "字节跳动", 50000)
print(emp.greet())          # 输出: 你好，我是李四，我在字节跳动工作
