# Vision Transformer中的Patch Embedding
class PatchEmbedding(nn.Module):
    def __init__(self, img_size=224, patch_size=16, d_model=768):
        super().__init__()
        self.num_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(3, d_model, patch_size, patch_size)
    
    def forward(self, x):
        # x: (B, C, H, W)
        x = self.proj(x)  # (B, d_model, H/P, W/P)
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches, d_model)
        return x

# 后续应用标准自注意力
patches = patch_embed(images)
output = transformer_encoder(patches)
