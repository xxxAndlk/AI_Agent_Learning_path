# LayerNorm vs BatchNorm
def layernorm_vs_batchnorm():
    """对比LayerNorm和BatchNorm"""
    
    batch_size, seq_len, hidden_dim = 8, 20, 128
    
    # 输入: (batch, seq_len, hidden_dim)
    x = torch.randn(batch_size, seq_len, hidden_dim)
    
    # BatchNorm1d: 在特征维度上归一化
    # 对于序列数据，对每个时间步在batch维度归一化
    bn = nn.BatchNorm1d(hidden_dim)
    bn_out = bn(x.view(-1, hidden_dim)).view(batch_size, seq_len, hidden_dim)
    print(f"BatchNorm1d输出形状: {bn_out.shape}")
    
    # LayerNorm: 在特征维度上归一化
    # 对每个样本，在hidden_dim维度归一化
    ln = nn.LayerNorm(hidden_dim)
    ln_out = ln(x)
    print(f"LayerNorm输出形状: {ln_out.shape}")
    
    # LayerNorm对每个token独立归一化，适合变长序列
    # Transformer和RNN中常用

# Instance Norm: 对每个样本、每个通道独立归一化
# 风格迁移中常用
instance_norm = nn.InstanceNorm2d(num_features=32)

# Group Norm: 将通道分组后在组内归一化
# 当batch较小时比BatchNorm效果好
group_norm = nn.GroupNorm(num_groups=8, num_channels=32)  # 32/8=4个通道一组
