from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_iris

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建管道：标准化 + SVM
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(random_state=42))
])

# 定义参数网格
param_grid = {
    'svm__C': [0.1, 1, 10],           # 正则化参数
    'svm__kernel': ['linear', 'rbf'],  # 核函数
    'svm__gamma': ['scale', 'auto']    # RBF核参数
}

# 网格搜索（5折分层交叉验证）
grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,  # 并行计算
    verbose=1
)

grid_search.fit(X_train, y_train)

print("\n=== 网格搜索结果 ===")
print(f"最优参数: {grid_search.best_params_}")
print(f"最优交叉验证分数: {grid_search.best_score_:.4f}")

# 在测试集上评估
best_model = grid_search.best_estimator_
test_score = best_model.score(X_test, y_test)
print(f"测试集准确率: {test_score:.4f}")
