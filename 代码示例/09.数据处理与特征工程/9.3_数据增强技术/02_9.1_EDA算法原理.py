import random
import re
from typing import List, Tuple

class EDA:
    """Easy Data Augmentation - 简单数据增强"""
    
    def __init__(
        self,
        synonym_dict: dict = None,
        stop_words: set = None
    ):
        """
        初始化EDA增强器
        
        参数:
            synonym_dict: 同义词词典
            stop_words: 停用词集合
        """
        # 默认同义词词典
        self.synonym_dict = synonym_dict or {
            "好": ["棒", "优秀", "不错", "出色", "很好", "优良"],
            "坏": ["差", "糟糕", "不好", "恶劣", "差劲"],
            "大": ["巨大", "庞大", "很大", "宏大", "广大"],
            "小": ["微小", "迷你", "很小", "细小", "渺小"],
            "快": ["迅速", "快速", "飞快", "高速", "敏捷"],
            "慢": ["缓慢", "迟钝", "迟缓", "慢慢", "磨蹭"],
            "高": ["高大", "高耸", "很高", "崇高", "高层次"],
            "低": ["矮小", "低矮", "很低", "低下", "低层次"],
            "多": ["众多", "许多", "大量", "诸多", "繁多"],
            "少": ["少量", "稀少", "少数", "稀疏", "不多"],
            "新": ["崭新", "全新", "新颖", "新式", "新鲜"],
            "旧": ["陈旧", "老化", "破旧", "陈腐", "过时"],
            "重要": ["关键", "主要", "重要", "要紧", "紧要"],
            "困难": ["艰难", "困难", "艰巨", "难办", "不易"],
            "简单": ["容易", "简单", "简便", "轻易", "不复杂"]
        }
        
        # 中文停用词
        self.stop_words = stop_words or {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这"
        }
    
    def synonym_replace(
        self,
        sentence: str,
        n: int = 1
    ) -> str:
        """
        同义词替换
        
        参数:
            sentence: 输入句子
            n: 替换词语数量
        
        返回:
            增强后的句子
        """
        words = self._tokenize(sentence)
        
        if len(words) == 0:
            return sentence
        
        # 找出可以替换的词
        replaceable_indices = []
        for i, word in enumerate(words):
            if word in self.synonym_dict:
                replaceable_indices.append(i)
        
        if not replaceable_indices:
            return sentence
        
        # 随机选择n个词进行替换
        n = min(n, len(replaceable_indices))
        replace_indices = random.sample(replaceable_indices, n)
        
        for idx in replace_indices:
            word = words[idx]
            synonyms = self.synonym_dict[word]
            words[idx] = random.choice(synonyms)
        
        return ''.join(words)
    
    def random_insert(
        self,
        sentence: str,
        n: int = 1
    ) -> str:
        """
        随机插入 - 在句子中随机位置插入同义词
        
        参数:
            sentence: 输入句子
            n: 插入次数
        
        返回:
            增强后的句子
        """
        words = list(sentence)
        
        for _ in range(n):
            # 找到可替换的词
            replaceable = [(i, w) for i, w in enumerate(words) if w in self.synonym_dict]
            
            if not replaceable:
                continue
            
            # 随机选择一个词
            idx, word = random.choice(replaceable)
            
            # 随机选择一个同义词插入
            synonym = random.choice(self.synonym_dict[word])
            
            # 在随机位置插入
            insert_pos = random.randint(0, len(words))
            words.insert(insert_pos, synonym)
        
        return ''.join(words)
    
    def random_swap(
        self,
        sentence: str,
        n: int = 1
    ) -> str:
        """
        随机交换 - 随机交换两个词的位置
        
        参数:
            sentence: 输入句子
            n: 交换次数
        
        返回:
            增强后的句子
        """
        words = list(sentence)
        
        length = len(words)
        
        if length < 2:
            return sentence
        
        for _ in range(n):
            # 随机选择两个不同的位置
            idx1, idx2 = random.sample(range(length), 2)
            
            # 交换
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return ''.join(words)
    
    def random_delete(
        self,
        sentence: str,
        p: float = 0.1
    ) -> str:
        """
        随机删除 - 以一定概率删除词
        
        参数:
            sentence: 输入句子
            p: 删除概率
        
        返回:
            增强后的句子
        """
        words = list(sentence)
        
        # 确保保留至少一个词
        if len(words) <= 1:
            return sentence
        
        new_words = [w for w in words if random.random() > p]
        
        # 如果删除后为空，保留原句
        if not new_words:
            return sentence
        
        return ''.join(new_words)
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 使用正则表达式分词
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+|[^\s]', text)
        return words
    
    def augment(
        self,
        sentence: str,
        num_augments: int = 4,
        alpha: float = 0.1
    ) -> List[str]:
        """
        综合增强 - 组合使用多种增强方法
        
        参数:
            sentence: 输入句子
            num_augments: 生成的增强样本数
            alpha: 增强强度参数
        
        返回:
            增强后的句子列表
        """
        augmented_sentences = []
        words = self._tokenize(sentence)
        n = max(1, int(len(words) * alpha))  # 计算增强参数
        
        # 增强方法
        aug_methods = [
            lambda: self.synonym_replace(sentence, n),
            lambda: self.random_insert(sentence, n),
            lambda: self.random_swap(sentence, n),
            lambda: self.random_delete(sentence, p=alpha)
        ]
        
        # 生成指定数量的增强样本
        for _ in range(num_augments):
            # 随机选择一种增强方法
            method = random.choice(aug_methods)
            augmented = method()
            
            if augmented and augmented != sentence:
                augmented_sentences.append(augmented)
        
        # 去重
        return list(set(augmented_sentences))
