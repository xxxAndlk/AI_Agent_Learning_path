# ============ 列表操作（对比Go的Slice） ============
# Go: nums := []int{1, 2, 3}
# Python: 使用方括号
nums = [1, 2, 3, 4, 5]

# 空列表
# Go: var nums []int
# Python:
empty_list = []

# 添加元素
# Go: nums = append(nums, 6)
# Python:
nums.append(6)         # 在末尾添加
nums.insert(0, 0)      # 在指定位置插入（Go没有直接对应方法）

# 删除元素
# Go: nums = append(nums[:2], nums[3:]...)
# Python:
nums.remove(3)         # 删除值为3的元素
del nums[0]            # 删除索引0的元素
last = nums.pop()      # 删除并返回最后一个元素（类似Go的pop）

# 切片（和Go语法几乎一样）
sub = nums[1:4]        # 取索引1到3的元素
first = nums[:3]       # 取前3个元素
last_three = nums[-3:] # 取最后3个（Go不支持负数索引）

# 长度
# Go: len(nums)
length = len(nums)

# 遍历
# Go: for i, v := range nums { ... }
# Python:
for num in nums:       # 只取值
    print(num)

for i, num in enumerate(nums):  # 取索引和值（类似Go的range）
    print(f"索引 {i}: {num}")

# 列表推导式（Python特有，类似函数式编程）
# 等价于Go的循环过滤
# Go:
# var squares []int
# for _, v := range nums {
#     squares = append(squares, v*v)
# }
# Python:
squares = [x*x for x in nums]           # 所有元素的平方
evens = [x for x in nums if x % 2 == 0] # 过滤偶数
