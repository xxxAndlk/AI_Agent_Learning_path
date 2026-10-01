# 不使用super()的父类调用（不推荐）
class Child(Parent):
    def method(self):
        Parent.method(self)  # 硬编码父类，MRO失效
        # 其他逻辑

# 使用super()的正确方式（推荐）
class Child(Parent):
    def method(self):
        # 先执行父类逻辑
        super().method()
        # 再执行子类逻辑
        print("Child additional logic")
