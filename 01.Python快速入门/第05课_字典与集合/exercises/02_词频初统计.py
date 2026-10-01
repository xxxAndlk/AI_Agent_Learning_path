# 练习2参考答案：词频初统计
# 思路：键存单词，值存次数。get(word, 0) 表示"没出现过就当 0"，再加 1

words = ["apple", "banana", "apple", "cat", "apple", "banana"]

counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

for word, count in counts.items():
    print(f"{word} 出现了 {count} 次")
