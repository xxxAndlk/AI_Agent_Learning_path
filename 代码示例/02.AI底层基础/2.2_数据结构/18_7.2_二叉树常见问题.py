def is_valid_bst(root):
    """利用BST中序遍历有序的特性"""
    def inorder(node, prev):
        if not node:
            return True
        if not inorder(node.left, prev):
            return False
        if prev[0] and node.val <= prev[0].val:
            return False
        prev[0] = node
        return inorder(node.right, prev)
    
    return inorder(root, [None])

# 或者使用范围检查
def is_valid_bst_v2(root, low=float('-inf'), high=float('inf')):
    if not root:
        return True
    if not (low < root.val < high):
        return False
    return (is_valid_bst_v2(root.left, low, root.val) and
            is_valid_bst_v2(root.right, root.val, high))
