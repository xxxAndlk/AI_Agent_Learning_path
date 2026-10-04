import numpy as np

class AttentionAnalyzer:
    """综合注意力分析工具
    
    集成了Rollout、Flow、Head specialization等分析功能。
    """
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device
    
    def analyze(self, text_or_input_ids, return_visualizations=True):
        """综合分析
        
        Args:
            text_or_input_ids: 文本或token ids
            return_visualizations: 是否返回可视化结果
        
        Returns:
            分析结果字典
        """
        # 处理输入
        if isinstance(text_or_input_ids, str):
            inputs = self.tokenizer(text_or_input_ids, return_tensors='pt')
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        else:
            inputs = {'input_ids': text_or_input_ids.to(self.device)}
        
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        # 获取注意力
        with torch.no_grad():
            outputs = self.model(**inputs, output_attentions=True)
        
        attentions = [attn.cpu() for attn in outputs.attentions]
        
        results = {
            'tokens': tokens,
            'num_layers': len(attentions),
            'num_heads': attentions[0].shape[1],
            'attentions': attentions
        }
        
        # 1. Attention Rollout
        results['rollout'] = compute_attention_rollup(attentions)
        
        # 2. Attention Flow
        results['flow_info'] = compute_attention_flow(attentions)
        
        # 3. 聚合分析
        cls_analysis = analyze_cls_aggregation(results['rollout'], tokens)
        results['cls_analysis'] = cls_analysis
        
        # 4. 可视化
        if return_visualizations:
            # 热力图
            visualize_attention_heatmap(attentions[-1].mean(dim=1)[0], tokens)
            
            # 多头模式
            visualize_multi_head_attention(attentions[-1], tokens)
            
            # 注意力流
            visualize_attention_flow(attentions)
            
            # Rollout
            visualize_attention_rollup(attentions, tokens)
            
            # Flow分析
            visualize_attention_flow(results['flow_info'])
        
        return results
    
    def compare_attention_patterns(self, texts):
        """比较多个文本的注意力模式
        
        找出不同文本间的共同模式和差异。
        """
        all_results = []
        
        for text in texts:
            inputs = self.tokenizer(text, return_tensors='pt')
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs, output_attentions=True)
            
            # 最后一层平均注意力
            avg_attn = outputs.attentions[-1].mean(dim=1)[0]
            all_results.append({
                'text': text,
                'attn': avg_attn
            })
        
        # 比较分析
        print("注意力模式比较:")
        print("=" * 50)
        
        for i, result in enumerate(all_results):
            print(f"\n文本 {i+1}: {result['text'][:50]}...")
            attn = result['attn']
            
            # 集中度
            concentration = (attn ** 2).sum(dim=-1).mean().item()
            print(f"  注意力集中度: {concentration:.4f}")
            
            # 位置偏差
            seq_len = attn.shape[0]
            pos_weights = attn.sum(dim=0).cpu().numpy()
            positions = np.arange(seq_len)
            center = np.sum(positions * pos_weights) / pos_weights.sum()
            print(f"  注意力中心位置: {center:.1f} / {seq_len}")
        
        return all_results


# 使用示例
def demo_attention_analyzer():
    """演示注意力分析工具的使用"""
    
    # 加载模型（需要transformers库）
    from transformers import AutoModel, AutoTokenizer
    
    # 使用BERT作为示例
    model_name = 'bert-base-chinese'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    
    # 创建分析器
    analyzer = AttentionAnalyzer(model, tokenizer)
    
    # 分析单个文本
    text = "今天天气很好，我们去公园散步吧。"
    results = analyzer.analyze(text)
    
    # 比较多个文本
    texts = [
        "今天天气很好，我们去公园散步吧。",
        "这个产品非常好用，推荐购买。",
        "电影很精彩，但是票价太贵了。"
    ]
    analyzer.compare_attention_patterns(texts)
    
    return results
