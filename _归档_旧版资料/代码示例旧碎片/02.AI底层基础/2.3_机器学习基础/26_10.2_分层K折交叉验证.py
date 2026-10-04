from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

# 生成分类不平衡数据
X, y = make_classification(
    n_samples=1000, 
    weights=[0.8, 0.2],  # 80%负类，20%正类
    random_state=42
)

# 普通K折（可能每折类别比例不一致）
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

# 分层K折（每折类别比例与原始一致）
stratified_kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

model = LogisticRegression(random_state=42)

# 对比两种方法
print("=== 普通K折 ===")
scores_normal = cross_val_score(model, X, y, cv=kfold)
print(f"准确率: {scores_normal.mean():.4f} (+/- {scores_normal.std()*2:.4f})")

print("\n=== 分层K折 ===")
scores_stratified = cross_val_score(model, X, y, cv=stratified_kfold)
print(f"准确率: {scores_stratified.mean():.4f} (+/- {scores_stratified.std()*2:.4f})")

# 查看每折中正类比例
print("\n每折正类样本数量:")
for fold_idx, (train_idx, val_idx) in enumerate(stratified_kfold.split(X, y)):
    fold_pos_ratio = y[val_idx].sum() / len(val_idx)
    print(f"Fold {fold_idx+1}: 正类比例 = {fold_pos_ratio:.2%}")
