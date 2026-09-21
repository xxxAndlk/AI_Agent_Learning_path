import pandas as pd
import matplotlib.pyplot as plt

# 训练随机森林
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)

# 获取特征重要性
importance = pd.DataFrame({
    'feature': feature_names,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

# 可视化
plt.figure(figsize=(10, 6))
plt.barh(importance['feature'], importance['importance'])
plt.xlabel('Feature Importance')
plt.title('Random Forest Feature Importance')
plt.tight_layout()
plt.savefig('feature_importance.png')

# 选择重要特征
selected_features = importance[importance['importance'] > 0.05]['feature'].tolist()
