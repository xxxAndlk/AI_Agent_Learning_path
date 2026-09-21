// Go: 使用context包传递上下文
func processRequest(ctx context.Context, requestID int) {
    // 将值存储在context中
    ctx = context.WithValue(ctx, "requestID", requestID)
    ctx = context.WithValue(ctx, "startTime", time.Now())
    
    doProcessing(ctx)
}

func doProcessing(ctx context.Context) {
    // 从context获取值
    requestID := ctx.Value("requestID").(int)
    fmt.Printf("处理请求: %d\n", requestID)
}
