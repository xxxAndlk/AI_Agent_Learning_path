// Go select示例 - 等待多个channel
func worker(ch1, ch2 <-chan int) {
    for {
        select {
        case msg := <-ch1:
            fmt.Println("Received from ch1:", msg)
        case msg := <-ch2:
            fmt.Println("Received from ch2:", msg)
        case <-time.After(time.Second):
            fmt.Println("Timeout")
        }
    }
}

// 特点：
// 1. 随机选择一个已就绪的case执行
// 2. 如果多个case同时就绪，随机选择
// 3. 可以设置default处理非阻塞情况
// 4. 可以用于超时控制
