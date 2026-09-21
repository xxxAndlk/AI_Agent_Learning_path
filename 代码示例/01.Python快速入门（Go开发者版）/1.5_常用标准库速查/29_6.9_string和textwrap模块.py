"""
字符串处理工具 - 对比Go的strings和fmt包
"""

import string
import textwrap
import re

# ============ string模块 - 字符串常量 ============
# Go: strings包

# 常用常量
print(f"小写字母: {string.ascii_lowercase}")   # abcdefghijklmnopqrstuvwxyz
print(f"大写字母: {string.ascii_uppercase}")   # ABCDEFGHIJKLMNOPQRSTUVWXYZ
print(f"字母: {string.ascii_letters}")         # 包含大小写
print(f"数字: {string.digits}")                # 0123456789
print(f"十六进制: {string.hexdigits}")         # 0-9a-fA-F
print(f"标点: {string.punctuation}")           # 所有标点符号
print(f"空白符: {string.whitespace}")          # 空格、Tab等

# 判断字符类别
# Go: unicode.IsLetter(), unicode.IsDigit()
print(f"是字母: {'A'.isalpha()}")              # True
print(f"是数字: {'123'.isdigit()}")            # True
print(f"是字母数字: {'abc123'.isalnum()}")     # True
print(f"是小写: {'abc'.islower()}")            # True
print(f"是标题格式: {'Hello World'.istitle()}") # True

# 字符串转换
s = "Hello World"
print(f"首字母大写: {s.capitalize()}")          # Hello world
print(f"小写: {s.lower()}")                     # hello world
print(f"大写: {s.upper()}")                     # HELLO WORLD
print(f"标题格式: {s.title()}")                 # Hello World
print(f"大小写交换: {s.swapcase()}")            # hELLO wORLD

# 填充和对齐
# Go: 使用fmt.Sprintf %-10s等
s = "Hello"
print(f"左对齐: {s.ljust(10)}")       # "Hello     "
print(f"右对齐: {s.rjust(10)}")       # "     Hello"
print(f"居中: {s.center(10)}")        # "  Hello   "
print(f"填充0: {s.zfill(10)}")        # "00000Hello"

# 去除空白
# Go: strings.TrimSpace()
s = "  Hello World  "
print(f"去除两端: '{s.strip()}'")        # "Hello World"
print(f"去除左: '{s.lstrip()}'")         # "Hello World  "
print(f"去除右: '{s.rstrip()}'")         # "  Hello World"

# 分割和连接
# Go: strings.Split(), strings.Join()
s = "a,b,c,d"
print(f"分割: {s.split(',')}")          # ['a', 'b', 'c', 'd']
print(f"分割N次: {s.split(',', 2)}")    # ['a', 'b', 'c,d']

parts = ['a', 'b', 'c']
print(f"连接: {','.join(parts)}")       # a,b,c

# 替换
# Go: strings.ReplaceAll()
s = "hello world"
print(f"替换: {s.replace('world', 'python')}")  # hello python
print(f"替换N次: {s.replace('o', 'X', 1)}")     # hellX world

# 查找
# Go: strings.Contains(), strings.Index()
s = "Hello World"
print(f"包含: {'World' in s}")           # True
print(f"查找位置: {s.find('World')}")    # 6
print(f"计数: {s.count('l')}")           # 3
print(f"开头: {s.startswith('Hello')}")  # True
print(f"结尾: {s.endswith('World')}")    # True

# ============ textwrap模块 - 文本格式化 ============
# Go: 需要手动实现或使用第三方库

# 缩进
text = """第一行
第二行
第三行"""

# 为每行添加相同前缀
indented = textwrap.indent(text, "    ")
print(indented)
#     第一行
#     第二行
#     第三行

# 条件缩进（仅缩进非空行）
indented = textwrap.indent(text, ">>> ", predicate=lambda line: line.strip())
print(indented)

# 填充文本（指定宽度）
text = "这是一个很长的段落，我们需要把它填充到指定的宽度，以便于显示。"
wrapped = textwrap.fill(text, width=20)
print(wrapped)
# 这是一个很长
# 的段落，我们需
# 要把它填充到指
# 定的宽度，以便
# 于显示。

# 包裹文本（返回行列表）
wrapped = textwrap.wrap(text, width=30)
print(wrapped)  # 列表形式

# 移除缩进
indented_text = """    首行有缩进
    第二行
    第三行"""
dedented = textwrap.dedent(indented_text)
print(dedented)

# 缩短文本（添加省略号）
text = "这是一个很长的文本，我们可以把它缩短显示。"
shortened = textwrap.shorten(text, width=20, placeholder="...")
print(shortened)  # 这是一个很长...

# 全部折叠（将空白压缩为单空格）
whitespace_text = "文本    有\n\n很多  空白"
folded = textwrap.fold(whitespace_text)
print(folded)  # 文本 有 很多 空白

# ============ 实际应用示例 ============

# 生成表格
def create_table(headers, rows):
    """创建格式化的表格"""
    # 计算每列最大宽度
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 格式化行
    def format_row(cells):
        return " | ".join(str(c).ljust(w) for c, w in zip(cells, col_widths))
    
    separator = "-+-".join("-" * w for w in col_widths)
    
    lines = [format_row(headers), separator]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)

table = create_table(
    ["姓名", "年龄", "城市"],
    [("张三", 25, "北京"), ("李四", 30, "上海")]
)
print(table)
