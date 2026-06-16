// #include <iostream>

// using namespace std;

// int custom_max(int a, int b) {
//    return (a > b) ? a : b;
// }

// struct QueueNode {
//    void* data;
//    QueueNode* next;
//    QueueNode(void* d) : data(d), next(nullptr) {}
// };

// class CustomQueue {
// public:
//    QueueNode *front, *rear;
//    int currentSize;

//    CustomQueue() : front(nullptr), rear(nullptr), currentSize(0) {}

//    ~CustomQueue() {
//        while(!isEmpty()) {
//            dequeue();
//        }
//    }

//    void enqueue(void* data) {
//        if (data == nullptr) return;
//        QueueNode* newNode = new QueueNode(data);
//        if (rear == nullptr) {
//            front = rear = newNode;
//        } else {
//            rear->next = newNode;
//            rear = newNode;
//        }
//        currentSize++;
//    }

//    void* dequeue() {
//        if (front == nullptr) {
//            return nullptr;
//        }
//        QueueNode* temp = front;
//        void* data = temp->data;
//        front = front->next;
//        if (front == nullptr) {
//            rear = nullptr;
//        }
//        delete temp;
//        currentSize--;
//        return data;
//    }

//    bool isEmpty() {
//        return front == nullptr;
//    }

//    int size() {
//        return currentSize;
//    }
// };

// namespace CompositionApproach {
//    class NodeData {
//    private:
//        int data;
//    public:
//        NodeData(int val) : data(val) {}
//        ~NodeData() {}
//        int getValue() const { return data; }
//        void setValue(int val) { data = val; }
//    };

//    class TreeStructure {
//    private:
//        NodeData* nodeData;
//        TreeStructure* firstChild;
//        TreeStructure* nextSibling;
//        TreeStructure* left;
//        TreeStructure* right;
//        bool ltag, rtag;
//    public:
//        TreeStructure(int data) : nodeData(new NodeData(data)), firstChild(nullptr), 
//                                  nextSibling(nullptr), left(nullptr), right(nullptr), 
//                                  ltag(false), rtag(false) {}
       
//        ~TreeStructure() {
//            delete nodeData;
//        }
       
//        int getData() const { return nodeData->getValue(); }
//        void setData(int val) { nodeData->setValue(val); }
       
//        TreeStructure* getFirstChild() const { return firstChild; }
//        TreeStructure* getNextSibling() const { return nextSibling; }
//        TreeStructure* getLeft() const { return left; }
//        TreeStructure* getRight() const { return right; }
       
//        void setFirstChild(TreeStructure* child) { firstChild = child; }
//        void setNextSibling(TreeStructure* sibling) { nextSibling = sibling; }
//        void setLeft(TreeStructure* leftNode) { left = leftNode; }
//        void setRight(TreeStructure* rightNode) { right = rightNode; }
       
//        bool getLeftTag() const { return ltag; }
//        bool getRightTag() const { return rtag; }
//        void setLeftTag(bool tag) { ltag = tag; }
//        void setRightTag(bool tag) { rtag = tag; }
//    };

//    class TraversalStrategy {
//    public:
//        virtual ~TraversalStrategy() {}
//        virtual int calculateHeight(TreeStructure* root) = 0;
//    };

//    class RecursiveTraversal : public TraversalStrategy {
//    public:
//        int calculateHeight(TreeStructure* root) override {
//            if (!root) return 0;
//            int maxChildHeight = 0;
//            TreeStructure* child = root->getFirstChild();
//            while (child) {
//                maxChildHeight = custom_max(maxChildHeight, calculateHeight(child));
//                child = child->getNextSibling();
//            }
//            return 1 + maxChildHeight;
//        }
//    };

//    class LevelOrderTraversal : public TraversalStrategy {
//    public:
//        int calculateHeight(TreeStructure* root) override {
//            if (!root) return 0;
//            CustomQueue q;
//            q.enqueue(root);
//            int height = 0;
//            while (!q.isEmpty()) {
//                int nodesAtCurrentLevel = q.size();
//                if (nodesAtCurrentLevel == 0) break;
//                height++;
//                for (int i = 0; i < nodesAtCurrentLevel; ++i) {
//                    TreeStructure* current = (TreeStructure*)q.dequeue();
//                    if (!current) continue;
//                    TreeStructure* child = current->getFirstChild();
//                    while (child) {
//                        q.enqueue(child);
//                        child = child->getNextSibling();
//                    }
//                }
//            }
//            return height;
//        }
//    };

