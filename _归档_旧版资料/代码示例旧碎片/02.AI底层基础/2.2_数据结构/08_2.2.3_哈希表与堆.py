class Stack:
    """栈类：后进先出（LIFO）的数据结构
    
    栈是一种受限的线性表，只允许在一端进行插入和删除操作。
    这一端称为栈顶，另一端称为栈底。
    """
    
    def __init__(self):
        """初始化空栈"""
        self.items = []                # 使用Python列表存储栈元素
    
    def is_empty(self):
        """判断栈是否为空"""
        return len(self.items) == 0    # 列表为空则栈为空
    
    def push(self, item):
        """压栈：将元素添加到栈顶
        
        时间复杂度: O(1)
        """
        self.items.append(item)        # 列表末尾添加元素，即栈顶
    
    def pop(self):
        """弹栈：移除并返回栈顶元素
        
        时间复杂度: O(1)
        返回值: 栈顶元素，如果栈空则返回None
        """
        if self.is_empty():
            return None
        return self.items.pop()        # 移除并返回列表末尾元素
    
    def peek(self):
        """查看栈顶元素但不移除
        
        时间复杂度: O(1)
        """
        return self.items[-1] if self.items else None
    
    def size(self):
        """返回栈的大小"""
        return len(self.items)


# 单调栈实现：用于解决Next Greater Element等问题的神器
class MonotonicStack:
    """单调栈类：栈内元素保持单调递增或递减
    
    应用场景：
    - 每日温度（找下一个更高温度）
    - 下一个更大元素
    - 柱状图中最大的矩形
    """
    
    def __init__(self):
        """初始化空单调栈"""
        self.stack = []                # 存储(值, 索引)元组
    
    def next_greater(self, nums):
        """计算每个元素下一个更大元素的位置
        
        参数:
            nums: 输入数组
        返回值:
            数组，每个位置是下一个更大元素的索引，不存在则为-1
        
        时间复杂度: O(n)，每个元素最多入栈和出栈一次
        空间复杂度: O(n)
        """
        n = len(nums)
        result = [-1] * n              # 初始化结果数组
        self.stack = []                # 清空栈，存储索引
        
        for i in range(n):
            # 当前元素大于栈顶元素时，找到下一个更大元素
            while self.stack and nums[i] > nums[self.stack[-1]]:
                prev_index = self.stack.pop()
                result[prev_index] = i # 记录下一个更大元素的位置
            self.stack.append(i)       # 当前元素入栈
        
        return result


# 括号匹配：栈的经典应用
def is_valid_parentheses(s):
    """验证括号字符串是否有效
    
    有效括号条件：
    - 左括号必须用相同类型的右括号闭合
    - 左括号必须以正确的顺序闭合
    
    示例:
    - "()" -> True
    - "()[]{}" -> True
    - "(]" -> False
    - "([)]" -> False
    
    参数:
        s: 括号字符串
    返回值:
        布尔值，表示是否有效
    
    时间复杂度: O(n)
    空间复杂度: O(n)
    """
    if not s:
        return True
    
    stack = []                         # 存储左括号
    bracket_map = {                    # 右括号到左括号的映射
        ')': '(',
        ']': '[',
        '}': '{'
    }
    
    for char in s:
        if char in bracket_map:
            # 遇到右括号，检查栈顶是否有对应的左括号
            if not stack or stack[-1] != bracket_map[char]:
                return False          # 不匹配
            stack.pop()               # 匹配成功，出栈
        else:
            # 遇到左括号，入栈
            stack.append(char)
    
    return len(stack) == 0            # 栈为空则完全匹配


# 表达式求值：中缀转后缀并计算
def evaluate_expression(expression):
    """计算中缀表达式的值（支持加减乘除和括号）
    
    算法步骤：
    1. 将中缀表达式转换为后缀表达式（逆波兰 notation）
    2. 使用栈计算后缀表达式的值
    
    示例:
    - "3 + 4 * 2" -> 11
    - "(3 + 4) * 2" -> 14
    
    参数:
        expression: 中缀表达式字符串
    返回值:
        计算结果
    
    时间复杂度: O(n)
    空间复杂度: O(n)
    """
    # 定义运算符优先级
    prec = {'+': 1, '-': 1, '*': 2, '/': 2}
    
    def to_postfix(tokens):
        """中缀转后缀"""
        output = []                    # 后缀表达式结果
        ops_stack = []                 # 运算符栈
        
        for token in tokens:
            if token.isdigit():
                # 数字直接输出
                output.append(token)
            elif token == '(':
                # 左括号入栈
                ops_stack.append(token)
            elif token == ')':
                # 右括号，弹出直到遇到左括号
                while ops_stack and ops_stack[-1] != '(':
                    output.append(ops_stack.pop())
                ops_stack.pop()        # 弹出左括号
            else:
                # 运算符：弹出优先级 >= 当前运算符的
                while (ops_stack and ops_stack[-1] != '(' and 
                       prec.get(ops_stack[-1], 0) >= prec[token]):
                    output.append(ops_stack.pop())
                ops_stack.append(token)
        
        # 剩余运算符全部弹出
        while ops_stack:
            output.append(ops_stack.pop())
        
        return output
    
    def evaluate_postfix(postfix):
        """计算后缀表达式"""
        eval_stack = []                # 计算栈
        
        for token in postfix:
            if token.isdigit():
                eval_stack.append(int(token))
            else:
                # 弹出两个操作数
                b = eval_stack.pop()
                a = eval_stack.pop()
                if token == '+':
                    eval_stack.append(a + b)
                elif token == '-':
                    eval_stack.append(a - b)
                elif token == '*':
                    eval_stack.append(a * b)
                elif token == '/':
                    # Python整除，向零取整
                    eval_stack.append(int(a / b))
        
        return eval_stack[0]
    
    # 解析表达式为token列表
    import re
    tokens = re.findall(r'\d+|[+\-*/()]', expression.replace(' ', ''))
    postfix = to_postfix(tokens)
    return evaluate_postfix(postfix)


if __name__ == "__main__":
    # 栈基本操作
    stack = Stack()
    stack.push(1)
    stack.push(2)
    stack.push(3)
    print("栈顶元素:", stack.peek())   # 3
    print("弹出元素:", stack.pop())    # 3
    print("栈大小:", stack.size())     # 2
    
    # 单调栈应用：下一个更大元素
    nums = [2, 1, 2, 4, 3]
    mono = MonotonicStack()
    result = mono.next_greater(nums)
    print("下一个更大元素位置:", result)  # [3, 2, 3, -1, -1]
    
    # 括号匹配
    print("括号匹配:", is_valid_parentheses("()[]{}"))  # True
    print("括号匹配:", is_valid_parentheses("([)]"))    # False
    
    # 表达式求值
    print("表达式求值:", evaluate_expression("3+4*2"))     # 11
    print("表达式求值:", evaluate_expression("(3+4)*2"))  # 14
