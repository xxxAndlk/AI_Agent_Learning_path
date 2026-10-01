# 1. venv（Python 内置）
python -m venv myenv
# 激活
# Windows: myenv\Scripts\activate
# Linux/Mac: source myenv/bin/activate

# 2. poetry（现代依赖管理）
# pip install poetry
poetry new myproject
poetry add requests
poetry install

# 3. pipenv（结合 pip 和 venv）
# pip install pipenv
pipenv install requests
pipenv shell

# 4. conda（科学计算常用）
# 安装 Anaconda 或 Miniconda
conda create -n myenv python=3.12
conda activate myenv

# 5. uv（新一代包/环境管理器，2024起成为主流）
# pip install uv
uv venv myenv
uv pip install requests