//    class TreeOperations {
//    private:
//        TraversalStrategy* strategy;
//    public:
//        TreeOperations(TraversalStrategy* s) : strategy(s) {}
//        ~TreeOperations() {}
//        int getHeight(TreeStructure* root) {
//            return strategy ? strategy->calculateHeight(root) : 0;
//        }
//        void setStrategy(TraversalStrategy* newStrategy) {
//            strategy = newStrategy;
//        }
//    };

//    class MemoryManager {
//    public:
//        TreeStructure* createNode(int data) {
//            return new TreeStructure(data);
//        }
//        void deallocateTree(TreeStructure* root) {
//            if (!root) return;
//            deallocateTree(root->getFirstChild());
//            deallocateTree(root->getNextSibling());
//            delete root;
//        }
//    };

//    class TreeManager {
//    private:
//        TreeOperations* operations;
//        MemoryManager* memManager;
//        TreeStructure* root;
//    public:
//        TreeManager() : operations(nullptr), memManager(new MemoryManager()), root(nullptr) {}
//        ~TreeManager() {
//            if (root) memManager->deallocateTree(root);
//            delete memManager;
//            delete operations;
//        }
       
//        void createSampleGeneralTree() {
//            root = memManager->createNode(1);
//            root->setFirstChild(memManager->createNode(2));
//            root->getFirstChild()->setNextSibling(memManager->createNode(3));
//            root->getFirstChild()->setFirstChild(memManager->createNode(4));
//        }
       
//        void createSampleBinaryTree() {
//            root = memManager->createNode(1);
//            root->setLeft(memManager->createNode(2));
//            root->setRight(memManager->createNode(3));
//            root->getLeft()->setLeft(memManager->createNode(4));
//        }
       
//        int getTreeHeight() {
//            return operations ? operations->getHeight(root) : 0;
//        }
       
//        void setTraversalStrategy(TraversalStrategy* strategy) {
//            delete operations;
//            operations = new TreeOperations(strategy);
//        }
//    };
// }

// namespace InheritanceApproach {
//    class AbstractTreeNode {
//    protected:
//        int data;
//    public:
//        AbstractTreeNode(int val) : data(val) {}
//        virtual ~AbstractTreeNode() {}
//        virtual AbstractTreeNode* getFirstChild() = 0;
//        virtual AbstractTreeNode* getNextSibling() = 0;
//        virtual void setFirstChild(AbstractTreeNode* child) = 0;
//        virtual void setNextSibling(AbstractTreeNode* sibling) = 0;
//        int getData() { return data; }
//    };

//    class GeneralTreeNode : public AbstractTreeNode {
//        GeneralTreeNode* firstChild;
//        GeneralTreeNode* nextSibling;
//    public:
//        GeneralTreeNode(int val) : AbstractTreeNode(val), firstChild(nullptr), nextSibling(nullptr) {}
//        ~GeneralTreeNode() {
//            delete firstChild;
//            delete nextSibling;
//        }
//        AbstractTreeNode* getFirstChild() override { return firstChild; }
//        AbstractTreeNode* getNextSibling() override { return nextSibling; }
//        void setFirstChild(AbstractTreeNode* child) override { 
//            firstChild = dynamic_cast<GeneralTreeNode*>(child); 
//        }
//        void setNextSibling(AbstractTreeNode* sibling) override { 
//            nextSibling = dynamic_cast<GeneralTreeNode*>(sibling); 
//        }
//    };

//    class BinaryTreeNode : public AbstractTreeNode {
//    protected:
//        BinaryTreeNode* left;
//        BinaryTreeNode* right;
//    public:
//        BinaryTreeNode(int val) : AbstractTreeNode(val), left(nullptr), right(nullptr) {}
//        ~BinaryTreeNode() {
//            delete left;
//            delete right;
//        }
//        AbstractTreeNode* getFirstChild() override { return left; }
//        AbstractTreeNode* getNextSibling() override { return right; }
//        void setFirstChild(AbstractTreeNode* child) override { 
//            left = dynamic_cast<BinaryTreeNode*>(child); 
//        }
//        void setNextSibling(AbstractTreeNode* sibling) override { 
//            right = dynamic_cast<BinaryTreeNode*>(sibling); 
//        }
//        BinaryTreeNode* getLeft() { return left; }
//        BinaryTreeNode* getRight() { return right; }
//        void setLeft(BinaryTreeNode* leftNode) { left = leftNode; }
//        void setRight(BinaryTreeNode* rightNode) { right = rightNode; }
//    };

//    class ThreadedBinaryTreeNode : public BinaryTreeNode {
//        bool ltag, rtag;
//    public:
//        ThreadedBinaryTreeNode(int val) : BinaryTreeNode(val), ltag(false), rtag(false) {}
//        bool getLeftTag() { return ltag; }
//        bool getRightTag() { return rtag; }
//        void setLeftTag(bool tag) { ltag = tag; }
//        void setRightTag(bool tag) { rtag = tag; }
//    };

