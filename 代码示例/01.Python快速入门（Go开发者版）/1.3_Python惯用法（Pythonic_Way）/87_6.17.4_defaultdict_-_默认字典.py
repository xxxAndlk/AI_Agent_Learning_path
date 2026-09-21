from collections import defaultdict

# 定义默认值类型
# 常见工厂函数：int, list, dict, set, str, float

# 示例1：计数（int默认值为0）
word_count = defaultdict(int)
text = "hello world hello python world"
for word in text.split():
    word_count[word] += 1  # 不存在的键自动创建为0
print(dict(word_count))  # {'hello': 2, 'world': 2, 'python': 1}

# 示例2：分组（list默认值为[]）
words_by_length = defaultdict(list)
words = ["apple", "banana", "cat", "dog", "egg"]
for word in words:
    words_by_length[len(word)].append(word)
print(dict(words_by_length))
# {5: ['apple', 'banana'], 3: ['cat', 'dog', 'egg']}

# 示例3：嵌套字典
nested = defaultdict(lambda: defaultdict(list))
nested['user1']['skills'].append('Python')
nested['user2']['skills'].append('Go')
print(dict(nested))

# 示例4：集合去重
unique_chars = defaultdict(set)
words = ["apple", "apply", "banana"]
for word in words:
    for char in word:
        unique_chars[char].add(word)
print(dict(unique_chars))
# {'a': {'apple', 'apply', 'banana'}, 'p': {'apple', 'apply'}, ...}

# 示例5：使用自定义工厂函数
def tree_factory():
    return {'left': None, 'right': None}

tree = defaultdict(tree_factory)
tree[0]['left'] = 1
tree[0]['right'] = 2
print(dict(tree))  # {0: {'left': 1, 'right': 2}}

# 示例6：lambda工厂函数
scores = defaultdict(lambda: (0, 0))  # (总分, 人数)
scores['math'] = (scores['math'][0] + 95, scores['math'][1] + 1)
scores['math'] = (scores['math'][0] + 88, scores['math'][1] + 1)
print(scores['math'])  # (183, 2)
