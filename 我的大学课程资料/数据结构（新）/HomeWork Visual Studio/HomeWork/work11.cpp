//#include <iostream>
//
//using namespace std;
//
//int custom_max(int a, int b) {
//    return (a > b) ? a : b;
//}
//
//struct TreeNode {
//    int data;
//    TreeNode* firstChild;
//    TreeNode* nextSibling;
//
//    TreeNode(int val) : data(val), firstChild(nullptr), nextSibling(nullptr) {}
//
//    ~TreeNode() {
//        delete firstChild;
//        delete nextSibling;
//    }
//};
//
//struct QueueNode {
//    TreeNode* treeNode;
//    QueueNode* next;
//    QueueNode(TreeNode* tn) : treeNode(tn), next(nullptr) {}
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
//    void enqueue(TreeNode* tn) {
//        if (tn == nullptr) return;
//        QueueNode* newNode = new QueueNode(tn);
//        if (rear == nullptr) {
//            front = rear = newNode;
//        } else {
//            rear->next = newNode;
//            rear = newNode;
//        }
//        currentSize++;
//    }
//
//    TreeNode* dequeue() {
//        if (front == nullptr) {
//            return nullptr;
//        }
//        QueueNode* temp = front;
//        TreeNode* tn = temp->treeNode;
//        front = front->next;
//        if (front == nullptr) {
//            rear = nullptr;
//        }
//        delete temp;
//        currentSize--;
//        return tn;
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
//class Tree {
//public:
//    TreeNode* root;
//
//    Tree() : root(nullptr) {}
//    Tree(TreeNode* r) : root(r) {}
//
//    int getHeightRecursive(TreeNode* node) {
//        if (!node) {
//            return 0;
//        }
//        int maxChildBranchHeight = 0;
//        TreeNode* child = node->firstChild;
//        while (child) {
//            maxChildBranchHeight = custom_max(maxChildBranchHeight, getHeightRecursive(child));
//            child = child->nextSibling;
//        }
//        return 1 + maxChildBranchHeight;
//    }
//
//    int getTreeHeightRecursive() {
//        return getHeightRecursive(root);
//    }
//
//    int getTreeHeightLevelOrder() {
//        if (!root) {
//            return 0;
//        }
//
//        CustomQueue q;
//        q.enqueue(root);
//        int height = 0;
//
//        while (!q.isEmpty()) {
//            int nodesAtCurrentLevel = q.size();
//            if (nodesAtCurrentLevel == 0) break;
//
//            height++;
//
//            for (int i = 0; i < nodesAtCurrentLevel; ++i) {
//                TreeNode* current = q.dequeue();
//                if (!current) continue;
//
//                TreeNode* child = current->firstChild;
//                while (child) {
//                    q.enqueue(child);
//                    child = child->nextSibling;
//                }
//            }
//        }
//        return height;
//    }
//};
//
//class Forest {
//public:
//    static int getForestHeightRecursive(TreeNode* forestRoots[], int numTrees) {
//        if (numTrees <= 0) {
//            return 0;
//        }
//        int maxHeight = 0;
//        Tree tempTree;
//        for (int i = 0; i < numTrees; ++i) {
//            tempTree.root = forestRoots[i];
//            maxHeight = custom_max(maxHeight, tempTree.getTreeHeightRecursive());
//        }
//        tempTree.root = nullptr;
//        return maxHeight;
//    }
//
//    static int getForestHeightLevelOrder(TreeNode* forestRoots[], int numTrees) {
//        if (numTrees <= 0) {
//            return 0;
//        }
//        int maxHeight = 0;
//        Tree tempTree;
//        for (int i = 0; i < numTrees; ++i) {
//            tempTree.root = forestRoots[i];
//            maxHeight = custom_max(maxHeight, tempTree.getTreeHeightLevelOrder());
//        }
//        tempTree.root = nullptr;
//        return maxHeight;
//    }
//};
//
//int main() {
//    TreeNode* t1Root = new TreeNode(1);
//    t1Root->firstChild = new TreeNode(2);
//    t1Root->firstChild->nextSibling = new TreeNode(3);
//    t1Root->firstChild->firstChild = new TreeNode(4);
//    t1Root->firstChild->firstChild->nextSibling = new TreeNode(5);
//    t1Root->firstChild->nextSibling->firstChild = new TreeNode(6);
//
//    Tree tree1(t1Root);
//    cout << "树 1 (孩子兄弟表示法) 高度 (递归): " << tree1.getTreeHeightRecursive() << endl;
//    cout << "树 1 (孩子兄弟表示法) 高度 (层次遍历): " << tree1.getTreeHeightLevelOrder() << endl;
//
//
//    TreeNode* t2Root = new TreeNode(10);
//    t2Root->firstChild = new TreeNode(11);
//    t2Root->firstChild->firstChild = new TreeNode(12);
//    t2Root->firstChild->firstChild->firstChild = new TreeNode(13);
//
//    Tree tree2(t2Root);
//    cout << "树 2 (孩子兄弟表示法) 高度 (递归): " << tree2.getTreeHeightRecursive() << endl;
//    cout << "树 2 (孩子兄弟表示法) 高度 (层次遍历): " << tree2.getTreeHeightLevelOrder() << endl;
//
//    TreeNode* forestRoots[] = {t1Root, t2Root};
//    cout << "森林 (由树1和树2组成) 高度 (递归): " << Forest::getForestHeightRecursive(forestRoots, 2) << endl;
//    cout << "森林 (由树1和树2组成) 高度 (层次遍历): " << Forest::getForestHeightLevelOrder(forestRoots, 2) << endl;
//    
//    delete t1Root;
//    delete t2Root;
//
//    return 0;
//}
