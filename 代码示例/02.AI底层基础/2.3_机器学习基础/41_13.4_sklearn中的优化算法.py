from sklearn.linear_model import SGDRegressor, LogisticRegression

# SGD回归器
sgd_reg = SGDRegressor(
    loss='squared_error',
    penalty='l2',
    alpha=0.0001,
    learning_rate='optimal',
    eta0=0.01,
    max_iter=1000,
    random_state=42
)

# 不同优化器的逻辑回归
lr_sgd = LogisticRegression(solver='sgd', learning_rate='adaptive', eta0=0.1, max_iter=1000, random_state=42)
lr_lbfgs = LogisticRegression(solver='lbfgs', max_iter=1000, random_state=42)
lr_saga = LogisticRegression(solver='saga', penalty='elasticnet', l1_ratio=0.5, max_iter=1000, random_state=42)
