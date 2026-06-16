#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cstring>

using namespace std;

const int MAX_N = 100;
vector<int> graph[MAX_N];
bool visited[MAX_N];
int degree[MAX_N];

void dfs(int node) {
	visited[node] = true;
	for (int neighbor : graph[node]) {
		if (!visited[neighbor]) {
			dfs(neighbor);
		}
	}
}

bool isConnected(int n) {
	memset(visited, false, sizeof(visited));
	int startNode = -1;
	for (int i = 0; i < n; ++i) {
		if (degree[i] > 0) {
			startNode = i;
			break;
		}
	}
	if (startNode == -1) return true;

	dfs(startNode);

	for (int i = 0; i < n; ++i) {
		if (degree[i] > 0 && !visited[i]) {
			return false;
		}
	}
	return true;
}

void checkEuler(int n) {
	if (!isConnected(n)) {
		cout << "该图不是连通图，因此不是欧拉图或半欧拉图。" << endl;
		return;
	}

	int oddCount = 0;
	for (int i = 0; i < n; ++i) {
		if (degree[i] % 2 != 0) {
			oddCount++;
		}
	}

	if (oddCount == 0) {
		cout << "该图是欧拉图。" << endl;
	}
	else if (oddCount == 2) {
		cout << "该图是半欧拉图。" << endl;
	}
	else {
		cout << "该图既不是欧拉图也不是半欧拉图。" << endl;
	}
}


int main() {
	int n, m;
	cout << "请输入图的顶点数和边数：" << endl;
	cin >> n >> m;

	for (int i = 0; i < m; ++i) {
		cout << "输入边（用边连接的两个顶点来代替）：";
		int u, v;
		cin >> u >> v;
		graph[u].push_back(v);
		graph[v].push_back(u);
		degree[u]++;
		degree[v]++;
	}

	checkEuler(n);

	return 0;
}
