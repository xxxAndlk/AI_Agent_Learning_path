def euclidean_distance(vec1, vec2):
    """距离越小越相似"""
    return torch.norm(vec1 - vec2)
