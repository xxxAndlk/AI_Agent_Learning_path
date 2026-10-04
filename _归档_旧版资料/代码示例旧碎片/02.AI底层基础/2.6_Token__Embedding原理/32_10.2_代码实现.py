# 安装: pip install sentencepiece

import sentencepiece as spm
import os

# 训练SentencePiece模型
def train_sentencepiece():
    """训练SentencePiece分词器"""
    
    # 准备训练语料（每行一条文本）
    corpus_file = "corpus.txt"
    with open(corpus_file, "w", encoding="utf-8") as f:
        texts = [
            "深度学习是机器学习的子领域",
            "自然语言处理让计算机理解人类语言",
            "人工智能改变世界",
            "计算机视觉处理图像和视频",
            "机器学习算法包括监督学习和无监督学习",
        ]
        f.write("\n".join(texts))
    
    # 训练参数
    train_command = f"""
    --input={corpus_file}
    --model_prefix=sentencepiece_model
    --vocab_size=1000
    --character_coverage=1.0
    --model_type=unigram
    --pad_id=0
    --unk_id=1
    --bos_id=2
    --eos_id=3
    """.replace("\n", " ")
    
    # 执行训练
    spm.SentencePieceTrainer.train(train_command)
    
    print("SentencePiece模型训练完成!")

# 使用预训练SentencePiece
def use_sentencepiece():
    """使用SentencePiece分词器"""
    
    # 加载模型
    sp = spm.SentencePieceProcessor()
    sp.load("sentencepiece_model.model")
    
    # 分词
    text = "深度学习非常有趣"
    pieces = sp.encode(text, out_type=str)
    ids = sp.encode(text, out_type=int)
    
    print(f"原文: {text}")
    print(f"分词: {pieces}")
    print(f"ID: {ids}")
    
    # 解码
    decoded = sp.decode(pieces)
    print(f"解码: {decoded}")
    
    # 获取词表大小
    print(f"词表大小: {sp.get_piece_size()}")

# 使用Hugging Face的SentencePiece
def use_huggingface_sentencepiece():
    """通过Hugging Face使用SentencePiece"""
    
    from transformers import XLNetTokenizer, T5Tokenizer
    
    # XLNet使用SentencePiece
    tokenizer = XLNetTokenizer.from_pretrained("xlnet-base-cased")
    
    text = "Natural language processing is fascinating"
    tokens = tokenizer.tokenize(text)
    ids = tokenizer.encode(text)
    
    print(f"XLNet (SentencePiece): {tokens}")
    print(f"IDs: {ids}")

use_sentencepiece()
