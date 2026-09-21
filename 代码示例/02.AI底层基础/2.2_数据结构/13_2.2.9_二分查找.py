from typing import List, Optional


def binary_search_basic(nums: List[int], target: int) -> int:
    """标准二分查找：查找目标值的位置
    
    前提条件：有序数组（升序）
    
    参数:
        nums: 有序数组
        target: 目标值
    返回值:
        目标值的索引，如果不存在返回-1
    
    时间复杂度: O(log n)
    空间复杂度: O(1)
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:               # 注意边界：包含等于情况
        mid = (left + right) // 2      # 防止整数溢出可写成 left + (right - left) // 2
        
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1             # 搜索右半部分
        else:
            right = mid - 1            # 搜索左半部分
    
    return -1                          # 未找到


def binary_search_left_bound(nums: List[int], target: int) -> int:
    """边界二分查找：查找左边界（第一个 >= target 的位置）
    
    应用场景：
    - 查找第一个满足条件的元素
    - 插入位置
    - 统计某个值出现的次数（需要配合右边界）
    
    时间复杂度: O(log n)
    空间复杂度: O(1)
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] < target:
            left = mid + 1
        else:
            # nums[mid] >= target 时，可能已经是左边界
            # 但需要继续向左搜索
            right = mid - 1
    
    # left 可能是左边界，或者超出数组范围
    # 检查left是否在有效范围内且是否为左边界
    if left < len(nums) and nums[left] == target:
        return left
    return left                         # 返回插入位置


def binary_search_right_bound(nums: List[int], target: int) -> int:
    """边界二分查找：查找右边界（最后一个 <= target 的位置）
    
    返回值:
        最后一个 >= target 的位置 - 1，即最后一个小于target的位置
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] <= target:
            left = mid + 1
        else:
            right = mid - 1
    
    return right


def binary_search_rotated(nums: List[int], target: int) -> int:
    """旋转数组二分查找
    
    旋转数组：原本升序的数组在某个位置旋转
    例如：[0,1,2,3,4,5,6] 旋转后可能是 [4,5,6,0,1,2,3]
    
    思路：
    - 每次比较中间元素和右边界，确定哪一半是有序的
    - 判断target是否在有序的一半中
    
    时间复杂度: O(log n)
    空间复杂度: O(1)
    """
    if not nums:
        return -1
    
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] == target:
            return mid
        
        # 判断哪一半是有序的
        if nums[left] <= nums[mid]:
            # 左半部分有序
            if nums[left] <= target < nums[mid]:
                right = mid - 1        # target在左半部分
            else:
                left = mid + 1         # target在右半部分
        else:
            # 右半部分有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1         # target在右半部分
            else:
                right = mid - 1        # target在左半部分
    
    return -1


def binary_search_lower_ceil(nums: List[float], target: float) -> int:
    """查找下取整：找 >= target 的最小值"""
    left, right = 0, len(nums) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] >= target:
            result = mid               # 可能是答案
            right = mid - 1            # 继续向左找更小的
        else:
            left = mid + 1
    
    return result


def binary_search_upper_floor(nums: List[float], target: float) -> int:
    """查找上取整：找 <= target 的最大值"""
    left, right = 0, len(nums) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] <= target:
            result = mid               # 可能是答案
            left = mid + 1             # 继续向右找更大的
        else:
            right = mid - 1
    
    return result


# 二分查找变体：查找峰值元素
def find_peak_element(nums: List[int]) -> int:
    """查找峰值元素（大于相邻元素的元素）
    
    峰值元素特点：nums[i] > nums[i-1] 且 nums[i] > nums[i+1]
    数组边界处：只需满足单向比较
    
    时间复杂度: O(log n)
    空间复杂度: O(1)
    
    AI应用：
    - 神经网络激活函数的峰值检测
    - 梯度下降的峰值检测
    """
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = left + (right - left) // 2
        
        if nums[mid] < nums[mid + 1]:
            # 上升趋势，峰值在右边
            left = mid + 1
        else:
            # 下降趋势或在峰值上，峰值在左边（包括mid）
            right = mid
    
    return left


if __name__ == "__main__":
    # 标准二分查找
    nums = [1, 3, 5, 7, 9, 11, 13]
    print("标准二分查找:")
    print(f"5的位置: {binary_search_basic(nums, 5)}")   # 2
    print(f"6的位置: {binary_search_basic(nums, 6)}")   # -1
    
    # 边界二分查找
    nums_with_dups = [1, 2, 2, 2, 3, 4]
    print("\n边界二分查找:")
    print(f"2的左边界: {binary_search_left_bound(nums_with_dups, 2)}")   # 1
    print(f"2的右边界: {binary_search_right_bound(nums_with_dups, 2)}")  # 3
    
    # 旋转数组二分查找
    rotated = [4, 5, 6, 7, 0, 1, 2]
    print("\n旋转数组二分查找:")
    print(f"0的位置: {binary_search_rotated(rotated, 0)}")   # 4
    print(f"3的位置: {binary_search_rotated(rotated, 3)}")   # -1
    
    # 峰值查找
    nums_peak = [1, 2, 3, 1]
    print("\n峰值查找:")
    print(f"峰值索引: {find_peak_element(nums_peak)}")      # 2
