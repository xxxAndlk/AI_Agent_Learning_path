from transformers import BertTokenizer

# 加载BERT的WordPiece分词器
tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")

text = "深度学习在人工智能领域有广泛应用"

# 分词
tokens = tokenizer.tokenize(text)
print("分词结果:", tokens)
# 输出: ['深', '度', '学', '习', '在', '人', '工', '智', '能', '领', '域', '有', '广', '泛', '应', '用']

# 编码为ID
input_ids = tokenizer.encode(text, add_special_tokens=True)
print("Token IDs:", input_ids)
# BERT会添加[CLS]和[SEP]

# 查看词表中的子词
print("词表大小:", tokenizer.vocab_size)
print("是否是WordPiece:", hasattr(tokenizer, 'wordpiece_tokenizer'))

# 未知词处理：看WordPiece如何处理OOV
text_oov = "这是一个超长新词汇automorphism"
tokens_oov = tokenizer.tokenize(text_oov)
print("OOV分词:", tokens_oov)
# 英文单词会被拆分为子词：['这', '是', '一', '个', '超', '长', '新', '词', '汇', 'au', '##to', '##morph', '##ism']
# '##'表示该token是前一个token的延续
