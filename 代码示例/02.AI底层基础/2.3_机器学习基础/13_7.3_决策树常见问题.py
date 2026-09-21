# 问题：决策树容易过拟合，尤其是深层树

# 解决方案：剪枝
# 预剪枝：限制树的生长
tree = DecisionTreeClassifier(
    max_depth=5,           # 最大深度
    min_samples_split=10,  # 分裂所需最小样本数
    min_samples_leaf=5,    # 叶节点最小样本数
    max_leaf_nodes=20      # 最大叶节点数
)

# 后剪枝：先生长再修剪（sklearn不直接支持）
# 可以使用cost-complexity pruning
tree = DecisionTreeClassifier(ccp_alpha=0.01)
