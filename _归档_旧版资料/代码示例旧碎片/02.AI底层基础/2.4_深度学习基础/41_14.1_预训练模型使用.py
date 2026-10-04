import torchvision.models as models
import torch.nn as nn

# 方法1：使用PyTorch内置的预训练模型
def use_pretrained_models():
    """使用PyTorch预训练模型"""
    
    # 加载ImageNet预训练的ResNet-18
    resnet = models.resnet18(pretrained=True)
    print(f"ResNet-18 预训练参数数量: {sum(p.numel() for p in resnet.parameters()):,}")
    
    # 加载VGG-16
    vgg = models.vgg16(pretrained=True)
    
    # 加载MobileNet（轻量级）
    mobilenet = models.mobilenet_v2(pretrained=True)
    
    # 加载EfficientNet
    efficientnet = models.efficientnet_b0(pretrained=True)
    
    # 查看模型结构
    print(resnet)
    
    # 使用现代的预训练API
    # PyTorch 0.4+ 推荐写法
    resnet_new = models.resnet18(weights='IMAGENET1K_V1')

# 方法2：修改预训练模型的最后几层
def modify_pretrained_model(num_classes=10):
    """修改预训练模型的分类头"""
    
    # 加载预训练的ResNet
    model = models.resnet18(pretrained=True)
    
    # 方法1：直接替换最后的全连接层
    num_features = model.fc.in_features  # 获取输入特征维度
    model.fc = nn.Linear(num_features, num_classes)
    
    # 方法2：添加新的分类头
    model.classifier = nn.Sequential(
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )
    
    # 方法3：冻结部分层，只训练新添加的层
    # 冻结所有卷积层参数
    for param in model.parameters():
        param.requires_grad = False
    
    # 只解冻最后几层
    for param in model.layer4.parameters():
        param.requires_grad = True
    
    # 新的分类层默认requires_grad=True
    # 优化器只优化requires_grad=True的参数
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()))
    
    return model
