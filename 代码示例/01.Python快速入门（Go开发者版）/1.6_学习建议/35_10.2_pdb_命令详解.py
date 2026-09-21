# pdb 常用命令（调试时输入）
"""
n (next)          - 执行下一行，不进入函数
s (step)          - 执行下一行，进入函数
c (continue)      - 继续执行到下一个断点
p <expr>          - 打印表达式的值
pp <expr>         - 美化打印表达式的值
l (list)          - 显示当前代码上下文
w (where)         - 显示调用栈
u (up)            - 向上移动调用栈
d (down)          - 向下移动调用栈
b (break)         - 设置断点
cl (clear)        - 清除断点
r (return)        - 执行到函数返回
q (quit)          - 退出调试器
"""

# 示例：调试计算函数
def calculate(items: list[int]) -> int:
    total = 0
    for i, item in enumerate(items):
        total += item
        # 在这里查看 total 和 i 的值
        breakpoint()  # 输入 p total, p i 查看
    return total
