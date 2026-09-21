class EnhancedRandomAugmenter:
    """增强的随机操作增强器"""
    
    def __init__(self):
        # 常用插入词
        self.insertion_words = {
            "确实": ["确实", "的确", "真的", "实在"],
            "非常": ["非常", "十分", "特别", "相当"],
            "因为": ["因为", "由于", "鉴于"],
            "所以": ["所以", "因此", "因而", "故"],
            "但是": ["但是", "然而", "不过", "只是"],
            "如果": ["如果", "假如", "倘若", "要是"],
            "虽然": ["虽然", "尽管", "固然"]
        }
        
        # 关键词（不易删除）
        self.key_words = {
            "是", "有", "在", "了", "和", "或", "与", "及",
            "的", "地", "得", "着", "过", "会", "能", "要"
        }
    
    def smart_insert(
        self,
        sentence: str,
        n: int = 2
    ) -> str:
        """
        智能插入 - 在合适的位置插入词
        
        参数:
            sentence: 输入句子
            n: 插入次数
        
        返回:
            增强后的句子
        """
        words = list(sentence)
        
        for _ in range(n):
            # 随机选择插入词
            insert_word_type = random.choice(list(self.insertion_words.keys()))
            insert_word = random.choice(self.insertion_words[insert_word_type])
            
            # 找到可能的插入位置（在关键词后）
            possible_positions = []
            for i, word in enumerate(words):
                if word in ["，", "。", "、", "；"]:
                    possible_positions.append(i)
            
            if not possible_positions:
                # 随机位置插入
                pos = random.randint(0, len(words))
            else:
                # 在标点后插入
                pos = random.choice(possible_positions) + 1
            
            words.insert(pos, insert_word)
        
        return ''.join(words)
    
    def smart_delete(
        self,
        sentence: str,
        p: float = 0.1
    ) -> str:
        """
        智能删除 - 避免删除关键词
        
        参数:
            sentence: 输入句子
            p: 删除概率
        
        返回:
            增强后的句子
        """
        words = list(sentence)
        
        if len(words) <= 2:
            return sentence
        
        # 分类词
        key_indices = [i for i, w in enumerate(words) if w in self.key_words]
        non_key_indices = [i for i, w in enumerate(words) if w not in self.key_words]
        
        if not non_key_indices:
            return sentence
        
        # 只在非关键词中随机删除
        new_words = []
        for i, word in enumerate(words):
            if i in key_indices:
                new_words.append(word)
            elif i in non_key_indices:
                if random.random() > p:
                    new_words.append(word)
        
        # 确保至少保留一些词
        if len(new_words) < 2:
            return sentence
        
        return ''.join(new_words)
    
    def sentence_swap(
        self,
        sentence: str,
        n: int = 1
    ) -> str:
        """
        句子级交换 - 按标点分割后交换
        
        参数:
            sentence: 输入句子
            n: 交换次数
        
        返回:
            增强后的句子
        """
        # 按标点分割
        import re
        parts = re.split(r'([，。、；！？])', sentence)
        
        # 过滤空部分
        parts = [p for p in parts if p.strip()]
        
        if len(parts) < 2:
            return sentence
        
        # 随机交换相邻部分
        for _ in range(n):
            if len(parts) >= 2:
                idx = random.randint(0, len(parts) - 2)
                parts[idx], parts[idx + 1] = parts[idx + 1], parts[idx]
        
        # 重新组合
        result = ''.join(parts)
        
        # 清理多余空格
        result = result.strip()
        
        return result
