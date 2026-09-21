// Go使用接口组合和嵌入实现类似功能
type Logger interface {
    Log(message string)
}

type Saver interface {
    Save()
}

// 通过接口组合而非继承
type User struct {
    Logger
    Saver
}

// 每个类型独立实现接口
func (u User) Log(message string) {
    fmt.Printf("[LOG] %s\n", message)
}

func (u User) Save() {
    u.Log("Saving User")
}
