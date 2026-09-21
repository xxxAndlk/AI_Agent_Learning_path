// Go需要额外数组来维护顺序
order := []string{"a", "b", "c"}
m := map[string]int{"a": 1, "b": 2, "c": 3}
for _, k := range order {
    fmt.Println(k, m[k])
}
