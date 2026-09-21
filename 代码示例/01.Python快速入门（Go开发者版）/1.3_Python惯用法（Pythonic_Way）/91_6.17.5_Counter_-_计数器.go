// Go版本
c := make(map[string]int)
chars := []rune("hello world")
for _, ch := range chars {
    c[string(ch)]++
}
// 找最常见需要遍历
