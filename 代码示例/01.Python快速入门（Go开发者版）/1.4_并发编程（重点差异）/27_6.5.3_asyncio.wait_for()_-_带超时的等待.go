// Go的超时控制
select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(2 * time.Second):
    fmt.Println("超时")
}

// Python等价的完整实现
async def wait_with_timeout(ch, timeout):
    try:
        result = await asyncio.wait_for(ch, timeout)
        print(result)
    except asyncio.TimeoutError:
        print("超时")
