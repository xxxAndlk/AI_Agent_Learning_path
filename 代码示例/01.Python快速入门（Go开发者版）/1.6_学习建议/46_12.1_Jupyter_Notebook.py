# 安装 Jupyter
# pip install jupyter
# 启动：jupyter notebook

# 核心概念
# - Cell: 代码或 Markdown 单元
# - Kernel: 执行代码的后端进程
# - Notebook: .ipynb 文件

# 常用快捷键
"""
Shift + Enter  - 运行当前单元并移动到下一个
Ctrl + Enter   - 运行当前单元
Alt + Enter    - 运行当前单元并在下方插入新单元
A              - 在上方插入单元
B              - 在下方插入单元
DD             - 删除单元
M              - 转换为 Markdown
Y              - 转换为代码
"""

import matplotlib


# 魔法命令（Magic Commands）
%ls              # 列出当前目录文件
%cd              # 切换目录
%pwd             # 显示当前路径

%timeit sum(range(10000))  # 测量执行时间

%matplotlib inline  # 图表内联显示

# 调试
%debug            # 启动调试器

# 加载外部代码
%load_ext autoreload
%autoreload 2     # 自动重载修改的模块

# 性能分析
%prun my_func()   # 运行并显示性能报告
