# 错误示范：padding参与平均
embeddings = model(input_ids)  # (batch, seq_len, dim)
mean_pool = embeddings.mean(dim=1)  # padding也参与了平均！

# 正确做法：使用attention_mask
embeddings = model(input_ids)
mask = attention_mask.unsqueeze(-1).expand(embeddings.shape).float()
sum_embeddings = (embeddings * mask).sum(dim=1)
sum_mask = mask.sum(dim=1)
mean_pool = sum_embeddings / sum_mask  # 只对真实token平均
