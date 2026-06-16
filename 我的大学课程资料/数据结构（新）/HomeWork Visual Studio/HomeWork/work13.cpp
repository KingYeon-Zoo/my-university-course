//#include <iostream>
//
//using namespace std;
//
//const int MAX_VERTICES = 100;
//
//struct AdjListNode {
//    int dest;
//    AdjListNode* next;
//    AdjListNode(int d) : dest(d), next(nullptr) {}
//};
//
//struct AdjList {
//    AdjListNode* head;
//};
//
//class Graph {
//public:
//    int V;
//    AdjList* array;
//    int* inDegree;
//
//    Graph(int vertices) : V(vertices) {
//        array = new AdjList[V];
//        inDegree = new int[V];
//        for (int i = 0; i < V; ++i) {
//            array[i].head = nullptr;
//            inDegree[i] = 0;
//        }
//    }
//
//    ~Graph() {
//        for (int i = 0; i < V; ++i) {
//            AdjListNode* current = array[i].head;
//            while (current != nullptr) {
//                AdjListNode* temp = current;
//                current = current->next;
//                delete temp;
//            }
//        }
//        delete[] array;
//        delete[] inDegree;
//    }
//
//    void addEdge(int src, int dest) {
//        if (src < 0 || src >= V || dest < 0 || dest >= V) return;
//        AdjListNode* newNode = new AdjListNode(dest);
//        newNode->next = array[src].head;
//        array[src].head = newNode;
//        inDegree[dest]++;
//    }
//
//    void findAllTopologicalSortsUtil(int* result, int count, bool* visited) {
//        bool flag = false;
//        for (int i = 0; i < V; ++i) {
//            if (inDegree[i] == 0 && !visited[i]) {
//                AdjListNode* temp = array[i].head;
//                while (temp != nullptr) {
//                    inDegree[temp->dest]--;
//                    temp = temp->next;
//                }
//
//                result[count] = i;
//                visited[i] = true;
//                findAllTopologicalSortsUtil(result, count + 1, visited);
//
//                visited[i] = false;
//                temp = array[i].head;
//                while (temp != nullptr) {
//                    inDegree[temp->dest]++;
//                    temp = temp->next;
//                }
//                flag = true;
//            }
//        }
//
//        if (!flag) {
//            if (count == V) { 
//                for (int i = 0; i < V; ++i) {
//                    cout << result[i] << (i == V - 1 ? "" : " -> ");
//                }
//                cout << endl;
//                countPrinted++; 
//            } else {
//                
//            }
//        }
//    }
//
//    void findAllTopologicalSorts() {
//        if (V == 0) {
//            cout << "图为空。" << endl;
//            return;
//        }
//        bool* visited = new bool[V];
//        int* result = new int[V];
//        for (int i = 0; i < V; ++i) {
//            visited[i] = false;
//        }
//
//        cout << "所有拓扑排序:" << endl;
//        Graph::countPrinted = 0; 
//        findAllTopologicalSortsUtil(result, 0, visited);
//
//        bool hasCycle = false;
//        int nodesInPath = 0;
//        for(int i=0; i<V; ++i) {
//            if(result[i] >=0 && result[i] < V) nodesInPath++;
//        }
//
//        int edgeCount = 0;
//        for(int i=0; i<V; ++i) {
//            AdjListNode* temp = array[i].head;
//            while(temp) {
//                edgeCount++;
//                temp = temp->next;
//            }
//        }
//        
//        if (nodesInPath < V && V > 0 && edgeCount > 0) { 
//            bool allZeroInDegree = true;
//            for(int i=0; i<V; ++i) {
//                if(inDegree[i] != 0) {
//                    allZeroInDegree = false;
//                    break;
//                }
//            }
//            bool printedNoPath = false;
//            findAllTopologicalSortsUtil(result,0,visited);
//            if(countPrinted == 0 && !allZeroInDegree ) { 
//                cout << "图包含环或存在无法从某些起点进行完整拓扑排序的断开连接。" << endl;
//                printedNoPath = true;
//            }
//            
//            int checkCount = 0;
//            for (int i=0; i<V; ++i) if (result[i] == -1 && visited[i] == false) checkCount++;
//            if (checkCount == V && V > 0 && !printedNoPath) { 
//                
//            }
//
//        }
//        if (countPrinted == 0 && V > 0 && !hasCycle) {
//            bool allVisited = true;
//            for(int i=0; i<V; ++i) {
//                if(!visited[i]) {
//                    bool isIsolated = true;
//                    if(inDegree[i] != 0) isIsolated = false;
//                    AdjListNode* temp = array[i].head;
//                    if(temp != nullptr) isIsolated = false;
//                    
//                    bool isPartOfPrintedPath = false;
//                    
//                    if(!isIsolated) allVisited = false;
//                }
//            }
//        }
//
//
//        delete[] visited;
//        delete[] result;
//    }
//
//    bool isReachable(int startNode, int endNode, bool visitedNodes[]) {
//        if (startNode == endNode) return true;
//        visitedNodes[startNode] = true;
//        AdjListNode* temp = array[startNode].head;
//        while(temp) {
//            if(!visitedNodes[temp->dest]){
//                if(isReachable(temp->dest, endNode, visitedNodes)) return true;
//            }
//            temp = temp->next;
//        }
//        return false;
//    }
//    static int countPrinted;
//};
//
//int Graph::countPrinted = 0;
//
//void printGraph(Graph& g) {
//    cout << "图的邻接表示:" << endl;
//    for (int i = 0; i < g.V; ++i) {
//        cout << "顶点 " << i << " (入度: " << g.inDegree[i] << "): ";
//        AdjListNode* temp = g.array[i].head;
//        while (temp) {
//            cout << "-> " << temp->dest;
//            temp = temp->next;
//        }
//        cout << endl;
//    }
//    cout << endl;
//}
//
//int main() {
//    Graph g1(6);
//    g1.addEdge(5, 2);
//    g1.addEdge(5, 0);
//    g1.addEdge(4, 0);
//    g1.addEdge(4, 1);
//    g1.addEdge(2, 3);
//    g1.addEdge(3, 1);
//    cout << "--- 图 1 (有向无环图) ---" << endl;
//    printGraph(g1);
//    g1.findAllTopologicalSorts();
//    cout << endl;
//
//    Graph::countPrinted = 0;
//    Graph g2(4);
//    g2.addEdge(0, 1);
//    g2.addEdge(1, 2);
//    g2.addEdge(2, 3);
//    cout << "--- 图 2 (简单链) ---" << endl;
//    printGraph(g2);
//    g2.findAllTopologicalSorts();
//    cout << endl;
//
//    Graph::countPrinted = 0;
//    Graph g3(3);
//    g3.addEdge(0, 1);
//    g3.addEdge(1, 2);
//    g3.addEdge(2, 0);
//    cout << "--- 图 3 (含环) ---" << endl;
//    printGraph(g3);
//    g3.findAllTopologicalSorts();
//    cout << endl;
//
//    Graph::countPrinted = 0;
//    Graph g4(4);
//    g4.addEdge(0,1);
//    g4.addEdge(0,2);
//    g4.addEdge(1,3);
//    g4.addEdge(2,3);
//    cout << "--- 图 4 (钻石形状) ---" << endl;
//    printGraph(g4);
//    g4.findAllTopologicalSorts();
//    cout << endl;
//
//    Graph::countPrinted = 0;
//    Graph g5(2);
//    cout << "--- 图 5 (断开连接, 2节点, 0边) ---" << endl;
//    printGraph(g5);
//    g5.findAllTopologicalSorts(); 
//    cout << endl;
//
//    Graph::countPrinted = 0;
//    Graph g6(3);
//    g6.addEdge(0,1);
//    cout << "--- 图 6 (部分连接) ---" << endl;
//    printGraph(g6);
//    g6.findAllTopologicalSorts();
//    cout << endl;
//
//    return 0;
//}
