# Go 语言并发编程

Go 语言的并发模型基于 CSP（Communicating Sequential Processes）。
goroutine 是 Go 并发的核心，它比操作系统线程更轻量，可以轻松创建成千上万个。

## Channel

channel 是 goroutine 之间通信的管道。
通过 channel，不同的 goroutine 可以安全地交换数据，不需要共享内存。

## Context

context 包用于控制 goroutine 的生命周期。
它可以传递取消信号、超时和截止日期，防止 goroutine 泄漏。

# Go 错误处理

Go 语言没有 try-catch 机制，错误通过返回值显式处理。
这迫使开发者正视每一个可能的错误，写出更健壮的代码。

## panic 与 recover

panic 用于不可恢复的错误，recover 用于从 panic 中恢复。
但一般不建议滥用 panic，应该优先返回 error。