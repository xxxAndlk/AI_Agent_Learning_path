# Python Lambda表达式
# Go匿名函数:
# add := func(a, b int) int {
#     return a + b
# }

# Python:
add = lambda a, b: a + b
print(add(2, 3))  # 输出: 5

# ============ 关键区别对比 ============

# 1. 语法简洁性
# Python: 单行表达式，简洁直接
# Go: 需要func关键字，函数体可以是多行语句块

# Python Lambda
multiply = lambda x, y: x * y

# Go匿名函数（需要完整函数语法）
# multiply := func(x, y int) int {
#     return x * y
# }

# 2. 函数体限制
# Python: 只能是单一表达式，不能包含语句
# Go: 可以包含多条语句

# Python（错误示例，会报语法错误）
# bad_lambda = lambda x: if x > 0: return x else: return -x

# Python正确写法（三元表达式）
abs_lambda = lambda x: x if x > 0 else -x

# Go可以实现更复杂的逻辑
# abs := func(x int) int {
#     if x > 0 {
#         return x
#     }
#     return -x
# }

# 3. 闭包捕获
# 两者都支持闭包，捕获外部变量

# Python闭包示例
def make_counter():
    count = 0
    # lambda捕获外部变量count的引用
    return lambda: count  # 返回计数器函数

def make_counter_correct():
    count = 0
    def counter():
        nonlocal count  # 使用nonlocal声明修改外层变量
        count += 1
        return count
    return counter

# 4. 多返回值
# Python Lambda不支持多返回值（因为只能是一个表达式）
# Go匿名函数可以返回多个值

# Python需要返回元组模拟
result = lambda x: (x * 2, x * 3)
print(result(5))  # 输出: (10, 15)

# 5. 类型声明
# Python: 动态类型，无需声明参数和返回类型
# Go: 静态类型，需要声明参数和返回类型

# Python（无类型声明）
add = lambda a, b: a + b
