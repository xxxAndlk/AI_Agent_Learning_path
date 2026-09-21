class TreeNode:
    """二叉树节点类"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val                # 节点的值
        self.left = left              # 左子树（左孩子节点）
        self.right = right            # 右子树（右孩子节点）

class BinaryTreeTraversal:
    """二叉树遍历类：实现四种遍历方式"""
    
    def preorder(self, root: TreeNode) -> list:
        """前序遍历：根 -> 左 -> 右"""
        res = []                      # 存储遍历结果的列表
        def dfs(node):
            """深度优先搜索递归函数"""
            if node:                  # 如果节点不为空
                res.append(node.val)  # 先访问根节点
                dfs(node.left)        # 递归遍历左子树
                dfs(node.right)       # 递归遍历右子树
        dfs(root)                     # 从根节点开始遍历
        return res                    # 返回遍历结果
    
    def inorder(self, root: TreeNode) -> list:
        """中序遍历：左 -> 根 -> 右（BST中会得到有序序列）"""
        res = []
        def dfs(node):
            if node:
                dfs(node.left)        # 先递归遍历左子树
                res.append(node.val)  # 然后访问根节点
                dfs(node.right)       # 最后递归遍历右子树
        dfs(root)
        return res
    
    def postorder(self, root: TreeNode) -> list:
        """后序遍历：左 -> 右 -> 根"""
        res = []
        def dfs(node):
            if node:
                dfs(node.left)        # 先递归遍历左子树
                dfs(node.right)       # 然后递归遍历右子树
                res.append(node.val)  # 最后访问根节点
        dfs(root)
        return res
    
    def levelorder(self, root: TreeNode) -> list:
        """层序遍历：按层级从上到下、从左到右遍历"""
        if not root:                  # 如果根节点为空
            return []                 # 返回空列表
        res, queue = [], [root]       # res存储结果，queue存储待遍历的节点
        while queue:                  # 当队列不为空时继续
            level_size = len(queue)   # 当前层的节点数量
            current_level = []        # 存储当前层的节点值
            for _ in range(level_size):  # 遍历当前层的所有节点
                node = queue.pop(0)   # 从队列头部取出节点
                current_level.append(node.val)  # 记录节点值
                if node.left:         # 如果有左孩子
                    queue.append(node.left)   # 加入队列
                if node.right:        # 如果有右孩子
                    queue.append(node.right)  # 加入队列
            res.append(current_level) # 将当前层结果加入最终结果
        return res                    # 返回按层级分组的结果

if __name__ == "__main__":
    # 构建二叉树
    #       1
    #      / \
    #     2   3
    #    / \
    #   4   5
    root = TreeNode(1)                # 创建根节点
    root.left = TreeNode(2)           # 根节点的左孩子
    root.right = TreeNode(3)          # 根节点的右孩子
    root.left.left = TreeNode(4)      # 节点2的左孩子
    root.left.right = TreeNode(5)     # 节点2的右孩子
    
    traversal = BinaryTreeTraversal() # 创建遍历器实例
    print("前序遍历:", traversal.preorder(root))    # [1, 2, 4, 5, 3]
    print("中序遍历:", traversal.inorder(root))     # [4, 2, 5, 1, 3]
    print("后序遍历:", traversal.postorder(root))   # [4, 5, 2, 3, 1]
    print("层序遍历:", traversal.levelorder(root))  # [[1], [2, 3], [4, 5]]
