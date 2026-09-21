// 方式1: 高阶函数（类似Python装饰器）
func Logger(next Handler) Handler {
    return func(w http.ResponseWriter, r *http.Request) {
        log.Println("前序操作")
        next(w, r)
        log.Println("后序操作")
    }
}

// 方式2: 结构体中间件
type Middleware func(Handler) Handler

func Chain(middlewares ...Middleware) func(Handler) Handler {
    return func(next Handler) Handler {
        for i := len(middlewares) - 1; i >= 0; i-- {
            next = middlewares[i](next)
        }
        return next
    }
}

// 使用
handler := Chain(Logger, Auth, RateLimit)(finalHandler)
