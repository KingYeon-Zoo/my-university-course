//#include <iostream>
//
//using namespace std;
//
//int custom_max(int a, int b) {
//    return (a > b) ? a : b;
//}
//
//struct BinaryTreeNode {
//    int data;
//    BinaryTreeNode *left, *right;
//    BinaryTreeNode(int val) : data(val), left(nullptr), right(nullptr) {}
//    ~BinaryTreeNode() {
//        delete left;
//        delete right;
//    }
//};
//
//struct QueueNode {
//    BinaryTreeNode* treeNode;
//    int level; 
//    QueueNode* next;
//    QueueNode(BinaryTreeNode* tn, int l) : treeNode(tn), level(l), next(nullptr) {}
//};
//
//class CustomQueue {
//public:
//    QueueNode *front, *rear;
//    int currentSize;
//
//    CustomQueue() : front(nullptr), rear(nullptr), currentSize(0) {}
//
//    ~CustomQueue() {
//        while(!isEmpty()) {
//            dequeue();
//        }
//    }
//
//    void enqueue(BinaryTreeNode* tn, int level) {
//        if (tn == nullptr) return;
//        QueueNode* newNode = new QueueNode(tn, level);
//        if (rear == nullptr) {
//            front = rear = newNode;
//        } else {
//            rear->next = newNode;
//            rear = newNode;
//        }
//        currentSize++;
//    }
//    
//    void enqueueNode(BinaryTreeNode* tn) { 
//        enqueue(tn, 0); 
//    }
//
//    QueueNode* dequeue() {
//        if (front == nullptr) {
//            return nullptr;
//        }
//        QueueNode* temp = front;
//        front = front->next;
//        if (front == nullptr) {
//            rear = nullptr;
//        }
//        currentSize--;
//        return temp; 
//    }
//    
//    BinaryTreeNode* dequeueTreeNode(){
//        QueueNode* qn = dequeue();
//        if(qn) {
//            BinaryTreeNode* tn = qn->treeNode;
//            delete qn;
//            return tn;
//        }
//        return nullptr;
//    }
//
//    bool isEmpty() {
//        return front == nullptr;
//    }
//
//    int size() {
//        return currentSize;
//    }
//};
//
//class LinkedBinaryTree {
//public:
//    BinaryTreeNode* root;
//
//    LinkedBinaryTree() : root(nullptr) {}
//    LinkedBinaryTree(BinaryTreeNode* r) : root(r) {}
//    ~LinkedBinaryTree() {
//        delete root;
//    }
//
//    int getHeightRecursive(BinaryTreeNode* node) {
//        if (node == nullptr) {
//            return 0;
//        }
//        int leftHeight = getHeightRecursive(node->left);
//        int rightHeight = getHeightRecursive(node->right);
//        return 1 + custom_max(leftHeight, rightHeight);
//    }
//
//    int getHeightRecursive() {
//        return getHeightRecursive(root);
//    }
//
//    int getHeightLevelOrder() {
//        if (root == nullptr) {
//            return 0;
//        }
//        CustomQueue q;
//        q.enqueue(root, 1); 
//        int maxHeight = 0;
//        while (!q.isEmpty()) {
//            QueueNode* currentQueueNode = q.dequeue();
//            BinaryTreeNode* currentNode = currentQueueNode->treeNode;
//            int currentLevel = currentQueueNode->level;
//            delete currentQueueNode; 
//
//            maxHeight = custom_max(maxHeight, currentLevel);
//
//            if (currentNode->left != nullptr) {
//                q.enqueue(currentNode->left, currentLevel + 1);
//            }
//            if (currentNode->right != nullptr) {
//                q.enqueue(currentNode->right, currentLevel + 1);
//            }
//        }
//        return maxHeight;
//    }
//    
//    BinaryTreeNode* insertLevelOrder(int arr[], BinaryTreeNode* currentRoot, int i, int n) {
//        if (i < n && arr[i] != -1) { 
//            currentRoot = new BinaryTreeNode(arr[i]);
//            currentRoot->left = insertLevelOrder(arr, currentRoot->left, 2 * i + 1, n);
//            currentRoot->right = insertLevelOrder(arr, currentRoot->right, 2 * i + 2, n);
//        }
//        return currentRoot;
//    }
//
//    void buildTreeFromArray(int arr[], int n) {
//        root = insertLevelOrder(arr, root, 0, n);
//    }
//};
//
//const int MAX_SEQ_NODES = 100; 
//class SequentialBinaryTree {
//public:
//    int tree[MAX_SEQ_NODES];
//    int nodeCount; 
//
//    SequentialBinaryTree() : nodeCount(0) {
//        for (int i = 0; i < MAX_SEQ_NODES; ++i) {
//            tree[i] = -1; 
//        }
//    }
//
//    void buildTree(int arr[], int n) {
//        nodeCount = n;
//        for (int i = 0; i < n && i < MAX_SEQ_NODES; ++i) {
//            tree[i] = arr[i];
//        }
//        for (int i = n; i < MAX_SEQ_NODES; ++i) {
//            tree[i] = -1;
//        }
//    }
//
//    int getHeightRecursive(int index) {
//        if (index >= nodeCount || tree[index] == -1) {
//            return 0;
//        }
//        int leftChildIndex = 2 * index + 1;
//        int rightChildIndex = 2 * index + 2;
//        int leftHeight = getHeightRecursive(leftChildIndex);
//        int rightHeight = getHeightRecursive(rightChildIndex);
//        return 1 + custom_max(leftHeight, rightHeight);
//    }
//
//    int getHeightRecursive() {
//        if (nodeCount == 0) return 0;
//        return getHeightRecursive(0); 
//    }
//
//    int getHeightLevelOrder() {
//        if (nodeCount == 0 || tree[0] == -1) {
//            return 0;
//        }
//
//        int* queue_nodes = new int[nodeCount]; 
//        int* queue_levels = new int[nodeCount];
//        int q_front = 0, q_rear = 0;
//        int maxHeight = 0;
//
//        queue_nodes[q_rear] = 0; 
//        queue_levels[q_rear] = 1;
//        q_rear++;
//
//        while (q_front < q_rear) {
//            int currentIndex = queue_nodes[q_front];
//            int currentLevel = queue_levels[q_front];
//            q_front++;
//
//            maxHeight = custom_max(maxHeight, currentLevel);
//
//            int leftChildIndex = 2 * currentIndex + 1;
//            int rightChildIndex = 2 * currentIndex + 2;
//
//            if (leftChildIndex < nodeCount && tree[leftChildIndex] != -1) {
//                queue_nodes[q_rear] = leftChildIndex;
//                queue_levels[q_rear] = currentLevel + 1;
//                q_rear++;
//            }
//            if (rightChildIndex < nodeCount && tree[rightChildIndex] != -1) {
//                queue_nodes[q_rear] = rightChildIndex;
//                queue_levels[q_rear] = currentLevel + 1;
//                q_rear++;
//            }
//        }
//        delete[] queue_nodes;
//        delete[] queue_levels;
//        return maxHeight;
//    }
//};
//
//int main() {
//    cout << "--- 链式二叉树 --- " << endl;
//    BinaryTreeNode* lRoot = new BinaryTreeNode(1);
//    lRoot->left = new BinaryTreeNode(2);
//    lRoot->right = new BinaryTreeNode(3);
//    lRoot->left->left = new BinaryTreeNode(4);
//    lRoot->left->right = new BinaryTreeNode(5);
//    lRoot->right->left = new BinaryTreeNode(6);
//    lRoot->left->left->left = new BinaryTreeNode(7);
//
//    LinkedBinaryTree linkedTree(lRoot);
//    cout << "高度 (递归): " << linkedTree.getHeightRecursive() << endl;
//    cout << "高度 (层次遍历): " << linkedTree.getHeightLevelOrder() << endl;
//    cout << endl;
//    
//    LinkedBinaryTree linkedTree2;
//    int arrForLinked[] = {1, 2, 3, 4, 5, -1, 6, -1, -1, 7};
//    int nForLinked = sizeof(arrForLinked)/sizeof(arrForLinked[0]);
//    linkedTree2.buildTreeFromArray(arrForLinked, nForLinked); 
//    cout << "从数组 {1, 2, 3, 4, 5, -1, 6, -1, -1, 7} 构建的链式树 (-1 为空节点):" << endl;
//    cout << "高度 (递归): " << linkedTree2.getHeightRecursive() << endl;
//    cout << "高度 (层次遍历): " << linkedTree2.getHeightLevelOrder() << endl;
//    cout << endl;
//
//
//    cout << "--- 顺序存储二叉树 --- " << endl;
//    SequentialBinaryTree seqTree;
//    int arr[] = {1, 2, 3, 4, 5, 6, -1, 7, -1, -1, -1, -1, -1, -1, -1}; 
//    int n = 7; 
//    for(int k=0; k<15; ++k) if(arr[k] != -1) n = k + 1; else if (k < n) {} 
//    
//    int actual_n = 0;
//    for(int k=0; k<15; ++k) {
//        if (arr[k] != -1) actual_n = k + 1;
//        else {
//            bool hasChild = false;
//            for(int j=k; j<15; ++j) {
//                 if ( (2*k+1 < 15 && arr[2*k+1] != -1) || (2*k+2 < 15 && arr[2*k+2] != -1) ) {
//                     
//                 }
//                 int parent_idx_l = (j-1)/2;
//                 int parent_idx_r = (j-2)/2;
//                 if (j > 0 && ((j%2 != 0 && arr[parent_idx_l] != -1) || (j%2 == 0 && arr[parent_idx_r] != -1) ) && arr[j] != -1) {
//                     actual_n = j+1;
//                 }
//            }
//        }
//    }
//     
//    int temp_arr_for_seq[] = {1, 2, 3, 4, 5, 6, -1, 7};
//    int count_nodes_for_seq = 0;
//    for(int val : temp_arr_for_seq) {
//        if(val != -1) count_nodes_for_seq++;
//    }
//    int max_idx_for_seq = -1;
//    for(int k=0; k < sizeof(temp_arr_for_seq)/sizeof(temp_arr_for_seq[0]); ++k) {
//        if (temp_arr_for_seq[k] != -1) max_idx_for_seq = k;
//    }
//
//    seqTree.buildTree(temp_arr_for_seq, max_idx_for_seq + 1); 
//    cout << "从数组 {1, 2, 3, 4, 5, 6, -1, 7} 构建的顺序树 (大小基于最后一个非-1元素):" << endl;
//    cout << "高度 (递归): " << seqTree.getHeightRecursive() << endl;
//    cout << "高度 (层次遍历): " << seqTree.getHeightLevelOrder() << endl;
//    cout << endl;
//    
//    SequentialBinaryTree seqTree2;
//    int arr2[] = {1,2,3,-1,-1,4,5,-1,-1,-1,-1,-1,-1,6,7};
//    max_idx_for_seq = -1;
//    for(int k=0; k < sizeof(arr2)/sizeof(arr2[0]); ++k) {
//        if (arr2[k] != -1) max_idx_for_seq = k;
//    }
//    seqTree2.buildTree(arr2, max_idx_for_seq +1);
//    cout << "从数组 {1,2,3,-1,-1,4,5,-1,-1,-1,-1,-1,-1,6,7} 构建的顺序树:" << endl;
//    cout << "高度 (递归): " << seqTree2.getHeightRecursive() << endl;
//    cout << "高度 (层次遍历): " << seqTree2.getHeightLevelOrder() << endl;
//    cout << endl;
//
//    SequentialBinaryTree seqTree3;
//    int arr3[] = {1, -1, 2, -1, -1, -1, 3}; 
//    max_idx_for_seq = -1;
//    for(int k=0; k < sizeof(arr3)/sizeof(arr3[0]); ++k) {
//        if (arr3[k] != -1) max_idx_for_seq = k;
//    }
//    seqTree3.buildTree(arr3, max_idx_for_seq +1);
//    cout << "从数组 {1, -1, 2, -1, -1, -1, 3} 构建的顺序树:" << endl;
//    cout << "高度 (递归): " << seqTree3.getHeightRecursive() << endl;
//    cout << "高度 (层次遍历): " << seqTree3.getHeightLevelOrder() << endl;
//
//    return 0;
//}
