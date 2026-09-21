# Go风格（不推荐）
result = []
for item in items:
    if item > 0:
        result.append(item * 2)

# Pythonic风格
result = [item * 2 for item in items if item > 0]
