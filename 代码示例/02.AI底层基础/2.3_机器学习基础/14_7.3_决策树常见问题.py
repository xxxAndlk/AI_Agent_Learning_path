# 问题：信息增益偏向取值多的特征

# 解决方案1：使用信息增益率 (C4.5)
# sklearn的DecisionTreeClassifier默认使用Gini

# 解决方案2：使用Gini系数 (CART，sklearn默认)
tree = DecisionTreeClassifier(criterion='gini')  # 或 'entropy'
