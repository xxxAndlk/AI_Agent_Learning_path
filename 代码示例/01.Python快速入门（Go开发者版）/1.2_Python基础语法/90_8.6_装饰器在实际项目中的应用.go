// 日志中间件（类似@log_calls）
func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("请求: %s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}

// 性能计时（类似@timer）
func Timer(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("耗时: %v", time.Since(start))
    })
}

// 权限检查（类似@require_role）
func RequireRole(role string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // 检查用户角色...
            if !hasRole(r.Context(), role) {
                http.Error(w, "Forbidden", http.StatusForbidden)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}

// 使用
http.Handle("/", Logger(Timer(RequireRole("admin")(handler))))
