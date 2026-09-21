class Descriptor:
    def __get__(self, obj, objtype=None):
        return self.value
    
    def __set__(self, obj, value):
        self.value = value
    
    def __delete__(self, obj):
        del self.value

class MyClass:
    attr = Descriptor()  # attr现在是描述符
