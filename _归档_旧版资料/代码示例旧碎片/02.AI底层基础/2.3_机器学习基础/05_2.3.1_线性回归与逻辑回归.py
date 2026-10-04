import numpy as np                   # 导入NumPy用于数值计算
from sklearn.linear_model import LinearRegression, LogisticRegression  # 导入模型
from sklearn.model_selection import train_test_split  # 数据集划分工具
from sklearn.metrics import mean_squared_error, accuracy_score  # 评估指标

def linear_regression_demo():
    """线性回归示例：预测连续值
    
    线性回归假设目标值与特征呈线性关系：y = w*x + b
    """
    np.random.seed(42)                # 设置随机种子，确保结果可复现
    # 生成100个样本，每个样本1个特征，值范围[0, 10)
    X = np.random.rand(100, 1) * 10
    # 生成目标值：y = 2*x + 1 + 噪声（模拟真实数据的不确定性）
    # np.random.randn(100, 1) * 2 添加均值为0、标准差为2的高斯噪声
    y = 2 * X + 1 + np.random.randn(100, 1) * 2
    
    # 划分训练集和测试集（80%训练，20%测试，random_state保证可复现）
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()        # 创建线性回归模型实例
    model.fit(X_train, y_train)       # 在训练集上拟合模型（学习参数w和b）
    y_pred = model.predict(X_test)    # 在测试集上进行预测
    
    print("=== 线性回归结果 ===")
    print("系数:", model.coef_[0][0])  # 斜率w，接近真实值2
    print("截距:", model.intercept_[0])  # 截距b，接近真实值1
    print("均方误差:", mean_squared_error(y_test, y_pred))  # 预测误差

def logistic_regression_demo():
    """逻辑回归示例：二分类问题
    
    逻辑回归使用sigmoid函数将线性输出映射到[0,1]，表示概率
    """
    np.random.seed(42)
    # 生成200个样本，每个样本2个特征，服从标准正态分布
    X = np.random.randn(200, 2)
    # 创建标签：当x1 + x2 > 0时为1（正类），否则为0（负类）
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression()      # 创建逻辑回归模型
    model.fit(X_train, y_train)       # 训练模型
    y_pred = model.predict(X_test)    # 预测测试集标签
    
    print("\n=== 逻辑回归结果 ===")
    print("准确率:", accuracy_score(y_test, y_pred))  # 预测正确率
    print("系数:", model.coef_)       # 每个特征的权重（决策边界参数）
    print("截距:", model.intercept_)  # 偏置项

if __name__ == "__main__":
    linear_regression_demo()          # 运行线性回归示例
    logistic_regression_demo()        # 运行逻辑回归示例
