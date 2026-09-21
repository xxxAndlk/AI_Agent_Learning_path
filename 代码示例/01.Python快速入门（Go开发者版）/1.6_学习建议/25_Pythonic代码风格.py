# ✓ 推荐
result = [x**2 for x in range(10) if x % 2 == 0]
names = [user.name for user in users]
with open("file.txt") as f: content = f.read()

# ✗ 避免
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x**2)
        
f = open("file.txt")
content = f.read()
f.close()
