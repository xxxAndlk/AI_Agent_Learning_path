import (
    "path/filepath"
    "os"
)

// 路径拼接 - 使用filepath.Join
base := "/home/user"
config := filepath.Join(base, "config", "app.yaml")

// 获取路径信息
filepath.Base("/home/user/file.txt")   // file.txt - 文件名
filepath.Dir("/home/user/file.txt")    // /home/user - 目录
filepath.Ext("/home/user/file.txt")    // .txt - 扩展名

// 检查路径类型
info, err := os.Stat("example.txt")
if err != nil { return }
info.IsDir()   // 是否为目录

// 遍历目录
filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
    fmt.Println(path)
    return nil
})

// 路径存在性
_, err := os.Stat("example.txt")
exists := !os.IsNotExist(err)
