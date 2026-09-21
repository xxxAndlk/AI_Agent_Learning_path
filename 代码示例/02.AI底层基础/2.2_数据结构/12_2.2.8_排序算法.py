import random
import time


def quick_sort(arr):
    """快速排序：分治思想，选择基准元素分区
    
    算法步骤：
    1. 选择一个基准元素（通常选第一个或随机）
    2. 将数组分为两部分：小于基准的 和 大于基准的
    3. 递归排序两部分
    
    特点：原地排序（空间复杂度O(log n)），平均情况性能优秀
    
    时间复杂度: 平均O(n log n)，最差O(n^2)
    空间复杂度: O(log n)（递归栈）
    稳定性: 不稳定
    """
    if len(arr) <= 1:
        return arr
    
    # 选择基准（使用三数取中法减少最差情况概率）
    mid = len(arr) // 2
    if arr[0] > arr[mid]:
        arr[0], arr[mid] = arr[mid], arr[0]
    if arr[0] > arr[-1]:
        arr[0], arr[-1] = arr[-1], arr[0]
    if arr[mid] > arr[-1]:
        arr[mid], arr[-1] = arr[-1], arr[mid]
    pivot = arr[mid]                   # 选择中位数作为基准
    
    # 分区：返回pivot的正确位置
    left = []                          # 小于基准的元素
    middle = []                        # 等于基准的元素
    right = []                         # 大于基准的元素
    
    for num in arr:
        if num < pivot:
            left.append(num)
        elif num == pivot:
            middle.append(num)
        else:
            right.append(num)
    
    # 递归排序并合并
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(arr):
    """归并排序：分治思想，递归拆分再合并
    
    算法步骤：
    1. 将数组递归地分成两半直到只剩一个元素
    2. 合并两个有序子数组
    
    特点：稳定排序，适合外部排序和链表排序
    
    时间复杂度: O(n log n)（始终如此）
    空间复杂度: O(n)（需要额外数组）
    稳定性: 稳定
    """
    if len(arr) <= 1:
        return arr
    
    # 拆分
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # 合并两个有序数组
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # 添加剩余元素
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(arr):
    """堆排序：利用堆数据结构的排序算法
    
    算法步骤：
    1. 将数组构建成大顶堆
    2. 交换堆顶和堆尾元素（最大值到末尾）
    3. 对剩余堆调整为大顶堆
    4. 重复直到排序完成
    
    特点：原地排序，时间复杂度始终O(n log n)
    
    时间复杂度: O(n log n)
    空间复杂度: O(1)
    稳定性: 不稳定
    """
    arr = arr.copy()                   # 避免修改原数组
    
    n = len(arr)
    
    def sift_down(start, end):
        """向下调整堆（ sift down / heapify）"""
        root = start
        while True:
            child = 2 * root + 1       # 左孩子
            if child > end:
                break
            
            # 找最大的孩子
            if child + 1 <= end and arr[child] < arr[child + 1]:
                child += 1
            
            if arr[root] < arr[child]:
                arr[root], arr[child] = arr[child], arr[root]
                root = child
            else:
                break
    
    # 构建大顶堆（从最后一个非叶子节点开始）
    for start in range((n - 2) // 2, -1, -1):
        sift_down(start, n - 1)
    
    # 排序：不断将堆顶移到末尾
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]  # 交换
        sift_down(0, end - 1)                # 调整堆
    
    return arr


def builtin_sort(arr):
    """Python内置排序：Timsort算法
    
    Python的list.sort()和sorted()使用Timsort算法：
    - 混合了归并排序和插入排序
    - 对部分有序数据特别高效
    - 稳定排序
    
    时间复杂度: O(n log n)（平均和最差）
    空间复杂度: O(n)（sorted需要新数组，sort原地）
    稳定性: 稳定
    
    AI应用：
    - 数据预处理
    - 特征排序
    - Top-K问题预处理
    """
    # 使用sorted（返回新列表）
    return sorted(arr)


def builtin_sort_inplace(arr):
    """原地排序版本"""
    arr.sort()                         # 原地修改


# 排序算法性能对比
def benchmark_sorts(arr_sizes=[100, 1000, 10000]):
    """对比不同排序算法的性能"""
    print("排序算法性能对比")
    print("=" * 60)
    print(f"{'数组大小':<12} {'快速排序':<12} {'归并排序':<12} {'堆排序':<12} {'内置排序':<12}")
    print("-" * 60)
    
    for size in arr_sizes:
        # 生成随机数组
        test_arr = [random.randint(0, size) for _ in range(size)]
        
        # 各排序耗时
        funcs = [
            ("快速排序", lambda a: quick_sort(a)),
            ("归并排序", lambda a: merge_sort(a)),
            ("堆排序", lambda a: heap_sort(a)),
            ("内置排序", lambda a: builtin_sort(a)),
        ]
        
        times = []
        for name, func in funcs:
            arr_copy = test_arr.copy()
            start = time.time()
            func(arr_copy)
            elapsed = (time.time() - start) * 1000  # 毫秒
            times.append(f"{elapsed:.2f}ms")
        
        print(f"{size:<12} {times[0]:<12} {times[1]:<12} {times[2]:<12} {times[3]:<12}")


# Top-K问题：使用堆排序思路
def top_k_heap(nums, k):
    """使用小顶堆找最大的K个元素
    
    思路：维护一个大小为K的小顶堆
    - 堆顶始终是当前K个最大元素中的最小值
    - 新元素大于堆顶时才替换
    
    时间复杂度: O(n log k)
    空间复杂度: O(k)
    适用场景：数据流Top-K，k远小于n时比全排序更优
    """
    import heapq
    
    heap = []                          # 小顶堆
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)
    
    # 堆中是小顶堆，需要反转得到从大到小
    return sorted(heap, reverse=True)


if __name__ == "__main__":
    # 基础排序测试
    arr = [64, 34, 25, 12, 22, 11, 90]
    print("原始数组:", arr)
    print("快速排序:", quick_sort(arr))
    print("归并排序:", merge_sort(arr))
    print("堆排序:", heap_sort(arr))
    print("内置排序:", builtin_sort(arr))
    
    # Top-K测试
    nums = [3, 2, 1, 5, 6, 4]
    print("\nTop-2最大元素:", top_k_heap(nums, 2))  # [5, 6]
    
    # 性能测试（小规模）
    print("\n排序算法性能对比:")
    benchmark_sorts([100, 1000])
