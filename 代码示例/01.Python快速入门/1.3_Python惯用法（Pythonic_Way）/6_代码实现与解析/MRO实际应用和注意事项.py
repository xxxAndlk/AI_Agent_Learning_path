# LoggerMixin: 提供日志功能的混合类
class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {message}")

    def save(self):
        self.log(f"Saving {self.__class__.__name__}")

# SerializableMixin: 提供序列化功能的混合类
class SerializableMixin:
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

# 使用Mixin
class User(LoggerMixin, SerializableMixin):
    def __init__(self, name):
        self.name = name

    def save(self):
        # 调用Mixin的save之前先记录日志
        self.log(f"About to save user: {self.name}")
        super().save()

user = User("Alice")
user.save()
# 输出:
# [LOG] About to save user: Alice
# [LOG] Saving User

print(user.to_dict())
# {'name': 'Alice'}
