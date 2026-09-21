# ============ 类类型注解 ============
from typing import Self

class Person:
    """带类型注解的类（类似Go的struct + 方法）"""
    
    # 类属性注解（类似Go的struct字段）
    species: str = "Homo sapiens"
    
    # 实例属性注解（类似Go的struct字段）
    name: str
    age: int
    
    # 构造函数（类似Go的工厂函数）
    def __init__(self, name: str, age: int) -> None:
        self.name = name          # 实例属性
        self.age = age
    
    # 实例方法（类似Go的方法）
    def greet(self) -> str:
        return f"你好，我是{self.name}"
    
    # 方法返回类型注解
    def have_birthday(self) -> int:
        self.age += 1
        return self.age
    
    # 类方法（类似Go的函数）
    @classmethod
    def create_infant(cls, name: str) -> "Person":
        """创建婴儿实例"""
        return cls(name, 0)
    
    # 静态方法（类似Go的包级函数）
    @staticmethod
    def validate_age(age: int) -> bool:
        """验证年龄是否有效"""
        return 0 <= age <= 150
    
    # 类型注解可以引用自身（类似Go的递归结构）
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Person):
            return NotImplemented
        return self.name == other.name and self.age == other.age

# 使用示例
person = Person("张三", 25)
print(person.greet())              # 类型检查器知道返回str
print(person.age)                  # 类型检查器知道是int

# 自我引用类型（Python 3.11+）
class Node:
    """链表节点"""
    value: int
    next: Optional["Node"] = None  # 引用自身，用字符串形式
    
    def __init__(self, value: int) -> None:
        self.value = value

# Python 3.11+ 也可以用Self类型
class TreeNode:
    """二叉树节点"""
    val: int
    left: Optional[Self] = None
    right: Optional[Self] = None
