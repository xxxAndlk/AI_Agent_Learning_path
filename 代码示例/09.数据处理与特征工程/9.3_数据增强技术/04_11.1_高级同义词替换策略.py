import numpy as np

class AdvancedSynonymReplacer:
    """高级同义词替换器"""
    
    def __init__(
        self,
        word_embeddings=None,
        synonym_dict: dict = None
    ):
        """
        初始化高级替换器
        
        参数:
            word_embeddings: 词向量模型
            synonym_dict: 同义词词典
        """
        self.word_embeddings = word_embeddings
        self.synonym_dict = synonym_dict or {}
        
        # 扩展同义词词典
        self._extend_synonym_dict()
    
    def _extend_synonym_dict(self):
        """扩展同义词词典"""
        # 可以从WordNet等资源加载
        # 这里添加更多常用词
        additional_synonyms = {
            "学习": ["学习", "掌握", "学会", "习得"],
            "工作": ["工作", "做事", "干活", "任职"],
            "生活": ["生活", "生存", "过日子", "日常"],
            "问题": ["问题", "疑问", "难题", "困惑"],
            "解决": ["解决", "处理", "解答", "化解"],
            "使用": ["使用", "运用", "应用", "采用"],
            "开发": ["开发", "研制", "构建", "创建"],
            "技术": ["技术", "技巧", "工艺", "科技"],
            "系统": ["系统", "体系", "架构", "平台"],
            "数据": ["数据", "资料", "信息", "数字"]
        }
        
        for word, synonyms in additional_synonyms.items():
            if word not in self.synonym_dict:
                self.synonym_dict[word] = synonyms
    
    def get_synonyms(self, word: str) -> List[str]:
        """
        获取同义词列表
        
        参数:
            word: 输入词语
        
        返回:
            同义词列表
        """
        synonyms = self.synonym_dict.get(word, [])
        
        # 如果有词向量，可以找相似词
        if self.word_embeddings and word in self.word_embeddings:
            word_vec = self.word_embeddings[word]
            
            # 计算相似词
            similar_words = self._find_similar_words(word_vec, top_k=5)
            synonyms.extend(similar_words)
        
        # 去重
        synonyms = list(set(synonyms))
        synonyms = [s for s in synonyms if s != word]
        
        return synonyms[:5]
    
    def _find_similar_words(
        self,
        word_vec: np.ndarray,
        top_k: int = 5
    ) -> List[str]:
        """查找相似词（简化版）"""
        # 实际实现需要计算所有词的相似度
        return []
    
    def context_aware_replace(
        self,
        sentence: str,
        n: int = 2,
        pos_filter: List[str] = None
    ) -> str:
        """
        上下文感知的替换
        
        参数:
            sentence: 输入句子
            n: 替换数量
            pos_filter: 词性过滤器
        
        返回:
            增强后的句子
        """
        # 分词（简化版）
        words = list(sentence)
        
        # 找出可替换的词
        replaceable = []
        for i, word in enumerate(words):
            if word in self.synonym_dict:
                replaceable.append(i)
        
        if not replaceable:
            return sentence
        
        # 随机选择替换
        n = min(n, len(replaceable))
        indices = random.sample(replaceable, n)
        
        for idx in indices:
            word = words[idx]
            synonyms = self.get_synonyms(word)
            
            if synonyms:
                # 根据上下文选择合适的同义词
                # 这里随机选择
                words[idx] = random.choice(synonyms)
        
        return ''.join(words)
