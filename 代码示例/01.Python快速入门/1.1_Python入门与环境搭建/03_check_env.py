# -*- coding: utf-8 -*-
"""03_check_env.py —— 学习环境一键自检
运行：python 03_check_env.py
"""
import sys                          # 解释器相关信息
import platform                     # 操作系统信息

print("Python 版本:", sys.version.split()[0])
print("操作系统:", platform.system(), platform.release())
print("解释器路径:", sys.executable)

assert sys.version_info >= (3, 10), "请升级到 Python 3.10 以上！"
print("✅ 环境正常，可以开始学习第 1.2 节了")
