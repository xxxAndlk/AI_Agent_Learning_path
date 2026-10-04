# CLIP风格的图文注意力
class CrossModalAttention(nn.Module):
    """图文跨模态注意力"""
    
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads)
    
    def forward(self, text_features, image_features):
        """
        text_features: (B, L_text, D)
        image_features: (B, L_image, D)
        """
        # 文本查询图像：文本关注相关的图像区域
        text_to_image, _ = self.attention(
            query=text_features,
            key=image_features,
            value=image_features
        )
        
        # 图像查询文本：图像关注相关的文本描述
        image_to_text, _ = self.attention(
            query=image_features,
            key=text_features,
            value=text_features
        )
        
        return text_to_image, image_to_text
