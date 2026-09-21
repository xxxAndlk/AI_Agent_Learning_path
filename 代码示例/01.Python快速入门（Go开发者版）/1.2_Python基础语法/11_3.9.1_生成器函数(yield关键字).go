// Go等价的惰性生成器
func generateNums() chan int {
    ch := make(chan int)
    go func() {  // 启动goroutine
        for i := 1; i <= 5; i++ {
            ch <- i
        }
        close(ch)
    }()
    return ch
}

// 使用
for n := range generateNums() {
    fmt.Println(n)
}
