# 随机森林关键实现
from sklearn.tree import DecisionTreeClassifier
import numpy as np

class RandomForestManual:
    def __init__(self, n_trees=100, max_depth=None, min_samples=2, max_features='sqrt'):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.max_features = max_features
        self.trees = []
    
    def _bootstrap_sample(self, X, y):
        """有放回采样"""
        n_samples = X.shape[0]
        indices = np.random.choice(n_samples, n_samples, replace=True)
        return X[indices], y[indices]
    
    def _get_max_features(self, n_features):
        """确定每个节点考虑的特征数"""
        if self.max_features == 'sqrt':
            return int(np.sqrt(n_features))
        elif self.max_features == 'log2':
            return int(np.log2(n_features))
        return n_features
    
    def fit(self, X, y):
        self.trees = []
        for _ in range(self.n_trees):
            # Bootstrap采样
            X_sample, y_sample = self._bootstrap_sample(X, y)
            
            # 创建决策树
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples,
                max_features=self._get_max_features(X.shape[1])
            )
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)
    
    def predict(self, X):
        # 收集所有树的预测
        predictions = np.array([tree.predict(X) for tree in self.trees])
        # 多数投票
        return np.apply_along_axis(lambda x: np.bincount(x).argmax(), axis=0, arr=predictions)
