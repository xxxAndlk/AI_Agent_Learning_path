# ============ 列表操作 ============
# 使用方括号
nums = [1, 2, 3, 4, 5]

# 空列表
# 
empty_list = []

# 添加元素
# 
nums.append(6)         # 在末尾添加
nums.insert(0, 0)      # 在指定位置插入

# 删除元素
# 
nums.remove(3)         # 删除值为3的元素
del nums[0]            # 删除索引0的元素
last = nums.pop()      # 删除并返回最后一个元素

# 切片
sub = nums[1:4]        # 取索引1到3的元素
first = nums[:3]       # 取前3个元素
last_three = nums[-3:] # 取最后3个

# 长度
length = len(nums)

# 遍历
# 
for num in nums:       # 只取值
    print(num)

for i, num in enumerate(nums):  # 取索引和值
    print(f"索引 {i}: {num}")

# 列表推导式（Python特有，类似函数式编程）
# 等价于其他语言的循环过滤
#     squares = append(squares, v*v)
# }
# 
squares = [x*x for x in nums]           # 所有元素的平方
evens = [x for x in nums if x % 2 == 0] # 过滤偶数
