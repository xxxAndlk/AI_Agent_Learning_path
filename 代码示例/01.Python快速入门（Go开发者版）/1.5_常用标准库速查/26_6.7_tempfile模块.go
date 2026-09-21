// Go的临时文件处理
import (
    "os"
    "io/ioutil"
)

// 创建临时文件
f, err := os.CreateTemp("", "prefix-*.txt")
defer os.Remove(f.Name())

// 创建临时目录
dir, err := os.MkdirTemp("", "prefix-")
defer os.RemoveAll(dir)

// 获取临时目录
tempDir := os.TempDir()
