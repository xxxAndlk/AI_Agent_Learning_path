from collections import Counter
import re

def word_frequency(text: str) -> dict[str, int]:
    """
    统计文本中单词出现频率
    
    Args:
        text: 输入文本
        
    Returns:
        单词到频率的映射，按频率降序排列
    """
    words = re.findall(r'\b\w+\b', text.lower())
    return dict(Counter(words).most_common())

# 测试用例
def test_word_frequency():
    text = "hello world hello python world world"
    result = word_frequency(text)
    assert result == {"world": 3, "hello": 2, "python": 1}
    print("✓ 测试通过!")
