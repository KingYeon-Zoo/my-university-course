//#include <iostream>
//using namespace std;
//
//struct QueueNode {
//    int data;
//    QueueNode* next;
//
//    QueueNode(int value) : data(value), next(nullptr) {}
//};
//
//class Queue {
//private:
//    QueueNode* front;
//    QueueNode* rear;
//    int size;
//
//public:
//    Queue() : front(nullptr), rear(nullptr), size(0) {}
//
//    ~Queue() {
//        while (!isEmpty()) {
//            dequeue();
//        }
//    }
//
//    void enqueue(int value) {
//        QueueNode* newNode = new QueueNode(value);
//
//        if (isEmpty()) {
//            front = rear = newNode;
//        }
//        else {
//            rear->next = newNode;
//            rear = newNode;
//        }
//        size++;
//    }
//
//    int dequeue() {
//        if (isEmpty()) {
//            cerr << "错误：队列为空，无法出队" << endl;
//            return -1;
//        }
//
//        QueueNode* temp = front;
//        int value = front->data;
//        front = front->next;
//
//        if (front == nullptr) {
//            rear = nullptr;
//        }
//
//        delete temp;
//        size--;
//        return value;
//    }
//
//    int getFront() const {
//        if (isEmpty()) {
//            cerr << "错误：队列为空，无法获取队头元素" << endl;
//            return -1;
//        }
//        return front->data;
//    }
//
//    bool isEmpty() const {
//        return front == nullptr;
//    }
//
//    int getSize() const {
//        return size;
//    }
//};
//
//void printPascalTriangle(int n) {
//    if (n <= 0) {
//        cout << "输入行数为负数！" << endl;
//        return;
//    }
//
//    Queue queue;
//    cout << "第1行: 1" << endl;
//    queue.enqueue(1);
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
//
//    while (!queue.isEmpty()) {
//        queue.dequeue();
//    }
//}
//
//int main() {
//    int n;
//    cout << "请输入要打印杨辉三角的行数: ";
//    cin >> n;
//    printPascalTriangle(n);
//    return 0;
//}
