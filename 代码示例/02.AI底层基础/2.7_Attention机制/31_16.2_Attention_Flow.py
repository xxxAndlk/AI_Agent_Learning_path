import numpy as np
import matplotlib.pyplot as plt

def compute_attention_flow(attentions):
    """计算Attention Flow
    
    分析从输入到输出的信息流动路径。
    """
    num_layers = len(attentions)
    
    # 聚合所有头
    layer_attentions = [attn.mean(dim=1)[0] for attn in attentions]  # list of (seq, seq)
    
    # 计算每层的信息保留
    # 使用奇异值分解分析注意力矩阵的秩
    flow_info = []
    
    for layer_idx, attn in enumerate(layer_attentions):
        # SVD分析
        U, S, V = torch.svd(attn)
        
        # 信息熵
        probs = S / S.sum()
        entropy = -(probs * torch.log(probs + 1e-10)).sum().item()
        
        # 前k个奇异值的能量占比
        cum_energy = (S ** 2).cumsum(dim=0) / (S ** 2).sum()
        top5_energy = cum_energy[4].item()
        
        flow_info.append({
            'layer': layer_idx,
            'entropy': entropy,
            'top5_energy': top5_energy,
            'rank': (S > 1e-6).sum().item()
        })
    
    return flow_info


def visualize_attention_flow(flow_info):
    """可视化Attention Flow分析结果"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    layers = [f['layer'] for f in flow_info]
    
    # 熵变化
    entropies = [f['entropy'] for f in flow_info]
    axes[0].plot(layers, entropies, 'b-o')
    axes[0].set_xlabel('Layer')
    axes[0].set_ylabel('Entropy')
    axes[0].set_title('Attention Entropy by Layer')
    axes[0].grid(True)
    
    # Top-5能量
    top5_energies = [f['top5_energy'] for f in flow_info]
    axes[1].plot(layers, top5_energies, 'r-o')
    axes[1].set_xlabel('Layer')
    axes[1].set_ylabel('Energy Ratio')
    axes[1].set_title('Top-5 Singular Value Energy')
    axes[1].grid(True)
    
    # 矩阵秩
    ranks = [f['rank'] for f in flow_info]
    axes[2].plot(layers, ranks, 'g-o')
    axes[2].set_xlabel('Layer')
    axes[2].set_ylabel('Matrix Rank')
    axes[2].set_title('Attention Matrix Rank')
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.show()


def analyze_head_specialization(model, tokenizer, text):
    """分析不同注意力头的专长
    
    每个头可能关注不同类型的信息（语法、语义、位置等）。
    """
    # 获取注意力
    inputs = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    
    attentions = outputs.attentions
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    
    num_layers = len(attentions)
    num_heads = attentions[0].shape[1]
    
    print(f"模型: {num_layers}层, {num_heads}头")
    print(f"文本: {text}")
    print(f"Tokens: {tokens}")
    print("=" * 60)
    
    # 分析每个头
    all_head_stats = []
    
    for layer_idx in range(num_layers):
        layer_attn = attentions[layer_idx][0]  # (heads, seq, seq)
        
        layer_stats = []
        
        for head_idx in range(num_heads):
            head_attn = layer_attn[head_idx]
            
            # 计算注意力对角线强度（自身注意力）
            diag_strength = head_attn.diagonal().mean().item()
            
            # 计算注意力分布的集中度
            head_attn_np = head_attn.cpu().numpy()
            concentration = (head_attn_np ** 2).sum()
            
            # 计算位置偏差（是否关注特定位置范围）
            pos_attention = head_attn.sum(dim=0).cpu().numpy()
            center_of_mass = np.sum(np.arange(len(pos_attention)) * pos_attention) / pos_attention.sum()
            
            layer_stats.append({
                'layer': layer_idx,
                'head': head_idx,
                'diag': diag_strength,
                'concentration': concentration,
                'center_of_mass': center_of_mass
            })
        
        all_head_stats.extend(layer_stats)
        
        # 打印该层最特殊的头
        sorted_heads = sorted(layer_stats, key=lambda x: x['concentration'], reverse=True)
        
        print(f"\nLayer {layer_idx}:")
        print(f"  最集中注意力头: Head {sorted_heads[0]['head']} (concentration={sorted_heads[0]['concentration']:.3f})")
        print(f"  自身注意力最高: Head {max(layer_stats, key=lambda x: x['diag'])['head']} (diag={max(l['diag'] for l in layer_stats):.3f})")
    
    return all_head_stats
