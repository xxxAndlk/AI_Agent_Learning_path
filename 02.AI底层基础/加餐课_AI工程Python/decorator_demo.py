"""decorator_demo.py —— 加餐课《AI 工程里的 Python》演示：装饰器。

纯标准库，Python 3.10+。运行：python decorator_demo.py
demo 1：给两个"AI 场景"函数套计时装饰器；demo 2：functools.wraps 的作用对照。
"""
import functools
import sys
import time


def timer(func):
    """计时装饰器：进门前记时间，出门报耗时，原函数一行不改。"""
    @functools.wraps(func)  # 把原函数的名字/文档抄回 wrapper，否则查错表时会"查无此人"
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # 专测时长的表，比 time.time 更适合计时
        result = func(*args, **kwargs)
        cost = time.perf_counter() - start
        print(f"[timer] {func.__name__} finished in {cost:.3f}s")
        return result
    return wrapper


@timer
def chat(prompt):
    """假装调一次大模型：固定等 0.2 秒再回话。"""
    time.sleep(0.2)
    return f"echo: {prompt}"


@timer
def embed_texts(texts):
    """假装批量算向量：逐条处理，每条歇 0.01 秒，批次越长越慢。"""
    total = 0
    for text in texts:
        time.sleep(0.01)
        total += sum(ord(ch) % 97 for ch in text)
    return total


def wraps_demo():
    """对照：不加 wraps，原函数的名字和文档会被 wrapper 顶掉。"""

    def bare(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def kept(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @bare
    def doc_a():
        "我是 doc_a 的说明书"

    @kept
    def doc_b():
        "我是 doc_b 的说明书"

    print("without @wraps -> __name__ =", doc_a.__name__, "| __doc__ =", doc_a.__doc__)
    print("with    @wraps -> __name__ =", doc_b.__name__, "| __doc__ =", doc_b.__doc__)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # 防 Windows 控制台中文乱码

    print("== demo 1: timer decorator on two functions ==")
    print("chat() ->", chat("你好，模型"))
    print("embed_texts() ->", embed_texts(["hello", "world"]))
    print()
    print("== demo 2: what functools.wraps keeps ==")
    wraps_demo()
