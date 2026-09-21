from transformers import AutoTokenizer, PreTrainedTokenizerFast
from tokenizers import Tokenizer, models, pre_tokenizers, trainers

def train_with_huggingface():
    """使用Hugging Face训练Tokenizer"""
    
    # 方法1: 使用tokenizers库训练，然后转换为Hugging Face格式
    
    # 训练基础tokenizer
    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    
    trainer = trainers.BpeTrainer(
        vocab_size=5000,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    )
    
    # 准备语料
    corpus = [
        "深度学习技术正在改变世界",
        "人工智能在各个领域有广泛应用",
        "自然语言处理让计算机理解人类语言",
    ]
    
    with open("corpus_hf.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(corpus))
    
    tokenizer.train(files=["corpus_hf.txt"], trainer=trainer)
    
    # 转换为Hugging Face格式
    hf_tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
    )
    
    # 保存
    hf_tokenizer.save_pretrained("my_tokenizer")
    print("Tokenizer已保存到 my_tokenizer 目录")
    
    # 加载使用
    loaded_tokenizer = AutoTokenizer.from_pretrained("my_tokenizer")
    
    text = "深度学习是AI的核心"
    tokens = loaded_tokenizer.tokenize(text)
    ids = loaded_tokenizer.encode(text)
    
    print(f"分词: {tokens}")
    print(f"IDs: {ids}")

train_with_huggingface()
