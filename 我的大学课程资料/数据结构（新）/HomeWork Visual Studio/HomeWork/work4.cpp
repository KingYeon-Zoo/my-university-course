//#include <iostream>
//
//using namespace std;
//
//class Queue {
//private:
//    int* data;
//    int capacity;
//    int front;
//    int rear;
//    int count;
//
//public:
//    Queue(int cap) {
//        capacity = cap > 0 ? cap : 10;
//        data = new int[capacity];
//        front = 0;
//        rear = 0;
//        count = 0;
//    }
//
//    ~Queue() {
//        delete[] data;
//    }
//
//    bool isFull() const {
//        return count == capacity;
//    }
//
//    bool isEmpty() const {
//        return count == 0;
//    }
//
//    void enqueue(int value) {
//        if (isFull()) {
//            cerr << "错误：队列已满，无法入队" << endl;
//            return;
//        }
//        data[rear] = value;
//        rear = (rear + 1) % capacity;
//        count++;
//    }
//
//    int dequeue() {
//        if (isEmpty()) {
//            cerr << "错误：队列为空，无法出队" << endl;
//            return -1;
//        }
//        int value = data[front];
//        front = (front + 1) % capacity;
//        count--;
//        return value;
//    }
//
//    int getFront() const {
//        if (isEmpty()) {
//            cerr << "错误：队列为空，无法获取队头元素" << endl;
//            return -1;
//        }
//        return data[front];
//    }
//
//    int getSize() const {
//        return count;
//    }
//};
//
//void printPascalTriangle(int n) {
//    if (n <= 0) {
//        cout << "行数必须为正整数" << endl;
//        return;
//    }
//
//    Queue queue(n + 1);
//
//    cout << "第1行: 1" << endl;
//    if (n >= 1) {
//        queue.enqueue(1);
//    }
//
//
//    for (int i = 2; i <= n; i++) {
//        cout << "第" << i << "行: ";
//        cout << "1 ";
//        queue.enqueue(1);
//
//        for (int j = 1; j < i - 1; j++) {
//            int val1 = queue.dequeue();
//            int val2 = queue.getFront();
//            int newVal = val1 + val2;
//            cout << newVal << " ";
//            queue.enqueue(newVal);
//        }
//
//        if (i > 1) {
//            cout << "1";
//            queue.dequeue();
//            queue.enqueue(1);
//        }
//        cout << endl;
//    }
//}
//
//int main() {
//    int n;
//    cout << "请输入要打印的杨辉三角的行数: ";
//    cin >> n;
//    printPascalTriangle(n);
//    return 0;
//}