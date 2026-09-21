# 变量
# Go: var x int = 1 或 x := 1
# Python: x = 1

# 常量
# Go: const PI = 3.14
# Python: PI = 3.14 (约定大写)

# 函数
# Go: func add(a, b int) int { return a + b }
# Python: def add(a: int, b: int) -> int: return a + b

# 多返回值
# Go: return a, b, err
# Python: return a, b  # 元组

# 错误处理
# Go: if err != nil { return err }
# Python: try: ... except Exception as e: ...

# 循环
# Go: for i := 0; i < 10; i++ { }
# Python: for i in range(10):

# 遍历map
# Go: for k, v := range m { }
# Python: for k, v in d.items():

# goroutine
# Go: go func() { ... }()
# Python: asyncio.create_task(coro())

# channel
# Go: ch := make(chan int)
# Python: asyncio.Queue()

# 接口
# Go: type Reader interface { Read() }
# Python: from abc import ABC, abstractmethod

# defer
# Go: defer f.Close()
# Python: with open(f) as file:

# 切片
# Go: arr[1:3]
# Python: lst[1:3]

# map
# Go: m := make(map[string]int)
# Python: d = {}  或 d = dict()

# 结构体
# Go: type User struct { Name string }
# Python: @dataclass class User: name: str
