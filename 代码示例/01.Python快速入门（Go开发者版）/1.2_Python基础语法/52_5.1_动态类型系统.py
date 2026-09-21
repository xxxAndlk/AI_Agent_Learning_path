# Python对象的内部结构
# 每个对象都有PyObject头部

# PyObject结构（C层面）
# typedef struct {
#     Py_ssize_t ob_refcnt;    // 引用计数
#     PyTypeObject *ob_type;   // 类型指针
# } PyObject;

x = 42
# x实际上是指向int对象的引用
# int对象包含：引用计数、类型信息、值

print(type(x))        # <class 'int'>
print(id(x))          # 对象的内存地址（类似Go的指针）

# 动态类型检查
if isinstance(x, int):
    print("x是整数")