//    class AbstractTree {
//    protected:
//        AbstractTreeNode* root;
//        virtual int calculateHeightRecursive(AbstractTreeNode* node) {
//            if (!node) return 0;
//            int maxChildHeight = 0;
//            AbstractTreeNode* child = node->getFirstChild();
//            while (child) {
//                maxChildHeight = custom_max(maxChildHeight, calculateHeightRecursive(child));
//                child = child->getNextSibling();
//            }
//            return 1 + maxChildHeight;
//        }
//        virtual int calculateHeightLevelOrder(AbstractTreeNode* node) {
//            if (!node) return 0;
//            CustomQueue q;
//            q.enqueue(node);
//            int height = 0;
//            while (!q.isEmpty()) {
//                int nodesAtCurrentLevel = q.size();
//                if (nodesAtCurrentLevel == 0) break;
//                height++;
//                for (int i = 0; i < nodesAtCurrentLevel; ++i) {
//                    AbstractTreeNode* current = (AbstractTreeNode*)q.dequeue();
//                    if (!current) continue;
//                    AbstractTreeNode* child = current->getFirstChild();
//                    while (child) {
//                        q.enqueue(child);
//                        child = child->getNextSibling();
//                    }
//                }
//            }
//            return height;
//        }
//    public:
//        AbstractTree() : root(nullptr) {}
//        virtual ~AbstractTree() { delete root; }
//        int getHeight() { return calculateHeightRecursive(root); }
//        virtual void createSampleTree() = 0;
//        virtual void displayTree() = 0;
//    };

//    class GeneralTree : public AbstractTree {
//    public:
//        void createSampleTree() override {
//            root = new GeneralTreeNode(1);
//            root->setFirstChild(new GeneralTreeNode(2));
//            root->getFirstChild()->setNextSibling(new GeneralTreeNode(3));
//            root->getFirstChild()->setFirstChild(new GeneralTreeNode(4));
//        }
//        void displayTree() override {}
//    };

//    class BinaryTree : public AbstractTree {
//    public:
//        void createSampleTree() override {
//            root = new BinaryTreeNode(1);
//            root->setFirstChild(new BinaryTreeNode(2));
//            root->getFirstChild()->setNextSibling(new BinaryTreeNode(3));
//            ((BinaryTreeNode*)root->getFirstChild())->setLeft(new BinaryTreeNode(4));
//        }
//        void displayTree() override {}
//    };

//    class ThreadedBinaryTree : public BinaryTree {
//    public:
//        void createThreadedTree() {}
//        void postOrderTraversal() {}
//    };

//    class Forest {
//        AbstractTree** trees;
//        int treeCount;
//    public:
//        Forest(AbstractTree** treeArray, int count) : trees(treeArray), treeCount(count) {}
//        int getForestHeight() {
//            int maxHeight = 0;
//            for (int i = 0; i < treeCount; i++) {
//                maxHeight = custom_max(maxHeight, trees[i]->getHeight());
//            }
//            return maxHeight;
//        }
//    };
// }

// int main() {
//    cout << "=== 树结构代码重构复用演示 ===" << endl;
   
//    cout << "\n方案A: 组合复用" << endl;
//    {
//        CompositionApproach::TreeManager manager;
//        CompositionApproach::RecursiveTraversal recursive;
//        CompositionApproach::LevelOrderTraversal levelOrder;
       
//        manager.setTraversalStrategy(&recursive);
//        manager.createSampleGeneralTree();
//        cout << "通用树高度 (递归): " << manager.getTreeHeight() << endl;
       
//        manager.setTraversalStrategy(&levelOrder);
//        cout << "通用树高度 (层序): " << manager.getTreeHeight() << endl;
//    }
   
//    cout << "\n方案B: 继承复用" << endl;
//    {
//        InheritanceApproach::GeneralTree generalTree;
//        InheritanceApproach::BinaryTree binaryTree;
//        InheritanceApproach::ThreadedBinaryTree threadedTree;
       
//        generalTree.createSampleTree();
//        binaryTree.createSampleTree();
//        threadedTree.createSampleTree();
       
//        cout << "通用树高度: " << generalTree.getHeight() << endl;
//        cout << "二叉树高度: " << binaryTree.getHeight() << endl;
//        cout << "线索二叉树高度: " << threadedTree.getHeight() << endl;
       
//        InheritanceApproach::AbstractTree* trees[] = {&generalTree, &binaryTree, &threadedTree};
//        InheritanceApproach::Forest forest(trees, 3);
//        cout << "森林最大高度: " << forest.getForestHeight() << endl;
//    }
   
//    return 0;
// }
