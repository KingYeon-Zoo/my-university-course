//#include <iostream>
//
//using namespace std;
//
//struct ThreadNode {
//    int data;
//    ThreadNode *left, *right;
//    bool ltag, rtag;
//
//    ThreadNode(int val) : data(val), left(nullptr), right(nullptr), ltag(false), rtag(false) {}
//};
//
//class PostOrderThreadedBinaryTree {
//private:
//    ThreadNode* root;
//    ThreadNode* pre;
//    ThreadNode* nodeArray[100];
//    int nodeCount;
//
//    void destroyTree(ThreadNode* node) {
//        if (node == nullptr) return;
//        
//        if (!node->ltag) {
//            destroyTree(node->left);
//        }
//        
//        if (!node->rtag) {
//            destroyTree(node->right);
//        }
//        
//        delete node;
//    }
//
//    void collectNodesPostOrder(ThreadNode* node) {
//        if (node == nullptr) return;
//        
//        collectNodesPostOrder(node->left);
//        collectNodesPostOrder(node->right);
//        nodeArray[nodeCount++] = node;
//    }
//
//    void createThreads() {
//        for (int i = 0; i < nodeCount; i++) {
//            ThreadNode* current = nodeArray[i];
//            
//            if (current->left == nullptr && i > 0) {
//                current->ltag = true;
//                current->left = nodeArray[i - 1];
//            }
//            
//            if (current->right == nullptr && i < nodeCount - 1) {
//                current->rtag = true;
//                current->right = nodeArray[i + 1];
//            }
//        }
//    }
//
//    ThreadNode* getFirstNodePostOrder(ThreadNode* node) {
//        if (node == nullptr) return nullptr;
//        
//        while (node != nullptr) {
//            if (!node->ltag && node->left != nullptr) {
//                node = node->left;
//            }
//            else if (!node->rtag && node->right != nullptr) {
//                node = node->right;
//            }
//            else {
//                break;
//            }
//        }
//        return node;
//    }
//
//    ThreadNode* insert(ThreadNode* node, int data) {
//        if (node == nullptr) {
//            return new ThreadNode(data);
//        }
//        
//        if (data < node->data) {
//            node->left = insert(node->left, data);
//        } else if (data > node->data) {
//            node->right = insert(node->right, data);
//        }
//        
//        return node;
//    }
//
//public:
//    PostOrderThreadedBinaryTree() : root(nullptr), pre(nullptr), nodeCount(0) {}
//
//    ~PostOrderThreadedBinaryTree() {
//        destroyTree(root);
//    }
//
//    void convertToPostOrderThreaded() {
//        if (root == nullptr) return;
//        
//        nodeCount = 0;  
//        
//        collectNodesPostOrder(root);
//        
//        createThreads();
//    }
//
//    void postOrderTraversalNonRecursive() {
//        if (root == nullptr) {
//            return;
//        }
//        
//        for (int i = 0; i < nodeCount; i++) {
//            cout << nodeArray[i]->data;
//            if (i < nodeCount - 1) cout << " ";
//        }
//        cout << endl;
//    }
//
//    void createTree() {
//        root = insert(root, 4);
//        insert(root, 2);
//        insert(root, 6);
//        insert(root, 1);
//        insert(root, 3);
//        insert(root, 5);
//        insert(root, 7);
//    }
//
//    void displayTreeInfo() {
//        if (root == nullptr) {
//            return;
//        }
//    }
//};
//
//int main() {
//    PostOrderThreadedBinaryTree tree;
//    
//    tree.createTree();
//    tree.convertToPostOrderThreaded();
//    tree.postOrderTraversalNonRecursive();
//    
//    return 0;
//}
