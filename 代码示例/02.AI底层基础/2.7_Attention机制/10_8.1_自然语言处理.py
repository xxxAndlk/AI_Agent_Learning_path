# 机器翻译中的Cross-Attention示例
class TranslatorDecoder(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.cross_attn = MultiHeadAttention(d_model, num_heads)
    
    def forward(self, tgt, encoder_output, tgt_mask=None, src_mask=None):
        # 自注意力：解码器内部
        x, _ = self.self_attn(tgt, tgt, tgt, tgt_mask)
        
        # 交叉注意力：查询解码器，键值来自编码器
        x, attention = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        
        return x, attention
