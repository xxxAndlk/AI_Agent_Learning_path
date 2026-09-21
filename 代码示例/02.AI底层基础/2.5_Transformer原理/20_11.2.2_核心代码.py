class BERTConfig:
    """BERT配置参数"""
    vocab_size = 30528
    hidden_size = 768
    num_hidden_layers = 12
    num_attention_heads = 12
    intermediate_size = 3072  # 4 * hidden_size
    hidden_dropout_prob = 0.1
    max_position_embeddings = 512

class BERT(nn.Module):
    """BERT模型实现"""
    
    def __init__(self, config: BERTConfig):
        super().__init__()
        self.config = config
        
        # 词嵌入 + 位置嵌入 + Token Type嵌入
        self.embeddings = nn.ModuleDict({
            'word_embeddings': nn.Embedding(config.vocab_size, config.hidden_size),
            'position_embeddings': nn.Embedding(config.max_position_embeddings, config.hidden_size),
            'token_type_embeddings': nn.Embedding(2, config.hidden_size)
        })
        
        # 编码器层
        self.encoder = nn.ModuleList([
            TransformerEncoderBlock(
                config.hidden_size,
                config.num_attention_heads,
                4,  # forward_expansion
                config.hidden_dropout_prob
            ) for _ in range(config.num_hidden_layers)
        ])
        
        # Pooler层
        self.pooler = nn.Linear(config.hidden_size, config.hidden_size)
        
        # 输出层（用于MLM和NSP）
        self.cls = nn.ModuleDict({
            'predictions': nn.Linear(config.hidden_size, config.vocab_size),
            'seq_relationship': nn.Linear(config.hidden_size, 2)
        })
    
    def forward(self, input_ids, token_type_ids=None, attention_mask=None):
        # 嵌入层
        sequence_output = self._embed(input_ids, token_type_ids)
        
        # 编码器
        for layer in self.encoder:
            sequence_output = layer(sequence_output, attention_mask)
        
        # Pooler
        pooled_output = torch.tanh(self.pooler(sequence_output[:, 0]))
        
        return {
            'sequence_output': sequence_output,
            'pooled_output': pooled_output
        }
    
    def _embed(self, input_ids, token_type_ids):
        # 词嵌入
        word_embeds = self.embeddings['word_embeddings'](input_ids)
        
        # 位置嵌入
        position_ids = torch.arange(input_ids.size(1), device=input_ids.device)
        position_embeds = self.embeddings['position_embeddings'](position_ids)
        
        # Token type嵌入
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)
        token_type_embeds = self.embeddings['token_type_embeddings'](token_type_ids)
        
        return word_embeds + position_embeds + token_type_embeds
