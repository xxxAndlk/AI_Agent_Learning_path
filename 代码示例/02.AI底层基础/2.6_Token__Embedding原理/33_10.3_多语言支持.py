# 多语言分词示例
def multilingual_tokenization():
    """多语言文本分词"""
    
    from transformers import XLMRobertaTokenizer
    
    # 加载多语言RoBERTa模型
    tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")
    
    # 多语言文本
    texts = [
        "Hello world",                                    # 英语
        "你好世界",                                       # 中文
        "こんにちは世界",                                 # 日语
        "안녕하세요 세계",                                # 韩语
        "مرحبا بالعالم",                                 # 阿拉伯语
        "Привет мир",                                    # 俄语
    ]
    
    print("多语言分词测试:")
    print("-" * 50)
    
    for text in texts:
        tokens = tokenizer.tokenize(text)
        ids = tokenizer.encode(text)
        
        print(f"文本: {text}")
        print(f"  Tokens: {tokens}")
        print(f"  Token数: {len(tokens)}")
        print()

multilingual_tokenization()

# 输出说明：
# - SentencePiece可以将任意语言的文本统一编码
# - 不需要语言特定的预处理
# - 适合多语言模型训练
