def feature_hashing(features, dim=10000):
    """用于高维稀疏特征的哈希"""
    hashed = [0] * dim
    for feature, value in features.items():
        index = hash(feature) % dim
        sign = 1 if hash(feature + "_sign") % 2 == 0 else -1
        hashed[index] += sign * value
    return hashed
