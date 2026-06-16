#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <algorithm>
#include <windows.h>
using namespace std;

// 扫描当前目录中的所有input*.txt文件
vector<string> scanInputFiles() {
    vector<string> inputFiles;
    WIN32_FIND_DATAA findFileData; 
    HANDLE hFind = FindFirstFileA("input*.txt", &findFileData); 
    
    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            string filename = findFileData.cFileName;
            inputFiles.push_back(filename);
        } while (FindNextFileA(hFind, &findFileData) != 0);  
        FindClose(hFind);
    }
        
    sort(inputFiles.begin(), inputFiles.end());
    return inputFiles;
}

bool dfs(int u, vector<vector<int>>& graph, vector<int>& match, vector<bool>& used) {
    for (int v : graph[u]) {
        if (!used[v]) {
            used[v] = true;
            if (match[v] == -1 || dfs(match[v], graph, match, used)) {
                match[v] = u; 
                return true;
            }
        }
    }
    return false;
}

int maxMatching(int m, int n, vector<vector<int>>& graph, vector<pair<int,int>>& result) {
    vector<int> match(n + 1, -1);  
    int matchCount = 0;
    
    for (int u = 1; u <= m; u++) {
        vector<bool> used(n + 1, false);  
        if (dfs(u, graph, match, used)) {
            matchCount++;
        }
    }

    result.clear();
    for (int v = m + 1; v <= n; v++) {
        if (match[v] != -1) {
            result.push_back({match[v], v});
        }
    }
    
    return matchCount;
}

bool readInput(const string& filename, int& m, int& n, vector<vector<int>>& graph) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "无法打开输入文件: " << filename << endl;
        return false;
    }
    
    file >> m >> n;
    if (m <= 0 || n <= 0 || m >= n) {
        cerr << "输入数据格式错误: m=" << m << ", n=" << n << endl;
        return false;
    }

    graph.assign(m + 1, vector<int>());

    int i, j;
    while (file >> i >> j) {
        if (i == -1 && j == -1) {
            break;  
        }
        
        if (i < 1 || i > m || j < m + 1 || j > n) {
            cerr << "输入数据超出范围: i=" << i << ", j=" << j << endl;
            continue;
        }
        
        graph[i].push_back(j);
    }
    
    file.close();
    return true;
}

// 将结果写入输出文件
void writeOutput(const string& filename, int maxMatch, const vector<pair<int,int>>& result) {
    ofstream file(filename);
    if (!file.is_open()) {
        cerr << "无法创建输出文件: " << filename << endl;
        return;
    }
    
    if (maxMatch == 0) {
        file << "No Solution!" << endl;
    } else {
        file << maxMatch << endl;
        for (const auto& pair : result) {
            file << pair.first << "  " << pair.second << endl;
        }
    }
    
    file.close();
}

// 显示文件选择菜单
void displayMenu(const vector<string>& files) {
    cout << "\n=== 二分图最大匹配算法 - 测试文件选择 ===" << endl;
    cout << "请选择要处理的输入文件：" << endl;
    cout << "----------------------------------------" << endl;
    
    for (size_t i = 0; i < files.size(); i++) {
        cout << (i + 1) << ". " << files[i] << endl;
    }
    
    cout << "0. 退出程序" << endl;
    cout << "----------------------------------------" << endl;
    cout << "请输入选择 (0-" << files.size() << "): ";
}

// 获取用户选择并验证输入
int getUserChoice(int maxChoice) {
    int choice;
    while (true) {
        if (cin >> choice) {
            if (choice >= 0 && choice <= maxChoice) {
                return choice;
            } else {
                cout << "输入超出范围，请重新输入 (0-" << maxChoice << "): ";
            }
        } else {
            cout << "输入格式错误，请输入数字 (0-" << maxChoice << "): ";
            cin.clear();
            cin.ignore(10000, '\n');
        }
    }
}

// 根据输入文件名生成对应的输出文件名
string generateOutputFilename(const string& inputFilename) {
    size_t dotPos = inputFilename.find(".txt");
    if (dotPos != string::npos) {
        string baseName = inputFilename.substr(0, dotPos);
        if (baseName.substr(0, 5) == "input") {
            return "output" + baseName.substr(5) + ".txt";
        }
    }
    return "output.txt";
}

int main() {
    vector<string> inputFiles = scanInputFiles();
    
    if (inputFiles.empty()) {
        cout << "未找到任何input*.txt文件！" << endl;
        cout << "请确保当前目录中存在input.txt、input1.txt、input2.txt等文件。" << endl;
        return 1;
    }
    
    while (true) {
        displayMenu(inputFiles);
        
        int choice = getUserChoice(inputFiles.size());
        
        if (choice == 0) {
            cout << "程序退出。" << endl;
            break;
        }
        
        string selectedFile = inputFiles[choice - 1];
        string outputFile = generateOutputFilename(selectedFile);
        
        cout << "\n正在处理文件: " << selectedFile << endl;
        cout << "输出文件: " << outputFile << endl;
        
        int m, n;
        vector<vector<int>> graph;
        vector<pair<int,int>> result;
        
        if (!readInput(selectedFile, m, n, graph)) {
            cerr << "读取输入文件失败: " << selectedFile << endl;
            cout << "按任意键继续..." << endl;
            cin.ignore();
            cin.get();
            continue;
        }
        
        int maxMatch = maxMatching(m, n, graph, result);
        
        writeOutput(outputFile, maxMatch, result);
        
        cout << "处理完成！" << endl;
        cout << "最大匹配数: " << maxMatch << endl;
        cout << "结果已写入: " << outputFile << endl;
        cout << "\n按任意键继续..." << endl;
        cin.ignore();
        cin.get();
    }
    
    return 0;
}
