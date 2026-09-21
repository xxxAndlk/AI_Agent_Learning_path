# Python变量查找顺序：LEGB
# Local → Enclosing → Global → Built-in

x = "global"

def outer():
    x = "enclosing"
    
    def inner():
        x = "local"       # Local
        print(x)          # 输出: local
    
    inner()
    print(x)              # 输出: enclosing

outer()
print(x)                  # 输出: global

# global和nonlocal关键字
def modify_global():
    global x
    x = "modified global"  # 修改全局变量

def modify_enclosing():
    x = "outer"
    def inner():
        nonlocal x
        x = "modified"     # 修改外层变量
    inner()
