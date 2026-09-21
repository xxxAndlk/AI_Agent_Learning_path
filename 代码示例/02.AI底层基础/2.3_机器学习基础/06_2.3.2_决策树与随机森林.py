from sklearn.tree import DecisionTreeClassifier      # 决策树分类器
from sklearn.ensemble import RandomForestClassifier  # 随机森林分类器
from sklearn.datasets import load_iris               # 鸢尾花数据集
from sklearn.model_selection import train_test_split # 数据集划分
from sklearn.metrics import accuracy_score           # 准确率评估

# 加载鸢尾花数据集（经典的3分类问题，150个样本，4个特征）
iris = load_iris()
X, y = iris.data, iris.target  # X: 特征矩阵(150,4), y: 标签向量(150,)
# 划分训练集和测试集（80%训练，20%测试）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

def decision_tree_demo():
    """决策树示例：基于信息增益递归划分数据"""
    # 创建决策树模型，max_depth=3限制树深度防止过拟合
    dt_model = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt_model.fit(X_train, y_train)    # 训练模型
    y_pred = dt_model.predict(X_test) # 预测测试集
    print("=== 决策树结果 ===")
    print("准确率:", accuracy_score(y_test, y_pred))

def random_forest_demo():
    """随机森林示例：集成多个决策树投票决策
    
    通过Bagging（自助采样聚合）和随机特征选择降低方差
    """
    # n_estimators=100: 构建100棵决策树
    # max_depth=3: 每棵树的最大深度
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)
    rf_model.fit(X_train, y_train)    # 训练模型
    y_pred = rf_model.predict(X_test) # 预测测试集
    print("\n=== 随机森林结果 ===")
    print("准确率:", accuracy_score(y_test, y_pred))
    # feature_importances_显示每个特征的重要性（基于不纯度减少）
    print("特征重要性:", rf_model.feature_importances_)

if __name__ == "__main__":
    decision_tree_demo()              # 运行决策树示例
    random_forest_demo()              # 运行随机森林示例
