def serialize(root):
    """前序遍历序列化"""
    if not root:
        return "None,"
    return str(root.val) + "," + serialize(root.left) + serialize(root.right)

def deserialize(data):
    """前序遍历反序列化"""
    def helper(nodes):
        val = nodes.pop(0)
        if val == "None":
            return None
        node = TreeNode(int(val))
        node.left = helper(nodes)
        node.right = helper(nodes)
        return node
    
    nodes = data.split(",")
    return helper(nodes[:-1])
