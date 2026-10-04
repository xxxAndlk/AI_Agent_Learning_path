class DecisionNode:
    def __init__(self, feature, threshold, left, right, value=None):
        self.feature = feature    # 分裂特征
        self.threshold = threshold  # 分裂阈值
        self.left = left          # 左子树
        self.right = right        # 右子树
        self.value = value        # 叶节点的预测值

def predict(node, x):
    """决策树预测"""
    if node.value is not None:
        return node.value
    if x[node.feature] <= node.threshold:
        return predict(node.left, x)
    else:
        return predict(node.right, x)
