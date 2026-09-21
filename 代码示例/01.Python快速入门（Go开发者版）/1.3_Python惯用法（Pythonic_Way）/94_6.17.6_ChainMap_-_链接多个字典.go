// Go模拟ChainMap
type ChainMap struct {
    maps []map[string]interface{}
}
func (c *ChainMap) Get(key string) (interface{}, bool) {
    for _, m := range c.maps {
        if val, ok := m[key]; ok {
            return val, true
        }
    }
    return nil, false
}
