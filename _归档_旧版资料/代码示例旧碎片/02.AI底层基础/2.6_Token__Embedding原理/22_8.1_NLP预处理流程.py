from transformers import AutoTokenizer

class TextPreprocessor:
    """文本预处理管道"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def preprocess(self, texts, max_length=512):
        """完整预处理流程"""
        
        # 1. 清洗（可选）
        cleaned = [self._clean(t) for t in texts]
        
        # 2. 分词 + 编码
        encoded = self.tokenizer(
            cleaned,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        return encoded
    
    def _clean(self, text):
        """文本清洗"""
        import re
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 去除特殊字符（根据需要）
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        return text.strip()

# 使用示例
preprocessor = TextPreprocessor()
texts = ["这是一段文本", "这是另一段更长的文本"]
encoded = preprocessor.preprocess(texts)
