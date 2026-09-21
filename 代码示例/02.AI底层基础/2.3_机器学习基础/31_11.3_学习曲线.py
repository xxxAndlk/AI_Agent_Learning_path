from sklearn.model_selection import learning_curve
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
import numpy as np
import matplotlib.pyplot as plt

# 生成数据
X, y = make_classification(
    n_samples=1000, n_features=20, 
    n_informative=15, n_redundant=5,
    random_state=42
)

def plot_learning_curves(model, X, y, title):
    """绘制学习曲线"""
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, 
        cv=5, 
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='accuracy',
        n_jobs=-1
    )
    
    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)
    
    plt.figure(figsize=(10, 6))
    plt.fill_between(train_sizes, train_mean - train_std, 
                     train_mean + train_std, alpha=0.1, color='blue')
    plt.fill_between(train_sizes, val_mean - val_std, 
                     val_mean + val_std, alpha=0.1, color='orange')
    plt.plot(train_sizes, train_mean, 'b-', label='训练分数')
    plt.plot(train_sizes, val_mean, 'r-', label='验证分数')
    plt.xlabel('训练样本数')
    plt.ylabel('准确率')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0.5, 1.0)
    plt.tight_layout()

# 绘制学习曲线
plot_learning_curves(
    LogisticRegression(max_iter=1000, random_state=42), 
    X, y, 
    '学习曲线'
)
plt.savefig('learning_curve.png', dpi=150)
plt.show()
