# 在代码开头设置（推荐在 main 开头）
import pdb

# 使用 pdb（默认）
breakpoint()  # 进入 pdb

# 使用 ipdb（更好看的交互式调试器）
# pip install ipdb
import ipdb
# 设置环境变量切换调试器
# Linux/Mac: PYTHONBREAKPOINT=ipdb.set_trace
# Windows: set PYTHONBREAKPOINT=ipdb.set_trace
