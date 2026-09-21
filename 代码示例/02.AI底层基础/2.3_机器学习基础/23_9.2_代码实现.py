import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,           # 混淆矩阵
    accuracy_score,             # 准确率
    precision_score,            # 精确率
    recall_score,               # 召回率
    f1_score,                   # F1分数
    roc_curve,                  # ROC曲线
    roc_auc_score,              # AUC值
    classification_report       # 完整报告
)
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

# 生成不平衡数据集（正负样本比例1:10）
X, y = make_classification(
    n_samples=1000, 
    n_features=20, 
    n_informative=15,
    n_redundant=5,
    weights=[0.9, 0.1],  # 负类90%，正类10%
    random_state=42
)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 训练逻辑回归模型
model = LogisticRegression(class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)              # 类别预测
y_proba = model.predict_proba(X_test)[:, 1] # 正类概率

# 1. 混淆矩阵
cm = confusion_matrix(y_test, y_pred)
print("=== 混淆矩阵 ===")
print(cm)
print(f"\nTN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")

# 2. 基本指标
print("\n=== 基本分类指标 ===")
print(f"准确率 (Accuracy): {accuracy_score(y_test, y_pred):.4f}")
print(f"精确率 (Precision): {precision_score(y_test, y_pred):.4f}")
print(f"召回率 (Recall): {recall_score(y_test, y_pred):.4f}")
print(f"F1分数: {f1_score(y_test, y_pred):.4f}")

# 3. 分类报告（包含宏平均和加权平均）
print("\n=== 完整分类报告 ===")
print(classification_report(y_test, y_pred, target_names=['负类', '正类']))

# 4. ROC曲线和AUC
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
auc_score = roc_auc_score(y_test, y_proba)

print(f"\nAUC: {auc_score:.4f}")

# 可视化ROC曲线
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC曲线 (AUC={auc_score:.3f})')
plt.plot([0, 1], [0, 1], 'r--', linewidth=1, label='随机猜测')
plt.xlabel('假正率 (FPR)', fontsize=12)
plt.ylabel('真正率 (TPR)', fontsize=12)
plt.title('ROC曲线', fontsize=14)
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('roc_curve.png', dpi=150)
plt.show()

# 5. 可视化混淆矩阵
plt.figure(figsize=(8, 6))
plt.imshow(cm, interpolation='nearest', cmap='Blues')
plt.title('混淆矩阵', fontsize=14)
plt.colorbar()

classes = ['负类', '正类']
tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, classes)
plt.yticks(tick_marks, classes)

# 在每个格子中显示数值
thresh = cm.max() / 2
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")

plt.ylabel('实际类别', fontsize=12)
plt.xlabel('预测类别', fontsize=12)
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150)
plt.show()
