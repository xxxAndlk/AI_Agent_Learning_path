from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

# 定义参数分布（而非固定值）
param_dist = {
    'svm__C': uniform(0.01, 100),      # 均匀分布 [0.01, 100.01]
    'svm__kernel': ['linear', 'rbf', 'poly'],
    'svm__gamma': uniform(0.01, 10),   # 均匀分布
    'svm__degree': randint(2, 6)       # 整数随机
}

# 随机搜索（采样30个参数组合）
random_search = RandomizedSearchCV(
    pipeline,
    param_dist,
    n_iter=30,        # 采样数量
    cv=5,
    scoring='accuracy',
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)
print(f"最优参数: {random_search.best_params_}")
