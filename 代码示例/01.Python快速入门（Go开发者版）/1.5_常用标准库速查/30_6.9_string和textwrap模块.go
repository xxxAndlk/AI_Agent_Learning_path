// Go的strings和text包
import (
    "strings"
    "fmt"
)

// 字符串操作
s := "Hello World"
s = strings.ToLower(s)
s = strings.ReplaceAll(s, "world", "golang")
parts := strings.Split(s, " ")

// 格式化
formatted := fmt.Sprintf("%-10s", s)

// 文本包裹（需要手动实现）
// 或使用 github.com/mitchellh/go-wordwrap
