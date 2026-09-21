# 缓存策略配置
CACHE_STRATEGIES = {
    # 完全匹配缓存（相同输入返回相同输出）
    "exact": {
        "description": "完全匹配缓存",
        "适用场景": "无状态API调用",
        "key生成": "prompt + model + temperature + max_tokens",
        "TTL": 3600,
    },
    
    # 语义缓存（相似输入返回相似输出）
    "semantic": {
        "description": "语义缓存",
        "适用场景": "允许近似匹配的搜索",
        "key生成": "向量相似度 + 阈值",
        "TTL": 1800,
    },
    
    # 会话缓存（同一会话内缓存）
    "session": {
        "description": "会话缓存",
        "适用场景": "多轮对话",
        "key生成": "session_id + message_hash",
        "TTL": 1800,  # 会话超时时间
    },
    
    # 用户缓存（用户级别缓存）
    "user": {
        "description": "用户缓存",
        "适用场景": "用户特定配置",
        "key生成": "user_id + preference_key",
        "TTL": 86400,  # 24小时
    },
}
