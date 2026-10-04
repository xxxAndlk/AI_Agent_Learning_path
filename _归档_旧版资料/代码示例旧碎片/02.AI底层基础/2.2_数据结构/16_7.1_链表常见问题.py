def has_cycle(head):
    """快慢指针法"""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

def detect_cycle_start(head):
    """找到环的起始节点"""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            # 快慢指针相遇后，一个从头开始
            slow = head
            while slow != fast:
                slow = slow.next
                fast = fast.next
            return slow
    return None
