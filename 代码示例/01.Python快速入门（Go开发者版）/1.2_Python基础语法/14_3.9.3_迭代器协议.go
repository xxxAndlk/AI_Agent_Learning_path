// Go的迭代器实现
type Counter struct {
    current int
    start   int
}

func NewCounter(start int) *Counter {
    return &Counter{start: start, current: start}
}

func (c *Counter) Next() (int, bool) {
    if c.current <= 0 {
        return 0, false
    }
    c.current--
    return c.current + 1, true
}

// 使用
counter := NewCounter(5)
for {
    v, ok := counter.Next()
    if !ok {
        break
    }
    fmt.Println(v)
}
