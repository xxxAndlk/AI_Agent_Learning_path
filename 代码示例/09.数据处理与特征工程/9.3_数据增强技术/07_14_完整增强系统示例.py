"""
完整的数据增强系统

包含多种增强方法的组合使用
"""

from typing import List, Dict, Any
import random

class TextAugmentationSystem:
    """文本数据增强系统"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化增强系统
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        
        # 初始化各个增强器
        self.eda = EDA()
        self.back_translator = BackTranslationAugmenter()
        self.llm_generator = LLMTextGenerator()
        
        # 增强方法配置
        self.augmentation_rates = self.config.get('rates', {
            'synonym_replace': 0.3,
            'random_insert': 0.2,
            'random_swap': 0.2,
            'random_delete': 0.2,
            'back_translation': 0.1,
            'llm_generation': 0.1
        })
    
    def augment_single(
        self,
        text: str,
        method: str = 'all'
    ) -> List[str]:
        """
        对单条文本进行增强
        
        参数:
            text: 原始文本
            method: 增强方法 ('eda', 'back_translation', 'llm', 'all')
        
        返回:
            增强后的文本列表
        """
        results = []
        
        if method in ['eda', 'all']:
            # EDA增强
            eda_results = self.eda.augment(text, num_augments=4)
            results.extend(eda_results)
        
        if method in ['back_translation', 'all']:
            # 回译增强
            bt_results = self.back_translator.augment(text, num_augments=2)
            results.extend(bt_results)
        
        if method in ['llm', 'all']:
            # LLM生成增强
            llm_results = self.llm_generator.augment(text, num_augments=3)
            results.extend(llm_results)
        
        # 去重
        results = list(set(results))
        
        return results
    
    def augment_batch(
        self,
        texts: List[str],
        samples_per_text: int = 5,
        method: str = 'all'
    ) -> List[str]:
        """
        批量增强文本
        
        参数:
            texts: 原始文本列表
            samples_per_text: 每条文本生成的增强样本数
            method: 增强方法
        
        返回:
            所有增强后的文本列表
        """
        all_augmented = []
        
        for text in texts:
            # 对每条文本进行增强
            augmented = self.augment_single(text, method)
            
            # 随机采样
            if len(augmented) > samples_per_text:
                augmented = random.sample(augmented, samples_per_text)
            
            all_augmented.extend(augmented)
        
        return all_augmented
    
    def balance_dataset(
        self,
        texts: List[str],
        target_count: int = None
    ) -> List[str]:
        """
        平衡数据集
        
        参数:
            texts: 原始文本列表
            target_count: 目标数量
        
        返回:
            增强后的文本列表
        """
        if target_count is None:
            target_count = len(texts) * 2
        
        augmented = list(texts)
        
        # 循环增强直到达到目标数量
        while len(augmented) < target_count:
            for text in texts:
                if len(augmented) >= target_count:
                    break
                
                # 随机选择增强方法
                method = random.choice(['eda', 'llm', 'back_translation'])
                new_texts = self.augment_single(text, method)
                
                if new_texts:
                    augmented.extend(random.sample(new_texts, 1))
        
        return augmented


def main():
    """测试主函数"""
    # 创建增强系统
    augmenter = TextAugmentationSystem()
    
    # 测试文本
    test_texts = [
        "这个产品质量很好，推荐购买",
        "学习新技术需要不断练习",
        "人工智能正在改变我们的生活方式"
    ]
    
    print("=" * 60)
    print("数据增强系统测试")
    print("=" * 60)
    
    for text in test_texts:
        print(f"\n原始文本: {text}")
        print("-" * 40)
        
        # 增强
        augmented = augmenter.augment_single(text, method='all')
        
        print(f"生成 {len(augmented)} 个增强样本:")
        for i, aug_text in enumerate(augmented, 1):
            print(f"  {i}. {aug_text}")


if __name__ == "__main__":
    main()
