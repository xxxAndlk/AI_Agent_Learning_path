def reverse_list(head):
    """迭代法反转链表"""
    prev = None
    current = head
    while current:
        next_temp = current.next  # 保存下一个节点
        current.next = prev       # 反转指针
        prev = current            # 移动prev
        current = next_temp       # 移动current
    return prev

def reverse_list_recursive(head):
    """递归法反转链表"""
    if not head or not head.next:
        return head
    new_head = reverse_list_recursive(head.next)
    head.next.next = head
    head.next = None
    return new_head
