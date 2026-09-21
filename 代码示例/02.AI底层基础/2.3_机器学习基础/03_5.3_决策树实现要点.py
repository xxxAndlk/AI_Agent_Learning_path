import numpy as np
# 简化版决策树
class DecisionTreeManual:
    def __init__(self, max_depth=3, min_samples=2):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.tree = None
    
    def _entropy(self, y):
        """计算熵"""
        classes, counts = np.unique(y, return_counts=True)
        probabilities = counts / len(y)
        return -np.sum(p * np.log2(p) for p in probabilities if p > 0)
    
    def _information_gain(self, y, left_y, right_y):
        """计算信息增益"""
        n = len(y)
        n_left, n_right = len(left_y), len(right_y)
        if n_left == 0 or n_right == 0:
            return 0
        return self._entropy(y) - (n_left/n) * self._entropy(left_y) - (n_right/n) * self._entropy(right_y)
    
    def _best_split(self, X, y):
        """找最佳分裂点"""
        best_gain = -1
        best_split = None
        
        for feature_idx in range(X.shape[1]):
            thresholds = np.unique(X[:, feature_idx])
            for threshold in thresholds:
                left_mask = X[:, feature_idx] <= threshold
                gain = self._information_gain(y, y[left_mask], y[~left_mask])
                if gain > best_gain:
                    best_gain = gain
                    best_split = (feature_idx, threshold)
        
        return best_split
