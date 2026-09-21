from sklearn.feature_extraction.text import TfidfVectorizer  # TF-IDF向量化
from sklearn.feature_selection import SelectKBest, chi2      # 特征选择
from sklearn.feature_selection import mutual_info_classif   # 互信息
import pandas as pd
import numpy as np
from typing import List

class FeatureEngineer:
    """特征工程工具类"""
    
    @staticmethod
    def extract_text_features(
        texts: List[str],
        method: str = "tfidf",
        max_features: int = 1000,
        ngram_range: tuple = (1, 2)
    ):
        """提取文本特征
        
        参数:
            texts: 文本列表
            method: 特征提取方法 (tfidf/count)
            max_features: 最大特征数
            ngram_range: N-gram范围
        返回:
            特征矩阵和向量化器
        """
        if method == "tfidf":
            # TF-IDF向量化
            # TF（词频）: 词在文档中出现频率
            # IDF（逆文档频率）: log(总文档数/包含该词的文档数)
            # TF-IDF = TF * IDF，衡量词的重要性
            vectorizer = TfidfVectorizer(
                max_features=max_features,      # 最大特征数
                ngram_range=ngram_range,        # N-gram范围，如(1,2)表示unigram和bigram
                stop_words='english',           # 停用词
                min_df=2,                       # 最小文档频率
                max_df=0.8                      # 最大文档频率（过滤高频词）
            )
        else:
            from sklearn.feature_extraction.text import CountVectorizer
            vectorizer = CountVectorizer(
                max_features=max_features,
                ngram_range=ngram_range,
                stop_words='english'
            )
        
        # 拟合并转换文本
        features = vectorizer.fit_transform(texts)
        
        print(f"文本特征形状: {features.shape}")
        print(f"特征示例: {vectorizer.get_feature_names_out()[:10]}")
        
        return features, vectorizer
    
    @staticmethod
    def select_features(
        X,
        y,
        method: str = "chi2",
        k: int = 100
    ):
        """选择最佳特征
        
        参数:
            X: 特征矩阵
            y: 标签
            method: 选择方法 (chi2/mutual_info/f_classif)
            k: 选择前k个特征
        返回:
            选择后的特征和选择器
        """
        if method == "chi2":
            # 卡方检验：衡量特征与标签的独立性
            # 卡方值越大，说明特征与标签越相关
            selector = SelectKBest(chi2, k=k)
        elif method == "mutual_info":
            # 互信息：衡量特征与标签的互信息
            selector = SelectKBest(mutual_info_classif, k=k)
        elif method == "f_classif":
            from sklearn.feature_selection import f_classif
            # ANOVA F-value
            selector = SelectKBest(f_classif, k=k)
        
        X_selected = selector.fit_transform(X, y)
        
        # 打印选中的特征
        if hasattr(selector, 'get_support'):
            selected_mask = selector.get_support()
            print(f"从 {X.shape[1]} 个特征中选择 {selected_mask.sum()} 个")
        
        return X_selected, selector
    
    @staticmethod
    def calculate_feature_importance(model, feature_names=None):
        """计算特征重要性
        
        参数:
            model: 训练好的模型（需要有feature_importances_或coef_属性）
            feature_names: 特征名称列表
        返回:
            特征重要性字典
        """
        importance = {}
        
        if hasattr(model, 'feature_importances_'):
            # 树模型（如RandomForest、XGBoost）
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # 线性模型（如LogisticRegression）
            importances = np.abs(model.coef_[0]) if model.coef_.ndim > 1 else np.abs(model.coef_)
        else:
            print("模型不支持特征重要性计算")
            return importance
        
        # 创建特征重要性字典
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        importance = dict(zip(feature_names, importances))
        
        # 按重要性排序
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return importance

if __name__ == "__main__":
    # 示例1: 文本特征提取
    texts = [
        "机器学习是人工智能的一个分支",
        "深度学习使用神经网络进行学习",
        "自然语言处理是AI的重要应用",
        "计算机视觉让机器能看懂图像",
        "强化学习通过试错来学习策略"
    ]
    
    # 注意：这里使用英文示例，中文需要额外分词处理
    english_texts = [
        "Machine learning is a branch of AI",
        "Deep learning uses neural networks",
        "Natural language processing is important",
        "Computer vision helps machines see",
        "Reinforcement learning learns from trial"
    ]
    
    engineer = FeatureEngineer()
    
    # 提取TF-IDF特征
    features, vectorizer = engineer.extract_text_features(
        english_texts,
        method="tfidf",
        max_features=20,
        ngram_range=(1, 2)
    )
    
    print("\nTF-IDF特征矩阵:")
    print(features.toarray())
