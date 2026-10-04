from sklearn.linear_model import LogisticRegression

# L2正则化（默认）
lr_l2 = LogisticRegression(penalty='l2', C=1.0, random_state=42)

# L1正则化
lr_l1 = LogisticRegression(penalty='l1', solver='saga', C=1.0, random_state=42)

# Elastic Net
lr_elastic = LogisticRegression(
    penalty='elasticnet', 
    solver='saga',
    l1_ratio=0.5,
    C=1.0, 
    random_state=42
)
