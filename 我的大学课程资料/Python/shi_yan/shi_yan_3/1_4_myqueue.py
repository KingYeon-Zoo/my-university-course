class MyQueue:
    def __init__(self, size):
        self.size = size  
        self.data = [None] * size 
        self.current = 0  
        self.front = 0 
        self.rear = 0 
    
    def is_empty(self):
        return self.current == 0
    
    def is_full(self):
        return self.current == self.size
    
    def get_front(self):
        if self.is_empty():
            raise ValueError("队列为空，无法获取队头元素")
        return self.data[self.front]
    
    def enqueue(self, item):
        if self.is_full():
            raise ValueError("队列已满，无法入队")    
        self.data[self.rear] = item
        self.rear = (self.rear + 1) % self.size
        self.current += 1
    
    def dequeue(self):
        if self.is_empty():
            raise ValueError("队列为空，无法出队")  
        item = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.size
        self.current -= 1
        return item


queue = MyQueue(5)

print("测试入队操作：")
for i in range(5):
    queue.enqueue(i)
    print(f"入队元素：{i}，当前队列：{queue.data}")

try:
    queue.enqueue(5)
except ValueError as e:
    print(f"\n入队失败：{e}")

print("\n测试出队操作：")
while not queue.is_empty():
    front = queue.get_front()
    item = queue.dequeue()
    print(f"队头元素：{front}，出队元素：{item}，当前队列：{queue.data}")

try:
    queue.dequeue()
except ValueError as e:
    print(f"\n出队失败：{e}")
