# 7. enumerate和zip
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 35]

# 不推荐
# for i in range(len(names)):
#     print(i, names[i])

# 推荐（Pythonic）
for i, name in enumerate(names):
    print(f"{i}: {name}")

for name, age in zip(names, ages):
    print(f"{name} is {age}")
