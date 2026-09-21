// Go: 用channel实现信号量
func semaphoreExample() {
    maxConnections := 3
    // 创建带缓冲的channel作为信号量
    sem := make(chan struct{}, maxConnections)
    
    for i := 0; i < 6; i++ {
        go func(id int) {
            sem <- struct{}{}  // 获取信号量（阻塞直到有空间）
            // 使用资源
            time.Sleep(time.Second)
            <-sem  // 释放信号量
        }(i)
    }
    
    time.Sleep(10 * time.Second)
}
