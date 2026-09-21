# Python import过程
# 1. 搜索模块文件（sys.path）
# 2. 编译为字节码（如需要）
# 3. 执行模块代码
# 4. 创建模块对象
# 5. 缓存到sys.modules

import sys
print(sys.path)       # 模块搜索路径
print(sys.modules)    # 已加载模块缓存
