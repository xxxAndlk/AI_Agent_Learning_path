# ============ 基本类型注解 ============
# Python: 类型注解是可选的，不会影响运行时
# Go: 类型声明是强制的，编译时检查

# 变量类型注解（类似Go的 var x int = 10）
x: int = 10           # 声明x是int类型
y: str = "hello"      # 声明y是str类型
z: float = 3.14       # 声明z是float类型
flag: bool = True     # 声明flag是bool类型

# Python没有类型注解也能运行
x = 10                # 完全合法

# Go必须有类型声明
# var x int = 10      # 编译错误！
