//#include <iostream>
//#include <stdexcept>
//
//using namespace std;
//
//struct FibFrame {
//    int n;
//    int return_address_label;
//    int stage;
//    int temp_result;
//    int final_result;
//};
//
//template <typename T>
//struct StackNode {
//    T data;
//    StackNode* next;
//
//    StackNode(T val) : data(val), next(NULL) {}
//};
//
//template <typename T>
//class Stack {
//private:
//    StackNode<T>* top_ptr;
//    int count;
//
//public:
//    Stack() : top_ptr(NULL), count(0) {}
//
//    ~Stack() {
//        while (!empty()) {
//            pop();
//        }
//    }
//
//    void push(T val) {
//        StackNode<T>* newNode = new StackNode<T>(val);
//        newNode->next = top_ptr;
//        top_ptr = newNode;
//        count++;
//    }
//
//    void pop() {
//        if (empty()) {
//            cerr << "Error: Stack underflow! Cannot pop from an empty stack." << endl;
//            return;
//        }
//        StackNode<T>* temp = top_ptr;
//        top_ptr = top_ptr->next;
//        delete temp;
//        count--;
//    }
//
//    T& top() {
//        if (empty()) {
//            static T dummy;
//            cerr << "Error: Cannot access top of an empty stack. Returning dummy value." << endl;
//            return dummy;
//        }
//        return top_ptr->data;
//    }
//
//    const T& top() const {
//        if (empty()) {
//            static T dummy;
//            cerr << "Error: Cannot access top of an empty stack. Returning dummy value." << endl;
//            return dummy;
//        }
//        return top_ptr->data;
//    }
//
//    bool empty() const {
//        return top_ptr == NULL;
//    }
//
//    int size() const {
//        return count;
//    }
//};
//
//int fib_recursive(int n) {
//    if (n <= 0) {
//        return 0;
//    }
//    else if (n == 1) {
//        return 1;
//    }
//    else {
//        int fib_n_minus_1 = fib_recursive(n - 1);
//        int fib_n_minus_2 = fib_recursive(n - 2);
//        return fib_n_minus_1 + fib_n_minus_2;
//    }
//}
//
//int fib_nonrecursive_unsimplified(int initial_n) {
//    if (initial_n <= 0) return 0;
//    if (initial_n == 1) return 1;
//
//    Stack<FibFrame> S;
//    int current_n = initial_n;
//    int current_result = 0;
//    int goto_label = 0;
//
//GOTO_DISPATCHER:
//    if (goto_label == 0) goto L0;
//    if (goto_label == 1) goto L1;
//    if (goto_label == 2) goto L2;
//    if (goto_label == 3) goto L_RETURN;
//    cerr << "Error: Invalid goto label " << goto_label << endl;
//    return -1;
//
//L0:
//    if (current_n <= 0) {
//        current_result = 0;
//        goto_label = 3;
//        goto GOTO_DISPATCHER;
//    }
//    else if (current_n == 1) {
//        current_result = 1;
//        goto_label = 3;
//        goto GOTO_DISPATCHER;
//    }
//    else {
//        FibFrame frame;
//        frame.n = current_n;
//        frame.return_address_label = 1;
//        frame.stage = 1;
//        frame.temp_result = 0;
//        S.push(frame);
//
//        current_n = current_n - 1;
//        goto_label = 0;
//        goto GOTO_DISPATCHER;
//    }
//
//L1:
//    {
//        if (S.empty()) {
//            cerr << "Error: Stack empty at L1!" << endl;
//            return -1;
//        }
//        FibFrame& current_frame = S.top();
//        current_frame.temp_result = current_result;
//        current_frame.stage = 2;
//        current_frame.return_address_label = 2;
//
//        current_n = current_frame.n - 2;
//        goto_label = 0;
//        goto GOTO_DISPATCHER;
//    }
//
//L2:
//    {
//        if (S.empty()) {
//            cerr << "Error: Stack empty at L2!" << endl;
//            return -1;
//        }
//        FibFrame& current_frame = S.top();
//        current_frame.final_result = current_frame.temp_result + current_result;
//        current_result = current_frame.final_result;
//        goto_label = 3;
//        goto GOTO_DISPATCHER;
//    }
//
//L_RETURN:
//    if (S.empty()) {
//        return current_result;
//    }
//    else {
//        FibFrame caller_frame = S.top();
//        S.pop();
//
//        current_n = caller_frame.n;
//        goto_label = caller_frame.return_address_label;
//        goto GOTO_DISPATCHER;
//    }
//}
//
//int fib_nonrecursive_simplified(int n) {
//    if (n <= 0) {
//        return 0;
//    }
//    if (n == 1) {
//        return 1;
//    }
//
//    int a = 0;
//    int b = 1;
//    int result = 0;
//
//    for (int i = 2; i <= n; ++i) {
//        result = a + b;
//        a = b;
//        b = result;
//    }
//
//    return b;
//}
//
//int main() {
//    int n_test = 8;
//
//    cout << "测试斐波那契数列计算 (n = " << n_test << ")" << endl;
//
//    cout << "递归法结果: F(" << n_test << ") = " << fib_recursive(n_test) << endl;
//
//    cout << "模拟递归非递归法结果: F(" << n_test << ") = " << fib_nonrecursive_unsimplified(n_test) << endl;
//
//    cout << "迭代法结果: F(" << n_test << ") = " << fib_nonrecursive_simplified(n_test) << endl;
//
//    cout << "测试不同 n 值:" << endl;
//    for (int i = 0; i <= 10; ++i) {
//        cout << "F(" << i << "): ";
//        cout << "递归=" << fib_recursive(i) << ", ";
//        cout << "模拟=" << fib_nonrecursive_unsimplified(i) << ", ";
//        cout << "迭代=" << fib_nonrecursive_simplified(i) << endl;
//    }
//
//    return 0;
//}