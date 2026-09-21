class TransformerEncoder(nn.Module):
    """完整的Transformer编码器
    
    由多个TransformerEncoderBlock堆叠而成
    """
    def __init__(self, vocab_size, embed_size, num_layers, heads, 
                 forward_expansion, dropout, max_seq_len):
        super().__init__()
        
        # 词嵌入层
        self.word_embedding = nn.Embedding(vocab_size, embed_size)
        
        # 位置编码
        self.position_encoding = PositionalEncoding(embed_size, max_seq_len, dropout)
        
        # 堆叠多个编码器块
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(embed_size, heads, forward_expansion, dropout)
            for _ in range(num_layers)
        ])
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        """
        x: (batch_size, seq_len) - 输入token索引
        """
        # 词嵌入 + 位置编码
        x = self.word_embedding(x)
        x = self.position_encoding(x)
        
        # 通过所有编码器层
        for layer in self.layers:
            x = layer(x, mask)
        
        return x


if __name__ == "__main__":
    # 测试Transformer编码器块
    embed_size = 256                  # 嵌入维度
    heads = 8                         # 8个注意力头
    forward_expansion = 4             # 前馈网络扩展4倍
    dropout = 0.1                     # Dropout概率10%
    
    # 创建编码器块实例
    encoder_block = TransformerEncoderBlock(embed_size, heads, forward_expansion, dropout)
    
    # 创建随机输入：batch_size=32, seq_len=10, embed_size=256
    x = torch.randn(32, 10, embed_size)
    
    # 前向传播
    output = encoder_block(x)
    
    print("Transformer编码器输入形状:", x.shape)
    print("Transformer编码器输出形状:", output.shape)
    
    # 测试完整编码器
    print("\n=== 测试完整Transformer编码器 ===")
    vocab_size = 10000
    num_layers = 6
    max_seq_len = 512
    
    encoder = TransformerEncoder(
        vocab_size=vocab_size,
        embed_size=embed_size,
        num_layers=num_layers,
        heads=heads,
        forward_expansion=forward_expansion,
        dropout=dropout,
        max_seq_len=max_seq_len
    )
    
    # 模拟输入token序列
    input_ids = torch.randint(0, vocab_size, (32, 20))
    output = encoder(input_ids)
    print(f"输入token形状: {input_ids.shape}")
    print(f"编码器输出形状: {output.shape}")
