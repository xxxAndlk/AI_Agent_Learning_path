// Go: 普通Mutex重入会死锁（❌ 错误示例）
var mu sync.Mutex
func foo() {
    mu.Lock()
    bar()  // 再次调用会死锁
    mu.Unlock()
}
func bar() {
    mu.Lock()  // 死锁！
    mu.Unlock()
}

// Python: RLock可以安全重入（✅ 正确示例）
lock = threading.RLock()
def foo():
    with lock:
        bar()  # 安全重入

def bar():
    with lock:  # 不会死锁，允许重入
        pass
