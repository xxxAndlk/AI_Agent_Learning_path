// Go: 使用channel实现生产者-消费者
func producer(ch chan<- int) {
    for i := 0; i < 6; i++ {
        ch <- i  // 阻塞直到消费者消费
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for v := range ch {  // 阻塞直到channel关闭
        fmt.Printf("消费: %d\n", v)
    }
}

func main() {
    ch := make(chan int, 3)
    go producer(ch)
    go consumer(ch)
    time.Sleep(2 * time.Second)
}
