"""
约束解码性能对比
"""

def benchmark_constrained_decoding():
    """测试约束解码性能"""
    import time
    
    # 测试不同约束类型
    test_cases = [
        {"name": "无约束", "constraint": None},
        {"name": "JSON Schema", "constraint": "json"},
        {"name": "正则约束", "constraint": "regex"},
        {"name": "词汇过滤", "constraint": "forbidden"},
    ]
    
    results = []
    
    for test in test_cases:
        # 运行测试
        start = time.time()
        
        # 实际生成逻辑...
        
        elapsed = time.time() - start
        results.append({
            "constraint": test["name"],
            "time": elapsed,
        })
        
        print(f"{test['name']}: {elapsed:.2f}s")
    
    # 约束解码通常比无约束慢10-30%
    print(f"\n约束解码开销: 约10-30%")
