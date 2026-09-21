# 问题：两个模块互相导入类型
# a.py 导入 b.py，b.py 导入 a.py

# 解决方案：使用TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from b import B  # 仅在类型检查时导入

class A:
    def method(self, b: "B"):  # 字符串注解
        pass
