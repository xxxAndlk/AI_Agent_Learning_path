// Go使用container/list实现双端队列
import "container/list"
dq := list.New()
dq.PushBack(1)      // append
dq.PushFront(0)    // appendleft
dq.Remove(dq.Back())   // pop
dq.Remove(dq.Front())  // popleft
