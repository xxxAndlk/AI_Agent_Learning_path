from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

class EmbeddingFineTuner:
    """Embedding模型微调器"""
    
    def __init__(
        self,
        base_model: str = 'bert-base-chinese',
        max_seq_length: int = 256
    ):
        """
        初始化微调器
        
        参数:
            base_model: 基础模型
            max_seq_length: 最大序列长度
        """
        self.model = SentenceTransformer(base_model)
        self.model.max_seq_length = max_seq_length
        self.train_examples = []
    
    def add_training_data(
        self,
        sentence_pairs: List[tuple],
        labels: List[int]
    ):
        """
        添加训练数据
        
        参数:
            sentence_pairs: 句子对列表
            labels: 标签（1表示相似，0表示不相似）
        """
        for (sent1, sent2), label in zip(sentence_pairs, labels):
            example = InputExample(
                texts=[sent1, sent2],
                label=float(label)
            )
            self.train_examples.append(example)
    
    def add_triplet_data(
        self,
        anchor: str,
        positive: str,
        negative: str
    ):
        """
        添加三元组数据（用于对比学习）
        
        参数:
            anchor: 锚点文本
            positive: 正样本
            negative: 负样本
        """
        example = InputExample(
            texts=[anchor, positive, negative]
        )
        self.train_examples.append(example)
    
    def fine_tune(
        self,
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        loss_type: str = 'contrastive'
    ):
        """
        微调模型
        
        参数:
            num_epochs: 训练轮数
            batch_size: 批量大小
            learning_rate: 学习率
            loss_type: 损失函数类型
        """
        # 创建数据加载器
        train_dataloader = DataLoader(
            self.train_examples,
            batch_size=batch_size,
            shuffle=True
        )
        
        # 选择损失函数
        if loss_type == 'contrastive':
            # 对比损失
            train_loss = losses.ContrastiveLoss(self.model)
        elif loss_type == 'cosine':
            # 余弦相似度损失
            train_loss = losses.CosineSimilarityLoss(self.model)
        else:
            # 多重正样本损失
            train_loss = losses.MultipleNegativesRankingLoss(self.model)
        
        # 微调
        self.model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=num_epochs,
            show_progress_bar=True
        )
    
    def save_model(self, path: str):
        """保存模型"""
        self.model.save(path)
    
    def load_model(self, path: str):
        """加载模型"""
        self.model = SentenceTransformer(path)
