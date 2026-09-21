// Go: select 随机选择已就绪的case
select {
case result := <-ch1:
    fmt.Println("ch1:", result)
case result := <-ch2:
    fmt.Println("ch2:", result)
case result := <-ch3:
    fmt.Println("ch3:", result)
}

// Python: as_completed 按照完成顺序处理
for coro in asyncio.as_completed(tasks):
    result = await coro
    print(result)
