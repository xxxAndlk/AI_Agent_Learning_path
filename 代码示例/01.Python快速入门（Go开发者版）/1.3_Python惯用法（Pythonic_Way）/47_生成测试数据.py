import itertools

# 场景：生成笛卡尔积测试用例
config = {
    'os': ['Windows', 'Linux', 'macOS'],
    'browser': ['Chrome', 'Firefox', 'Safari'],
}

# 生成所有组合
test_cases = list(itertools.product(config['os'], config['browser']))
print(f"总测试用例数: {len(test_cases)}")  # 9
for tc in test_cases[:3]:
    print(tc)
# ('Windows', 'Chrome')
# ('Windows', 'Firefox')
# ('Windows', 'Safari')
