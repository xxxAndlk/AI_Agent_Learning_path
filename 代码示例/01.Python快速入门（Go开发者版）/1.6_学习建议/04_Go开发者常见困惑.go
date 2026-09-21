// Go: goroutine + channel
go func() {
    ch <- data
}()
result := <-ch
