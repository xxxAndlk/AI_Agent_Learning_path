# 1. 使用类型提示
def process(data: list[dict[str, int]]) -> dict[str, int]:
    ...

# 2. 使用mypy检查
# pip install mypy
# mypy your_file.py

# 3. 使用pyright（VS Code内置）
# 更快的类型检查

# 4. 使用严格模式
# mypy --strict your_file.py
