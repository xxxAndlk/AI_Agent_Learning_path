from sklearn.tree import export_text, plot_tree
import matplotlib.pyplot as plt

# 训练决策树
tree = DecisionTreeClassifier(max_depth=4)
tree.fit(X_train, y_train)

# 导出文本规则
rules = export_text(tree, feature_names=feature_names)
print(rules)

# 可视化决策树
plt.figure(figsize=(20, 10))
plot_tree(tree, feature_names=feature_names, class_names=class_names, filled=True)
plt.savefig('decision_tree.png')
