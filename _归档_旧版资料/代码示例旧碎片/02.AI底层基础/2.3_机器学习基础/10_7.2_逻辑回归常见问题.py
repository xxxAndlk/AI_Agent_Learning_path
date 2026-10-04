# 问题：正负样本比例悬殊，模型偏向多数类

# 解决方案1：类别权重
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(class_weight='balanced')

# 解决方案2：过采样
from imblearn.over_sampling import SMOTE
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X, y)

# 解决方案3：调整阈值
y_proba = model.predict_proba(X_test)[:, 1]
threshold = 0.3  # 降低阈值提高召回率
y_pred = (y_proba >= threshold).astype(int)
