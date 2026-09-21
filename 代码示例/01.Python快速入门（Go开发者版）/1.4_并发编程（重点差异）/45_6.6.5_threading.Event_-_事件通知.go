// Go: 使用channel实现事件
func worker(done chan bool) {
    <-done  // 等待事件
    fmt.Println("开始工作")
    time.Sleep(time.Second)
    done <- true  // 通知完成
}

func main() {
    done := make(chan bool)
    go worker(done)
    done <- true  // 发出开始信号
    <-done  // 等待完成
}
