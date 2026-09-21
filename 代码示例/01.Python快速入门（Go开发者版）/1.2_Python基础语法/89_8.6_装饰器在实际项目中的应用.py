import functools
import time
from functools import wraps

# ============ 场景1: 日志记录 ============
# 记录函数调用信息
def log_calls(func):
    """记录函数调用日志"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[日志] 调用函数: {func.__name__}")
        print(f"[日志] 参数: args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            print(f"[日志] 函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            print(f"[日志] 函数 {func.__name__} 执行失败: {e}")
            raise
    return wrapper

@log_calls
def divide(a, b):
    return a / b

divide(10, 2)
# 输出:
# [日志] 调用函数: divide
# [日志] 参数: args=(10, 2), kwargs={}
# [日志] 函数 divide 执行成功

# ============ 场景2: 性能计时 ============
def timer(func):
    """测量函数执行时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[计时] {func.__name__} 执行耗时: {elapsed:.4f}秒")
        return result
    return wrapper

@timer
def slow_operation():
    time.sleep(0.5)
    return "完成"

slow_operation()
# 输出: [计时] slow_operation 执行耗时: 0.5000秒

# ============ 场景3: 缓存装饰器（记忆化） ============
def memoize(func):
    """缓存函数结果，避免重复计算"""
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
            print(f"[缓存] 计算 {func.__name__}({args})")
        else:
            print(f"[缓存] 命中 {func.__name__}({args})")
        return cache[args]
    
    # 提供清空缓存的方法
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper

@memoize
def fibonacci(n):
    """斐波那契数列（递归版本）"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(5))  # 首次计算，需要多次递归
print(fibonacci(5))  # 命中缓存，直接返回结果

# ============ 场景4: 权限检查 ============
# 模拟用户认证系统
current_user = {"name": "张三", "role": "user"}

def require_role(role):
    """检查用户权限的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.get("role") != role:
                raise PermissionError(f"需要 {role} 权限，当前角色: {current_user.get('role')}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

class Article:
    @require_role("admin")
    def delete_article(self, article_id):
        print(f"删除文章 {article_id}")
    
    @require_role("user")
    def publish_article(self, title):
        print(f"发布文章: {title}")

# 测试权限
article = Article()
article.publish_article("Python教程")  # 成功

try:
    article.delete_article(123)  # 失败: 需要admin权限
except PermissionError as e:
    print(f"权限错误: {e}")

# ============ 场景5: 重试机制 ============
def retry(max_attempts=3, delay=1):
    """自动重试失败的函数"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    print(f"[重试] {func.__name__} 失败，{attempts}/{max_attempts}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unreliable_api_call():
    """模拟不稳定的API调用"""
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络错误")
    return "API响应数据"

# 测试重试
for _ in range(5):
    try:
        result = unreliable_api_call()
        print(f"成功: {result}")
    except ConnectionError as e:
        print(f"失败: {e}")

# ============ 场景6: Web框架中的装饰器应用 ============
# Flask风格路由装饰器示例
class Router:
    def __init__(self):
        self.routes = {}
    
    def route(self, path):
        """路由装饰器"""
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
    
    def handle(self, path):
        """处理请求"""
        if path in self.routes:
            return self.routes[path]()
        return "404 Not Found"

# 使用
app = Router()

@app.route("/home")
def home():
    return "欢迎来到首页"

@app.route("/about")
def about():
    return "关于页面"

print(app.handle("/home"))    # 输出: 欢迎来到首页
print(app.handle("/about"))   # 输出: 关于页面
print(app.handle("/contact")) # 输出: 404 Not Found
