def lowest_common_ancestor(root, p, q):
    """二叉树的最近公共祖先"""
    if not root or root == p or root == q:
        return root
    
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    if left and right:
        return root  # p和q分别在左右子树
    return left or right  # 都在一侧
