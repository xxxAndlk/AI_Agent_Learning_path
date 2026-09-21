import random
import re
from typing import List

class TextAugmenter:
    """文本数据增强
    
    通过同义词替换、随机删除、回译等方法扩充文本数据
    """
    
    def __init__(self):
        # 简单的同义词词典（实际应用可使用WordNet）
        self.synonyms = {
            "好": ["棒", "优秀", "不错", "出色"],
            "坏": ["差", "糟糕", "不好"],
            "大": ["巨大", "庞大", "很大"],
            "小": ["微小", "迷你", "很小"],
            "快": ["迅速", "快速", "飞快"],
            "慢": ["缓慢", "迟钝"],
            "高兴": ["开心", "快乐", "愉快"],
            "难过": ["伤心", "悲伤", "痛苦"],
        }
    
    def synonym_replacement(self, text: str, n: int = 2) -> str:
        """同义词替换
        
        参数:
            text: 原始文本
            n: 替换次数
        返回:
            增强后的文本
        """
        words = list(text)
        new_words = words.copy()
        
        # 找出可以替换的词
        replaceable = []
        for i, word in enumerate(words):
            if word in self.synonyms:
                replaceable.append(i)
        
        # 随机选择n个位置替换
        if len(replaceable) >= n:
            replace_indices = random.sample(replaceable, n)
            for idx in replace_indices:
                word = words[idx]
                synonym = random.choice(self.synonyms[word])
                new_words[idx] = synonym
        
        return ''.join(new_words)
    
    def random_deletion(self, text: str, p: float = 0.1) -> str:
        """随机删除字符
        
        参数:
            text: 原始文本
            p: 删除概率
        返回:
            增强后的文本
        """
        if len(text) <= 3:
            return text
        
        words = list(text)
        new_words = []
        
        for word in words:
            if random.random() > p:
                new_words.append(word)
        
        # 确保至少保留一个字符
        if not new_words:
            return text[0]
        
        return ''.join(new_words)
    
    def random_swap(self, text: str, n: int = 2) -> str:
        """随机交换字符位置
        
        参数:
            text: 原始文本
            n: 交换次数
        返回:
            增强后的文本
        """
        words = list(text)
        
        for _ in range(n):
            if len(words) >= 2:
                idx1, idx2 = random.sample(range(len(words)), 2)
                words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return ''.join(words)
    
    def augment(self, text: str, num_augments: int = 3) -> List[str]:
        """综合增强
        
        参数:
            text: 原始文本
            num_augments: 生成增强样本数
        返回:
            增强后的文本列表
        """
        augmented = []
        
        for _ in range(num_augments):
            # 随机选择增强方法
            method = random.choice([
                self.synonym_replacement,
                self.random_deletion,
                self.random_swap
            ])
            
            new_text = method(text)
            if new_text != text:
                augmented.append(new_text)
        
        return augmented

if __name__ == "__main__":
    # 测试文本增强
    augmenter = TextAugmenter()
    
    test_text = "这个产品质量很好，物流也很快"
    
    print(f"原始文本: {test_text}")
    print()
    
    # 同义词替换
    synonym_text = augmenter.synonym_replacement(test_text, n=2)
    print(f"同义词替换: {synonym_text}")
    
    # 随机删除
    deleted_text = augmenter.random_deletion(test_text, p=0.1)
    print(f"随机删除: {deleted_text}")
    
    # 随机交换
    swapped_text = augmenter.random_swap(test_text, n=2)
    print(f"随机交换: {swapped_text}")
    
    # 综合增强
    print("\n综合增强:")
    augmented = augmenter.augment(test_text, num_augments=5)
    for i, text in enumerate(augmented, 1):
        print(f"  {i}. {text}")
