// Go实现类似功能
package main

import (
    "sync"
    "time"
)

type CacheItem struct {
    value     interface{}
    timestamp time.Time
}

type Cache struct {
    items map[string]CacheItem
    ttl   time.Duration
    mu    sync.RWMutex
}

func NewCache(ttl time.Duration) *Cache {
    return &Cache{
        items: make(map[string]CacheItem),
        ttl:   ttl,
    }
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    
    item, exists := c.items[key]
    if !exists {
        return nil, false
    }
    
    if time.Since(item.timestamp) > c.ttl {
        return nil, false
    }
    
    return item.value, true
}

func (c *Cache) Set(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    
    c.items[key] = CacheItem{
        value:     value,
        timestamp: time.Now(),
    }
}
