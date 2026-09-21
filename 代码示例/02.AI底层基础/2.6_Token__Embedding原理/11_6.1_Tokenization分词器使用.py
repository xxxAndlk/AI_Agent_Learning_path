from transformers import AutoTokenizer  # 从transformers库导入分词器

# 加载BERT中文基础版分词器
# 会自动下载模型文件（如果本地不存在）
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

def tokenization_demo():
    """分词器使用演示"""
    # 示例文本：包含中英文混合内容
    text = "人工智能是引领未来的战略性技术，RAG是检索增强生成技术"
    
    # 1. 分词：将文本切分为子词（subword）单元
    tokens = tokenizer.tokenize(text)
    print("分词结果:", tokens)
    # 输出类似：['人', '工', '智', '能', '是', '引', '领', '未', '来', '的', '战', '略', '性', '技', '术', '，', 'rag', '是', '检', '索', '增', '强', '生', '成', '技', '术']
    # BERT中文分词特点：
    # - 中文按字符切分（每个汉字一个token）
    # - 英文按子词切分（rag保持完整）
    # - 标点符号单独处理
    
    # 2. 编码：将文本转为token ID序列
    # add_special_tokens=True 会自动添加[CLS]和[SEP]标记
    input_ids = tokenizer.encode(text, add_special_tokens=True)
    print("Token ID:", input_ids)
    # BERT格式：[CLS] + token_ids + [SEP]
    # [CLS] = 101: 句首标记，用于分类任务
    # [SEP] = 102: 句分隔标记，用于区分句子
    
    # 3. 解码：将token ID还原为文本
    decoded_text = tokenizer.decode(input_ids)
    print("解码还原文本:", decoded_text)
    # 注意：解码时特殊标记会被还原为可读形式
    
    # 4. 批量处理：同时处理多条文本
    batch_texts = [
        "我爱深度学习",
        "大语言模型的应用开发",
        "RAG技术可以解决大模型幻觉问题"
    ]
    
    # padding=True: 自动填充到最长序列
    # truncation=True: 超过max_length时截断
    # return_tensors="pt": 返回PyTorch张量
    batch_encoding = tokenizer(
        batch_texts,
        padding=True,                  # 填充（短的序列补0）
        truncation=True,               # 截断（长的序列截断）
        max_length=10,                 # 最大长度限制
        return_tensors="pt"            # 返回PyTorch张量格式
    )
    
    print("\n批量处理结果:")
    print("input_ids:\n", batch_encoding["input_ids"])
    # input_ids形状: (batch_size=3, seq_len=10)
    # 每行是一个句子的token ID序列，不足10的用0填充
    
    # attention_mask: 标记哪些位置是真实token（1）哪些是填充（0）
    print("attention_mask:\n", batch_encoding["attention_mask"])
    # 用途：让模型忽略padding位置，不参与计算
    # 示例: [1, 1, 1, 1, 1, 1, 0, 0, 0, 0] 表示前6个有效，后4个是填充

if __name__ == "__main__":
    tokenization_demo()
