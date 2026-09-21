// Go非阻塞select
select {
case msg := <-ch:
    fmt.Println(msg)
default:
    fmt.Println("没有数据，非阻塞")
}
