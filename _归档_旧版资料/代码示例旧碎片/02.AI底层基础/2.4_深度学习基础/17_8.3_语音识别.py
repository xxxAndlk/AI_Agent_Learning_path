# 简单语音识别模型
class SpeechRecognizer(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(input_dim, hidden_dim, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim)
        )
        self.rnn = nn.LSTM(hidden_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
    
    def forward(self, x):
        # x: (batch, mel_bins, time)
        x = self.conv(x)  # (batch, hidden, time)
        x = x.transpose(1, 2)  # (batch, time, hidden)
        x, _ = self.rnn(x)  # (batch, time, hidden*2)
        return self.fc(x)  # (batch, time, num_classes)
