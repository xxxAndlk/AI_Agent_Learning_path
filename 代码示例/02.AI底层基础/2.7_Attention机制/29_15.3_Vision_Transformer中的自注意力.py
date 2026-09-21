class VisionTransformerAttention(nn.Module):
    """Vision Transformer (ViT) 自注意力
    
    将图像划分为patches，然后应用标准自注意力。
    """
    
    def __init__(self, d_model, num_heads, img_size=224, patch_size=16):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2 + 1  # +1 for CLS
        
        # Patch嵌入
        self.patch_embed = nn.Conv2d(3, d_model, patch_size, patch_size)
        
        # 位置编码
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, d_model))
        
        # CLS token
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
        
        # 注意力
        self.attention = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        
        # 层归一化
        self.norm = nn.LayerNorm(d_model)
        
        # 初始化
        nn.init.normal_(self.cls_token, std=0.02)
        nn.init.normal_(self.pos_embed, std=0.02)
    
    def forward(self, x):
        """
        x: (batch, 3, img_size, img_size)
        """
        batch_size = x.shape[0]
        
        # 1. Patch embedding
        x = self.patch_embed(x)  # (B, d_model, H/P, W/P)
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches-1, d_model)
        
        # 2. 添加CLS token
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)  # (B, num_patches, d_model)
        
        # 3. 添加位置编码
        x = x + self.pos_embed
        
        # 4. 自注意力
        attn_output, attn_weights = self.attention(x, x, x)
        
        # 5. 层归一化
        x = self.norm(attn_output)
        
        return x, attn_weights


class SelfAttentionCV(nn.Module):
    """自注意力在计算机视觉中的其他应用
    
    非ViT架构中的自注意力层，可插入到CNN中。
    """
    
    def __init__(self, in_channels, num_heads=8):
        super().__init__()
        self.in_channels = in_channels
        self.num_heads = num_heads
        self.head_dim = in_channels // num_heads
        
        # 三个投影
        self.query = nn.Conv2d(in_channels, in_channels, 1)
        self.key = nn.Conv2d(in_channels, in_channels, 1)
        self.value = nn.Conv2d(in_channels, in_channels, 1)
        
        # 输出投影
        self.out_proj = nn.Conv2d(in_channels, in_channels, 1)
        
        self.norm = nn.BatchNorm2d(in_channels)
    
    def forward(self, x):
        """
        x: (batch, channels, height, width)
        """
        batch, channels, height, width = x.shape
        
        # 投影并reshape为 (B, H, num_heads, head_dim)
        Q = self.query(x).reshape(batch, self.num_heads, self.head_dim, height * width)
        K = self.key(x).reshape(batch, self.num_heads, self.head_dim, height * width)
        V = self.value(x).reshape(batch, self.num_heads, self.head_dim, height * width)
        
        # 转置用于矩阵乘法
        Q = Q.transpose(-2, -1)  # (B, num_heads, H*W, head_dim)
        K = K.transpose(-2, -1)
        V = V.transpose(-2, -1)
        
        # 缩放点积注意力
        scale = math.sqrt(self.head_dim)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / scale
        attn = F.softmax(scores, dim=-1)
        
        # 加权求和
        out = torch.matmul(attn, V)  # (B, num_heads, H*W, head_dim)
        
        # reshape回空间形式
        out = out.transpose(-2, -1).reshape(batch, channels, height, width)
        
        # 输出投影
        out = self.out_proj(out)
        out = self.norm(out)
        
        # 残差连接
        out = out + x
        
        return out, attn
