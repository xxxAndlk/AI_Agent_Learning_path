# 场景1：分析BERT分词特点
def analyze_bert_tokenization():
    """分析BERT分词器的分词行为"""
    
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    
    test_cases = [
        "人工智能",
        "AI和ML",
        "Transformer模型",
        "12345数字",
    ]
    
    for text in test_cases:
        tokens = tokenizer.tokenize(text)
        ids = tokenizer.convert_tokens_to_ids(tokens)
        
        print(f"文本: {text}")
        print(f"  Tokens: {tokens}")
        print(f"  IDs: {ids}")
        print()

analyze_bert_tokenization()

# 场景2：子词还原与拼接
def subword_handling():
    """处理子词拼接"""
    
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    
    # 子词拼接示例
    tokens = ['人', '工', '智', '能']
    
    # 检测子词（以##开头）
    def merge_subwords(tokens):
        """将子词拼接回完整词"""
        words = []
        current = ""
        for token in tokens:
            if token.startswith("##"):
                current += token[2:]
            else:
                if current:
                    words.append(current)
                current = token
        if current:
            words.append(current)
        return words
    
    # 测试
    subword_tokens = ['un', '##friend', '##ly']
    merged = merge_subwords(subword_tokens)
    print(f"子词拼接: {subword_tokens} -> {merged}")

subword_handling()
