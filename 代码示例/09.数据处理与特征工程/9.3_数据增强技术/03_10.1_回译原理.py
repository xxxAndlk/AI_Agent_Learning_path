from typing import List, Optional
import random
import time

class BackTranslationAugmenter:
    """回译数据增强器"""
    
    def __init__(
        self,
        translator=None,
        target_languages: List[str] = None
    ):
        """
        初始化回译增强器
        
        参数:
            translator: 翻译器对象
            target_languages: 目标语言列表
        """
        self.translator = translator
        # 默认目标语言（中文可用的回译目标）
        self.target_languages = target_languages or [
            'en', 'ja', 'ko', 'fr', 'de', 'es', 'ru'
        ]
    
    def back_translate(
        self,
        sentence: str,
        target_lang: str = None,
        intermediate_lang: str = 'en'
    ) -> Optional[str]:
        """
        执行回译
        
        参数:
            sentence: 原始句子
            target_lang: 目标语言（可选，随机选择）
            intermediate_lang: 中间语言
        
        返回:
            回译后的句子
        """
        # 随机选择目标语言
        if target_lang is None:
            target_lang = random.choice(self.target_languages)
        
        try:
            # 步骤1: 原始语言 -> 目标语言
            if self.translator:
                translated = self.translator.translate(
                    sentence,
                    src=intermediate_lang,
                    dest=target_lang
                )
                time.sleep(0.1)  # 避免请求过快
                
                # 步骤2: 目标语言 -> 原始语言
                back_translated = self.translator.translate(
                    translated,
                    src=target_lang,
                    dest=intermediate_lang
                )
                
                return back_translated
            
            # 如果没有翻译器，返回模拟结果
            return f"[回译] {sentence}"
            
        except Exception as e:
            print(f"回译失败: {e}")
            return None
    
    def augment(
        self,
        sentence: str,
        num_augments: int = 3,
        use_multiple_langs: bool = True
    ) -> List[str]:
        """
        回译增强
        
        参数:
            sentence: 原始句子
            num_augments: 生成数量
            use_multiple_langs: 是否使用多种语言
        
        返回:
            增强后的句子列表
        """
        augmented = []
        
        if use_multiple_langs:
            # 使用多种语言进行回译
            selected_langs = random.sample(
                self.target_languages,
                min(num_augments, len(self.target_languages))
            )
            
            for lang in selected_langs:
                result = self.back_translate(sentence, target_lang=lang)
                if result:
                    augmented.append(result)
        else:
            # 使用单一语言
            for _ in range(num_augments):
                result = self.back_translate(sentence)
                if result:
                    augmented.append(result)
        
        return augmented


class MockTranslator:
    """模拟翻译器（用于测试）"""
    
    def __init__(self):
        # 模拟翻译字典
        self.translations = {
            ('hello', 'en', 'zh'): '你好',
            ('hello', 'zh', 'en'): 'hello',
            ('good', 'en', 'zh'): '好',
            ('good', 'zh', 'en'): 'good',
        }
    
    def translate(self, text: str, src: str, dest: str) -> str:
        """翻译方法"""
        key = (text, src, dest)
        
        if key in self.translations:
            return self.translations[key]
        
        # 模拟翻译（添加标记）
        return f"[{dest}]{text}[/{dest}]"
