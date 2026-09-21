from tokenizers import Tokenizer, models, pre_tokenizers, trainers
from pathlib import Path
import glob

def train_large_corpus_tokenizer():
    """大规模语料训练"""
    
    # 1. 收集所有语料文件
    corpus_dir = "./corpus"
    corpus_files = glob.glob(f"{corpus_dir}/*.txt")
    
    if not corpus_files:
        print("没有找到语料文件，跳过训练")
        return
    
    # 2. 创建tokenizer
    tokenizer = Tokenizer(models.BPE())
    
    # 3. 优化预分词器
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.Whitespace(),
        pre_tokenizers.Punctuation(),
        pre_tokenizers.Digits(individual_digits=True),  # 数字分割
    ])
    
    # 4. 训练配置
    trainer = trainers.BpeTrainer(
        vocab_size=30000,
        min_frequency=3,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
        show_progress=True,
        # 加速训练
        length=5000000,  # 只使用前500万个token
    )
    
    # 5. 训练（支持多文件）
    tokenizer.train(files=corpus_files, trainer=trainer)
    
    # 6. 添加后处理
    from tokenizers.processors import TemplateProcessing
    
    tokenizer.post_processor = TemplateProcessing(
        single="$A [SEP]",
        pair="$A [SEP] $B:1 [SEP]:1",
        special_tokens=[("[SEP]", 2)],
    )
    
    # 7. 保存
    tokenizer.save("large_vocab_tokenizer.json")
    print("大规模Tokenizer训练完成!")

# 示例：分块训练大文件
def train_chunked():
    """分块训练大文件"""
    
    # 适合内存有限的情况
    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    
    trainer = trainers.BpeTrainer(
        vocab_size=10000,
        min_frequency=2,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
    )
    
    # 逐文件训练
    corpus_files = ["corpus1.txt", "corpus2.txt", "corpus3.txt"]
    
    for file in corpus_files:
        if Path(file).exists():
            tokenizer.train(files=[file], trainer=trainer)
            print(f"已完成: {file}")
    
    tokenizer.save("merged_tokenizer.json")

train_chunked()
