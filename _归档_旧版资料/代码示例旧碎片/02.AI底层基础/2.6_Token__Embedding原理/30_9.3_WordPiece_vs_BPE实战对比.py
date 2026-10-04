from transformers import BertTokenizer, GPT2Tokenizer

def compare_tokenizers():
    """对比WordPiece和BPE分词器"""
    
    texts = [
        "unhappiness",
        "unfriendly",
        "antidisestablishmentarianism",
        "深度学习",
    ]
    
    # WordPiece (BERT)
    bert_tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    
    # BPE (GPT-2)
    gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    gpt2_tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    
    print("=" * 60)
    print("WordPiece vs BPE 对比")
    print("=" * 60)
    
    for text in texts:
        wp_tokens = bert_tokenizer.tokenize(text) if text.isascii() else list(text)
        # 中文按字符分词
        if not text.isascii():
            wp_tokens = list(text)
        
        # GPT-2 BPE分词
        bpe_tokens = gpt2_tokenizer.tokenize(text)
        
        print(f"\n原文: {text}")
        print(f"WordPiece: {wp_tokens}")
        print(f"BPE:       {bpe_tokens}")
        print(f"WordPiece长度: {len(wp_tokens)}, BPE长度: {len(bpe_tokens)}")

compare_tokenizers()

# 输出示例：
# 原文: unhappiness
# WordPiece: ['un', '##happ', '##in', '##ess']
# BPE:       ['un', 'happ', 'in', 'ess']
# 
# 特点：
# - WordPiece用'##'标记子词的延续
# - BPE直接拆分，粒度可能更细
