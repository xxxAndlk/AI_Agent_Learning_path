# Python 调试 vs Go 调试

# 1. 断点设置
# Go: dlv break main.go:10
# Python: breakpoint() 或 IDE 点击

# 2. 查看变量
# Go: p variable
# Python: p variable 或 print(variable)

# 3. 调用栈
# Go: bt (backtrace)
# Python: w (where)

# 4. 条件断点
# Go: cond breakpoint_name condition
# Python: 在 IDE 右键断点 -> 编辑条件

# 5. 调试时执行代码
# Go: call function_name()
# Python: !code 或直接调用
