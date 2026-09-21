# 虚拟头节点技巧：简化边界条件处理
class LinkedList:
    def __init__(self):
        self.dummy = ListNode(0)  # 虚拟头节点
        self.tail = self.dummy    # 尾指针优化追加操作
    
    def append(self, val):
        new_node = ListNode(val)
        self.tail.next = new_node
        self.tail = new_node
    
    def delete(self, val):
        prev = self.dummy
        while prev.next:
            if prev.next.val == val:
                prev.next = prev.next.next
                return True
            prev = prev.next
        return False

# 快慢指针技巧：找中点、检测环
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow  # slow指向中点

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
