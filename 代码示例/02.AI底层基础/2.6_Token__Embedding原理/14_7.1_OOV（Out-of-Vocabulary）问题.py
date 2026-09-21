# 问题示例
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
text = "这是一些不存在的新词：YYDS、绝绝子"

tokens = tokenizer.tokenize(text)
# "YYDS"、"绝绝子" 可能被拆分为字符或标记为[UNK]
