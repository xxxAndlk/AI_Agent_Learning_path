class TextClassificationLSTM(nn.Module):
    """基于LSTM的文本分类模型
    
    完整流程:
    1. 词嵌入 -> 2. BiLSTM编码 -> 3. 注意力/池化 -> 4. 分类
    """
    def __init__(self, vocab_size, embed_dim, hidden_size, num_classes, 
                 num_layers=2, dropout=0.3):
        super().__init__()
        
        # 1. 词嵌入层
        self.embedding = nn.Embedding(
            num_embeddings=vocab_size, 
            embedding_dim=embed_dim,
            padding_idx=0  # 填充词的索引，不参与训练
        )
        
        # 2. 双向LSTM编码器
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        
        # 3. 全连接分类器
        # 输入是双向LSTM的输出，所以维度翻倍
        self.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, num_classes)
        )
    
    def forward(self, x):
        """
        参数:
            x: (batch_size, seq_len) - 文本的token索引
        """
        # 词嵌入: (batch, seq_len) -> (batch, seq_len, embed_dim)
        embedded = self.embedding(x)
        
        # LSTM: (batch, seq_len, embed_dim) -> (batch, seq_len, hidden*2)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # 方法1: 使用最后一个时间步的隐藏状态
        # 双向LSTM有两个方向，需要拼接
        # hidden shape: (num_layers*2, batch, hidden)
        # 取最后一层的两个方向的隐藏状态
        hidden_forward = hidden[-2]    # 最后一层前向
        hidden_backward = hidden[-1]   # 最后一层后向
        combined_hidden = torch.cat([hidden_forward, hidden_backward], dim=1)
        
        # 分类
        output = self.fc(combined_hidden)
        return output


class TextClassificationWithAttention(nn.Module):
    """带注意力机制的文本分类模型"""
    def __init__(self, vocab_size, embed_dim, hidden_size, num_classes):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # 双向LSTM
        self.lstm = nn.LSTM(
            embed_dim, hidden_size,
            batch_first=True, bidirectional=True
        )
        
        # 注意力机制
        self.attention = nn.Linear(hidden_size * 2, 1)
        
        # 分类器
        self.classifier = nn.Linear(hidden_size * 2, num_classes)
    
    def forward(self, x):
        # 嵌入
        embedded = self.embedding(x)  # (batch, seq, embed)
        
        # LSTM
        lstm_out, _ = self.lstm(embedded)  # (batch, seq, hidden*2)
        
        # 注意力权重
        attention_scores = self.attention(lstm_out)  # (batch, seq, 1)
        attention_weights = F.softmax(attention_scores, dim=1)  # (batch, seq, 1)
        
        # 加权求和
        context = torch.sum(attention_weights * lstm_out, dim=1)  # (batch, hidden*2)
        
        # 分类
        output = self.classifier(context)
        return output


def train_text_classifier():
    """文本分类训练示例"""
    
    # 超参数
    VOCAB_SIZE = 10000
    EMBED_DIM = 128
    HIDDEN_SIZE = 256
    NUM_CLASSES = 2
    SEQ_LEN = 100
    BATCH_SIZE = 32
    
    # 创建模型
    model = TextClassificationLSTM(
        vocab_size=VOCAB_SIZE,
        embed_dim=EMBED_DIM,
        hidden_size=HIDDEN_SIZE,
        num_classes=NUM_CLASSES,
        num_layers=2
    )
    
    # 模拟数据
    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    y = torch.randint(0, NUM_CLASSES, (BATCH_SIZE,))
    
    # 前向传播
    output = model(x)
    print(f"输出形状: {output.shape}")  # (32, 2)
    
    # 损失计算
    criterion = nn.CrossEntropyLoss()
    loss = criterion(output, y)
    print(f"损失: {loss.item():.4f}")
