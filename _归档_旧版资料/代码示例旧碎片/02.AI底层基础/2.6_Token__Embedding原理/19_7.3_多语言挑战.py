# 方案1：统一词表
# 所有语言共享一个词表
# 优点：跨语言迁移
# 缺点：词表巨大（10万+）

# 方案2：语言特定adapter
# 共享底层，上层分语言
# 优点：语言特化
# 缺点：架构复杂

# 推荐：使用现成的多语言模型
model = AutoModel.from_pretrained("xlm-roberta-base")  # 100种语言
