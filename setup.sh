#!/usr/bin/env bash
# =========================================================
# AI Agent 学习路径 · 一键环境准备（macOS / Linux / Git Bash）
# 作用：创建虚拟环境 -> （可选）安装依赖 -> 运行自检
# 用法：bash setup.sh
# =========================================================
set -e

# 选择 python 命令（macOS 上通常是 python3）
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi

echo "========================================================="
echo " AI Agent 学习路径 · 环境准备"
echo "========================================================="
echo "  [1] 最小启动（推荐新手）：只建虚拟环境 + 自检，"
echo "      不装第三方库，立刻能学第 1 章"
echo "  [2] 完整安装：额外安装全书依赖 requirements.txt"
echo "---------------------------------------------------------"
read -r -p "请输入 1 或 2（直接回车默认 1）: " choice
choice="${choice:-1}"
if [ "$choice" != "1" ] && [ "$choice" != "2" ]; then
    echo "输入无效，按默认 [1] 最小启动处理。"
    choice="1"
fi

echo ""
echo "[1/3] 创建虚拟环境 venv ..."
"$PY" -m venv venv

# 定位虚拟环境里的 python（Windows Git Bash 与 *nix 路径不同）
if [ -f "venv/bin/python" ]; then VPY="venv/bin/python"; else VPY="venv/Scripts/python.exe"; fi

echo "[2/3] 升级 pip ..."
"$VPY" -m pip install --upgrade pip

if [ "$choice" = "2" ]; then
    echo "[3/3] 安装全书依赖（内容较多，稍后也可按需补装）..."
    "$VPY" -m pip install -r requirements.txt
else
    echo "[3/3] 跳过第三方库（最小启动）。"
    echo "      学到第 3 章前执行：pip install openai python-dotenv"
fi

echo ""
echo "运行环境自检 ..."
"$VPY" check_env.py

echo ""
if [ -f "venv/bin/activate" ]; then ACT="source venv/bin/activate"; else ACT="venv\\Scripts\\activate"; fi
echo "全部完成！激活虚拟环境请执行： $ACT"
