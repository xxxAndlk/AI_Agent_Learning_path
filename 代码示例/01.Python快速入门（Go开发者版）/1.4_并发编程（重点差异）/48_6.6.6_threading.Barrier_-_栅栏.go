// Go: 使用WaitGroup实现类似Barrier的功能
func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    
    fmt.Printf("Worker %d 阶段1完成\n", id)
    wg.Wait()  // 等待所有人（需要预先知道数量）
    
    fmt.Printf("Worker %d 阶段2开始\n", id)
}

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }
    wg.Wait()
    fmt.Println("所有阶段完成")
}
