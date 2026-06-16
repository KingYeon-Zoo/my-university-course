//#include <iostream>
//using namespace std;
//
//class ArrayMerger {
//private:
//    int* arr1;
//    int* arr2;
//    int* result;
//    int size1;
//    int size2;
//    int resultSize;
//
//public:
//    ArrayMerger(int* a1, int s1, int* a2, int s2) {
//        arr1 = a1;
//        arr2 = a2;
//        size1 = s1;
//        size2 = s2;
//        resultSize = s1 + s2;
//        result = new int[resultSize];
//    }
//
//    ~ArrayMerger() {
//        delete[] result;
//    }
//
//    void mergeTwoPointers() {
//        int i = 0, j = 0, k = 0;
//        
//        while (i < size1 && j < size2) {
//            if (arr1[i] <= arr2[j]) {
//                result[k++] = arr1[i++];
//            } else {
//                result[k++] = arr2[j++];
//            }
//        }
//        
//        while (i < size1) {
//            result[k++] = arr1[i++];
//        }
//        
//        while (j < size2) {
//            result[k++] = arr2[j++];
//        }
//    }
//
//    void mergeAndSort() {
//        int k = 0;
//        
//        for (int i = 0; i < size1; i++) {
//            result[k++] = arr1[i];
//        }
//        
//        for (int i = 0; i < size2; i++) {
//            result[k++] = arr2[i];
//        }
//        
//        for (int i = 0; i < resultSize - 1; i++) {
//            for (int j = 0; j < resultSize - i - 1; j++) {
//                if (result[j] > result[j + 1]) {
//                    int temp = result[j];
//                    result[j] = result[j + 1];
//                    result[j + 1] = temp;
//                }
//            }
//        }
//    }
//
//    void printResult() {
//        cout << "合并结果: ";
//        for (int i = 0; i < resultSize; i++) {
//            cout << result[i] << " ";
//        }
//        cout << endl;
//    }
//};
//
//struct Node {
//    int data;
//    Node* next;
//    
//    Node(int value) {
//        data = value;
//        next = nullptr;
//    }
//};
//
//class LinkedListMerger {
//private:
//    Node* head1;
//    Node* head2;
//    Node* resultHead;
//    int size1;
//    int size2;
//    bool isResultFromOriginalLists;
//
//public:
//    LinkedListMerger(int* arr1, int s1, int* arr2, int s2) {
//        size1 = s1;
//        size2 = s2;
//        isResultFromOriginalLists = false;
//        
//        if (s1 > 0) {
//            head1 = new Node(arr1[0]);
//            Node* current = head1;
//            for (int i = 1; i < s1; i++) {
//                current->next = new Node(arr1[i]);
//                current = current->next;
//            }
//        } else {
//            head1 = nullptr;
//        }
//        
//        if (s2 > 0) {
//            head2 = new Node(arr2[0]);
//            Node* current = head2;
//            for (int i = 1; i < s2; i++) {
//                current->next = new Node(arr2[i]);
//                current = current->next;
//            }
//        } else {
//            head2 = nullptr;
//        }
//        
//        resultHead = nullptr;
//    }
//    
//    ~LinkedListMerger() {
//        if (head1 != nullptr && !isResultFromOriginalLists) {
//            Node* current = head1;
//            while (current != nullptr) {
//                Node* temp = current;
//                current = current->next;
//                delete temp;
//            }
//        }
//        
//        if (head2 != nullptr && !isResultFromOriginalLists) {
//            Node* current = head2;
//            while (current != nullptr) {
//                Node* temp = current;
//                current = current->next;
//                delete temp;
//            }
//        }
//        
//        if (resultHead != nullptr && !isResultFromOriginalLists) {
//            Node* current = resultHead;
//            while (current != nullptr) {
//                Node* temp = current;
//                current = current->next;
//                delete temp;
//            }
//        }
//    }
//
//    void mergeTwoPointers() {
//        Node* current1 = head1;
//        Node* current2 = head2;
//        
//        if (current1 == nullptr && current2 == nullptr) {
//            resultHead = nullptr;
//            return;
//        }
//        
//        if (current1 == nullptr) {
//            resultHead = current2;
//            isResultFromOriginalLists = true;
//            return;
//        }
//        
//        if (current2 == nullptr) {
//            resultHead = current1;
//            isResultFromOriginalLists = true;
//            return;
//        }
//        
//        if (current1->data <= current2->data) {
//            resultHead = current1;
//            current1 = current1->next;
//        } else {
//            resultHead = current2;
//            current2 = current2->next;
//        }
//        
//        Node* resultCurrent = resultHead;
//        
//        while (current1 != nullptr && current2 != nullptr) {
//            if (current1->data <= current2->data) {
//                resultCurrent->next = current1;
//                current1 = current1->next;
//            } else {
//                resultCurrent->next = current2;
//                current2 = current2->next;
//            }
//            resultCurrent = resultCurrent->next;
//        }
//        
//        if (current1 != nullptr) {
//            resultCurrent->next = current1;
//        }
//        
//        if (current2 != nullptr) {
//            resultCurrent->next = current2;
//        }
//        
//        isResultFromOriginalLists = true;
//    }
//
//    void mergeAndSort() {
//        Node* current = head1;
//        resultHead = nullptr;
//        
//        while (current != nullptr) {
//            Node* newNode = new Node(current->data);
//            newNode->next = resultHead;
//            resultHead = newNode;
//            current = current->next;
//        }
//        
//        current = head2;
//        while (current != nullptr) {
//            Node* newNode = new Node(current->data);
//            newNode->next = resultHead;
//            resultHead = newNode;
//            current = current->next;
//        }
//        
//        bool swapped;
//        Node* ptr1;
//        Node* lptr = nullptr;
//        
//        do {
//            swapped = false;
//            ptr1 = resultHead;
//            
//            while (ptr1->next != lptr) {
//                if (ptr1->data > ptr1->next->data) {
//                    int temp = ptr1->data;
//                    ptr1->data = ptr1->next->data;
//                    ptr1->next->data = temp;
//                    swapped = true;
//                }
//                ptr1 = ptr1->next;
//            }
//            lptr = ptr1;
//        } while (swapped);
//    }
//
//    void printResult() {
//        cout << "合并结果: ";
//        Node* current = resultHead;
//        while (current != nullptr) {
//            cout << current->data << " ";
//            current = current->next;
//        }
//        cout << endl;
//    }
//};
//
//int main() {
//    int arr1[] = {1, 3, 5, 7, 9};
//    int arr2[] = {2, 4, 6, 8, 10};
//    int size1 = 5;
//    int size2 = 5;
//    
//    cout << "原始数组1: ";
//    for (int i = 0; i < size1; i++) {
//        cout << arr1[i] << " ";
//    }
//    cout << endl;
//    
//    cout << "原始数组2: ";
//    for (int i = 0; i < size2; i++) {
//        cout << arr2[i] << " ";
//    }
//    cout << endl << endl;
//    
//    cout << "方法一：使用数组存储" << endl;
//    cout << "处理流程一：双指针法" << endl;
//    ArrayMerger arrayMerger1(arr1, size1, arr2, size2);
//    arrayMerger1.mergeTwoPointers();
//    arrayMerger1.printResult();
//    cout << endl;
//    
//    cout << "处理流程二：先合并后排序" << endl;
//    ArrayMerger arrayMerger2(arr1, size1, arr2, size2);
//    arrayMerger2.mergeAndSort();
//    arrayMerger2.printResult();
//    cout << endl;
//    
//    cout << "方法二：使用链表存储" << endl;
//    cout << "处理流程一：双指针法" << endl;
//    LinkedListMerger listMerger1(arr1, size1, arr2, size2);
//    listMerger1.mergeTwoPointers();
//    listMerger1.printResult();
//    cout << endl;
//    
//    cout << "处理流程二：先合并后排序" << endl;
//    LinkedListMerger listMerger2(arr1, size1, arr2, size2);
//    listMerger2.mergeAndSort();
//    listMerger2.printResult();
//    
//    return 0;
//}
