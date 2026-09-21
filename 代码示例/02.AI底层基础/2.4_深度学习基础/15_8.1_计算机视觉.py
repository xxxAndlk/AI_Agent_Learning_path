# 图像分类完整示例
class ImageClassifier(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # 使用预训练模型
        self.backbone = models.resnet18(pretrained=True)
        # 替换最后一层
        self.backbone.fc = nn.Linear(512, num_classes)
    
    def forward(self, x):
        return self.backbone(x)
