# 安装
# pip install ipython

# 启动：ipython

# 特色功能

# 1. Tab 自动补全
# 输入函数名按 Tab 键查看提示

# 2. ? 查看文档
# str?
# len?

# 3. ?? 查看源码
# list??

# 4. 魔法命令
# %time       # 测量执行时间（IPython魔法命令）
# %who        # 列出所有变量
# %reset      # 清空所有变量

# 5. 历史记录
# ↑↓ 键浏览命令历史

# 6. 粘贴多行代码
# 支持自动缩进

# 7. 系统命令
# !ls  # 执行 shell 命令

# IPython 配置
# 创建 ~/.ipython/profile_default/ipython_config.py
c = get_config()
c.TerminalInteractiveShell.editing_mode = 'vi'  # 使用 vi 模式
c.Completer.use_jedi = True                     # 启用自动补全
