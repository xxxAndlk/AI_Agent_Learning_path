from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report

# 训练模型
model = LogisticRegression(class_weight='balanced')
model.fit(X_train, y_train)

# 获取概率预测
y_proba = model.predict_proba(X_test)[:, 1]

# 评估
print("AUC:", roc_auc_score(y_test, y_proba))

# 查看特征权重（可解释性）
for feature, coef in zip(feature_names, model.coef_[0]):
    print(f"{feature}: {coef:.4f}")
