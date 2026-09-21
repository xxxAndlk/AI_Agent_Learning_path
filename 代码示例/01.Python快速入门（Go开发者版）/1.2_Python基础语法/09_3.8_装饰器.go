// Go中间件模式示例
func Logger(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        log.Println("调用前")
        next(w, r)
        log.Println("调用后")
    }
}

// 使用
http.HandleFunc("/hello", Logger(HelloHandler))
