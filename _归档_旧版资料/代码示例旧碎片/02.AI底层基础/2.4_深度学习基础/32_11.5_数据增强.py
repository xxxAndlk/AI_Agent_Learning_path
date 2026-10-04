import numpy as np
from torchvision import transforms

# 图像数据增强
image_augmentation = transforms.Compose([
    # 1. 随机水平翻转
    transforms.RandomHorizontalFlip(p=0.5),
    
    # 2. 随机垂直翻转（某些场景）
    transforms.RandomVerticalFlip(p=0.2),
    
    # 3. 随机旋转
    transforms.RandomRotation(degrees=15),  # ±15度
    
    # 4. 随机裁剪并调整大小
    transforms.RandomResizedCrop(
        size=224, 
        scale=(0.8, 1.0),  # 裁剪比例范围
        ratio=(0.9, 1.1)   # 宽高比范围
    ),
    
    # 5. 颜色抖动
    transforms.ColorJitter(
        brightness=0.2,   # 亮度
        contrast=0.2,     # 对比度
        saturation=0.2,   # 饱和度
        hue=0.1           # 色相
    ),
    
    # 6. 随机灰度化
    transforms.RandomGrayscale(p=0.1),
    
    # 7. 随机仿射变换
    transforms.RandomAffine(
        degrees=0,
        translate=(0.1, 0.1),  # 平移
        scale=(0.9, 1.1),      # 缩放
        shear=5                # 剪切
    ),
    
    # 8. 随机 erasing（随机遮挡）
    transforms.RandomErasing(p=0.3, scale=(0.02, 0.2)),
    
    # 9. 归一化（最后进行）
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# 文本数据增强
class TextAugmentation:
    """文本数据增强方法"""
    
    @staticmethod
    def random_deletion(tokens, p=0.1):
        """随机删除：随机删除部分token"""
        if len(tokens) == 1:
            return tokens
        return [t for t in tokens if random.random() > p or random.random() < 0.25]
    
    @staticmethod
    def random_swap(tokens, n=1):
        """随机交换：随机交换两个token的位置"""
        new_tokens = tokens.copy()
        for _ in range(n):
            if len(new_tokens) < 2:
                break
            idx1, idx2 = random.sample(range(len(new_tokens)), 2)
            new_tokens[idx1], new_tokens[idx2] = new_tokens[idx2], new_tokens[idx1]
        return new_tokens
    
    @staticmethod
    def random_insertion(tokens, n=1):
        """随机插入：随机插入同义词的随机位置"""
        # 简化实现：随机复制已有token
        for _ in range(n):
            if not tokens:
                break
            idx = random.randint(0, len(tokens) - 1)
            tokens.insert(idx, tokens[idx])
        return tokens
    
    @staticmethod
    def synonym_replacement(tokens, n=1, synonyms_dict=None):
        """同义词替换：用同义词替换token"""
        if synonyms_dict is None:
            return tokens
        new_tokens = tokens.copy()
        replaceable = [i for i, t in enumerate(new_tokens) if t in synonyms_dict]
        if not replaceable:
            return new_tokens
        for idx in random.sample(replaceable, min(n, len(replaceable))):
            syns = synonyms_dict.get(new_tokens[idx], [new_tokens[idx]])
            new_tokens[idx] = random.choice(syns)
        return new_tokens

# 高级数据增强：Mixup和CutMix
class MixupLoss(nn.Module):
    """Mixup数据增强对应的损失函数
    
    Mixup: 将两个样本及其标签按比例混合
    """
    def __init__(self, criterion):
        super().__init__()
        self.criterion = criterion
    
    def forward(self, pred, y_a, y_b, lam):
        return lam * self.criterion(pred, y_a) + (1 - lam) * self.criterion(pred, y_b)

def mixup_data(x, y, alpha=1.0):
    """Mixup数据生成
    
    返回混合后的输入和两组标签及其混合系数
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(x.device)
    
    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    
    return mixed_x, y_a, y_b, lam

def cutmix_data(x, y, alpha=1.0):
    """CutMix数据增强
    
    将一个样本的随机矩形区域替换为另一个样本的区域
    """
    lam = np.random.beta(alpha, alpha)
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(x.device)
    
    # 生成随机矩形
    W, H = x.size(2), x.size(3)
    cut_rat = np.sqrt(1. - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)
    
    cx = np.random.randint(W)
    cy = np.random.randint(H)
    
    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)
    
    x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
    
    # 调整lambda使其与实际区域比例匹配
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
    
    return x, y, y[index], lam
