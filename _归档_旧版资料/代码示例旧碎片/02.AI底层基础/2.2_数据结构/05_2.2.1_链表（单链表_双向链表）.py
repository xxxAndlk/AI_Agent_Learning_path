class ListNode:
    """链表节点类：存储数据和指向下一个节点的指针"""
    def __init__(self, val=0, next=None):
        self.val = val                # 节点存储的数据值
        self.next = next              # 指向下一个节点的指针（None表示链表末尾）

class SingleLinkedList:
    """单链表类：支持增删改查操作"""
    def __init__(self):
        """初始化空链表"""
        self.head = None              # 头节点指针，初始为None表示空链表
    
    def append(self, val):
        """在链表尾部添加新节点"""
        new_node = ListNode(val)      # 创建新节点
        if not self.head:             # 如果链表为空
            self.head = new_node      # 新节点成为头节点
            return                    # 结束函数
        current = self.head           # 从头节点开始遍历
        while current.next:           # 找到最后一个节点（next为None的节点）
            current = current.next    # 移动到下一个节点
        current.next = new_node       # 最后一个节点指向新节点
    
    def prepend(self, val):
        """在链表头部添加新节点"""
        new_node = ListNode(val)      # 创建新节点
        new_node.next = self.head     # 新节点指向当前的头节点
        self.head = new_node          # 新节点成为新的头节点
    
    def delete(self, val):
        """删除第一个值为val的节点"""
        if not self.head:             # 空链表直接返回
            return
        if self.head.val == val:      # 如果要删除的是头节点
            self.head = self.head.next  # 头节点指向下一个节点
            return
        current = self.head           # 从头节点开始遍历
        while current.next:           # 遍历链表
            if current.next.val == val:  # 找到要删除的节点
                current.next = current.next.next  # 跳过要删除的节点
                return                # 删除后退出
            current = current.next    # 移动到下一个节点
    
    def print_list(self):
        """打印链表所有节点的值"""
        current = self.head           # 从头节点开始
        res = []                      # 存储节点值的列表
        while current:                # 遍历到链表末尾
            res.append(str(current.val))  # 添加节点值（转为字符串）
            current = current.next    # 移动到下一个节点
        print(" -> ".join(res) + " -> None")  # 用箭头连接，最后指向None

if __name__ == "__main__":
    ll = SingleLinkedList()           # 创建链表实例
    ll.append(1)                      # 添加节点1
    ll.append(2)                      # 添加节点2
    ll.append(3)                      # 添加节点3
    ll.prepend(0)                     # 在头部添加节点0
    ll.print_list()                   # 输出: 0 -> 1 -> 2 -> 3 -> None
    ll.delete(2)                      # 删除值为2的节点
    ll.print_list()                   # 输出: 0 -> 1 -> 3 -> None
