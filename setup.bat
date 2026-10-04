@echo off
rem =========================================================
rem AI Agent 学习路径 · 一键环境准备（Windows）
rem 作用：创建虚拟环境 -> （可选）安装依赖 -> 运行自检
rem =========================================================

chcp 65001 >nul

echo =========================================================
echo  AI Agent 学习路径 · 环境准备
echo =========================================================
echo   [1] 最小启动（推荐新手）：只建虚拟环境 + 自检，
echo       不装第三方库，立刻能学第 1 章
echo   [2] 完整安装：额外安装全书依赖 requirements.txt
echo ---------------------------------------------------------
set /p choice=请输入 1 或 2（直接回车默认 1）: 
if "%choice%"=="" set choice=1
if not "%choice%"=="1" if not "%choice%"=="2" (
    echo 输入无效，按默认 [1] 最小启动处理。
    set choice=1
)

echo.
echo [1/3] 创建虚拟环境 venv ...
python -m venv venv
if errorlevel 1 (echo 创建失败，请先确认已安装 Python 并勾选 Add to PATH ^& pause ^& exit /b 1)

echo [2/3] 升级 pip ...
venv\Scripts\python.exe -m pip install --upgrade pip

if "%choice%"=="2" (
    echo [3/3] 安装全书依赖（内容较多，稍后也可按需补装）...
    venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo [3/3] 跳过第三方库（最小启动）。
    echo       学到第 3 章前执行：pip install openai python-dotenv
)

echo.
echo 运行环境自检 ...
venv\Scripts\python.exe check_env.py

echo.
echo 全部完成！激活虚拟环境请执行： venv\Scripts\activate
pause
