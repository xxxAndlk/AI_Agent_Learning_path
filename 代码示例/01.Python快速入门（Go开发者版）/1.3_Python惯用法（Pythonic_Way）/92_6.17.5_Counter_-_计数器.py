# 实际案例：查找出现次数超过k的元素
def find_frequent(items, k):
    """查找出现次数超过k的元素"""
    count = Counter(items)
    return [item for item, cnt in count.items() if cnt > k]

items = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
print(find_frequent(items, 2))  # [3, 4]

# 实际案例：两篇文章的关键词差异
article1_words = Counter(['python', 'java', 'go', 'rust', 'python'])
article2_words = Counter(['python', 'java', 'c++', 'rust', 'python'])

# 找出两篇文章共有的关键词
common = article1_words & article2_words
print("共有关键词:", list(common.elements()))

# 找出文章1独有关键词
unique1 = article1_words - article2_words
print("文章1独有:", list(unique1.elements()))
