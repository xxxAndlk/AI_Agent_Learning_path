import sentencepiece as spm
from pathlib import Path

class CustomSentencePiece:
    """自定义SentencePiece分词器"""
    
    def __init__(self, model_prefix="custom_sp"):
        self.model_prefix = model_prefix
        self.sp = None
    
    def train(self, texts, vocab_size=8000):
        """训练分词器
        
        参数:
            texts: 文本列表
            vocab_size: 词表大小
        """
        # 写入临时文件
        temp_file = "temp_corpus.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("\n".join(texts))
        
        # 训练参数
        spm.SentencePieceTrainer.train(
            input=temp_file,
            model_prefix=self.model_prefix,
            vocab_size=vocab_size,
            character_coverage=0.9995,  # 字符覆盖率
            model_type='unigram',       # 或 'bpe', 'char', 'word'
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
            pad_piece='<pad>',
            unk_piece='<unk>',
            bos_piece='<s>',
            eos_piece='</s>',
        )
        
        # 加载模型
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(f"{self.model_prefix}.model")
        
        print(f"训练完成! 词表大小: {self.sp.get_piece_size()}")
        
        # 清理临时文件
        Path(temp_file).unlink()
    
    def tokenize(self, text):
        """分词"""
        return self.sp.encode(text, out_type=str)
    
    def encode(self, text, add_bos_eos=False):
        """编码"""
        if add_bos_eos:
            return self.sp.encode(text)
        return self.sp.encode(text)
    
    def decode(self, pieces):
        """解码"""
        return self.sp.decode(pieces)

# 使用示例
if __name__ == "__main__":
    # 准备训练数据
    training_texts = [
        "深度学习是人工智能的核心技术",
        "机器学习包括监督学习和无监督学习",
        "自然语言处理用于文本分析",
        "计算机视觉用于图像识别",
        "Transformer模型改变了NLP领域",
    ]
    
    # 训练
    sp = CustomSentencePiece("my_sp")
    sp.train(training_texts, vocab_size=100)
    
    # 测试
    test_text = "深度学习很有意思"
    tokens = sp.tokenize(test_text)
    ids = sp.encode(test_text)
    decoded = sp.decode(tokens)
    
    print(f"测试文本: {test_text}")
    print(f"分词结果: {tokens}")
    print(f"ID序列: {ids}")
    print(f"解码结果: {decoded}")
