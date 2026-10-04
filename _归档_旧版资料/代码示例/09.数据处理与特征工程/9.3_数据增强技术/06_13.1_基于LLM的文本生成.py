from typing import Dict, Any

class LLMTextGenerator:
    """基于LLM的文本生成增强器"""
    
    def __init__(self, llm_model=None):
        """
        初始化生成器
        
        参数:
            llm_model: LLM模型对象
        """
        self.llm = llm_model
    
    def generate_paraphrase(
        self,
        sentence: str,
        num_samples: int = 3
    ) -> List[str]:
        """
        生成改写句子
        
        参数:
            sentence: 原始句子
            num_samples: 生成数量
        
        返回:
            改写句子列表
        """
        if not self.llm:
            # 模拟生成
            return [
                f"[改写{i}] {sentence}"
                for i in range(num_samples)
            ]
        
        prompt = f"""请生成3个与以下句子语义相同但表达不同的改写句子：

原句：{sentence}

要求：
1. 保持相同语义
2. 使用不同的词语和句式
3. 每行一个改写

改写句子："""
        
        response = self.llm.invoke(prompt)
        
        # 解析结果
        paraphrases = [
            line.strip()
            for line in response.strip().split('\n')
            if line.strip()
        ]
        
        return paraphrases[:num_samples]
    
    def generate_expansion(
        self,
        sentence: str,
        num_samples: int = 2
    ) -> List[str]:
        """
        生成扩展句子
        
        参数:
            sentence: 原始句子
            num_samples: 生成数量
        
        返回:
            扩展句子列表
        """
        if not self.llm:
            return [f"[扩展] {sentence}的情况" for _ in range(num_samples)]
        
        prompt = f"""请为以下句子生成{num_samples}个更详细的扩展描述：

原句：{sentence}

扩展描述："""
        
        response = self.llm.invoke(prompt)
        
        expansions = [
            line.strip()
            for line in response.strip().split('\n')
            if line.strip()
        ]
        
        return expansions[:num_samples]
    
    def generate_contraction(
        self,
        sentence: str,
        num_samples: int = 2
    ) -> List[str]:
        """
        生成简缩句子
        
        参数:
            sentence: 原始句子
            num_samples: 生成数量
        
        返回:
            简化句子列表
        """
        if not self.llm:
            return [f"[简化] {sentence[:10]}..." for _ in range(num_samples)]
        
        prompt = f"""请将以下句子简化为最核心的意思，只保留关键词：

原句：{sentence}

简化版本："""
        
        response = self.llm.invoke(prompt)
        
        contractions = [
            line.strip()
            for line in response.strip().split('\n')
            if line.strip()
        ]
        
        return contractions[:num_samples]
    
    def augment(
        self,
        sentence: str,
        num_augments: int = 5
    ) -> List[str]:
        """
        综合增强 - 使用多种生成方法
        
        参数:
            sentence: 原始句子
            num_augments: 生成总量
        
        返回:
            增强后的句子列表
        """
        augmented = []
        
        # 生成改写
        paraphrases = self.generate_paraphrase(sentence, num_samples=2)
        augmented.extend(paraphrases)
        
        # 生成扩展
        if len(augmented) < num_augments:
            expansions = self.generate_expansion(sentence, num_samples=2)
            augmented.extend(expansions)
        
        # 生成简化
        if len(augmented) < num_augments:
            contractions = self.generate_contraction(sentence, num_samples=2)
            augmented.extend(contractions)
        
        return augmented[:num_augments]
