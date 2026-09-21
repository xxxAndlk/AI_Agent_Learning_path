import pandas as pd
# 问题：特征之间高度相关，导致参数不稳定
# 检测方法：VIF (方差膨胀因子)

from statsmodels.stats.outliers_influence import variance_inflation_factor

def check_vif(X):
    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) 
                       for i in range(X.shape[1])]
    return vif_data

# VIF > 10 表示存在严重共线性
# 解决方案：删除相关特征、PCA降维、正则化
