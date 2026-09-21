# Python 3.12 之前的错误消息
# TypeError: unsupported operand type(s) for +: 'int' and 'str'

# Python 3.12+ 的改进错误消息
# TypeError: unsupported operand type(s) for +: 'int' and 'str'. 
# Did you mean: 'int + int' or 'str + str'?

# 另一个例子
result = "hello" + 123
# 错误消息现在会提示：Did you mean: "hello" + "123"?

# 导入错误改进
import non_existent_module
# 错误消息会建议相似的可用模块
