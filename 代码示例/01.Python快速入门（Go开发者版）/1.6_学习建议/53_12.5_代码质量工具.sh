# 安装常用工具
pip install black ruff mypy pytest coverage

# black - 代码格式化
black mymodule.py
black .  # 格式化整个目录

# ruff - 快速代码检查（比 flake8 快 10-100 倍）
ruff check mymodule.py
ruff check . --fix  # 自动修复

# mypy - 类型检查
mypy mymodule.py
mypy . --strict  # 严格模式

# pytest - 测试框架
pytest tests/
pytest -v  # 详细输出
pytest --cov=mymodule  # 覆盖率

# 预提交钩子配置
# 创建 .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
  
  - repo: https://github.com/astral-sh/ruff
    rev: v0.1.9
    hooks:
      - id: ruff
