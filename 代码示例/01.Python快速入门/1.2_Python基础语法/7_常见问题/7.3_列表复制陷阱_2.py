a = [1, 2, 3]
b = a[:]            # 切片复制
b = a.copy()        # 方法复制
b = list(a)         # 构造函数复制
import copy
b = copy.deepcopy(a)  # 深拷贝（嵌套结构）
