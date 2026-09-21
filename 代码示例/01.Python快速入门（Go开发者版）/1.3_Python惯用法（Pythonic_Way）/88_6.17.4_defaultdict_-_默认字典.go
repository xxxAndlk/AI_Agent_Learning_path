// Go版本
wordCount := make(map[string]int)
text := "hello world hello python world"
words := strings.Split(text, " ")
for _, word := range words {
    wordCount[word]++  // 未初始化的值为0
}
