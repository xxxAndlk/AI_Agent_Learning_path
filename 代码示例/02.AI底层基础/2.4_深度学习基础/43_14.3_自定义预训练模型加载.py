def load_custom_pretrained():
    """加载自定义预训练模型"""
    
    # 保存和加载整个模型（不推荐，依赖代码结构）
    # torch.save(model, 'model.pth')
    # model = torch.load('model.pth')
    
    # 推荐：只保存和加载state_dict（参数）
    # torch.save(model.state_dict(), 'model_weights.pth')
    # model = MyModel()
    # model.load_state_dict(torch.load('model_weights.pth'))
    
    # 从URL加载预训练权重
    import urllib.request
    import os
    
    # 例如加载timm库的其他模型
    # import timm
    # model = timm.create_model('vit_base_patch16_224', pretrained=True)
    
    # 多GPU模型转为单GPU
    # model.load_state_dict({k.replace('module.', ''): v 
    #                        for k, v in torch.load('model.pth').items()})
    
    # 单GPU模型转为多GPU
    # model = nn.DataParallel(model)
