#include <iostream>
#include <vector>
#include <queue>
using namespace std;

const int MAXN = 1005;
vector<int> graph[MAXN];
int color[MAXN];
int match[MAXN];
bool visited[MAXN];
int n, m;

bool isBipartite(int start) {
    if (color[start] != 0) return true;

    queue<int> q;
    q.push(start);
    color[start] = 1;

    while (!q.empty()) {
        int curr = q.front();
        q.pop();

        for (int next : graph[curr]) {
            if (color[next] == 0) {
                color[next] = -color[curr];
                q.push(next);
            }
            else if (color[next] == color[curr]) {
                return false;
            }
        }
    }
    return true;
}

bool dfs(int u) {
    for (int v : graph[u]) {
        if (!visited[v]) {
            visited[v] = true;
            if (match[v] == -1 || dfs(match[v])) {
                match[v] = u;
                return true;
            }
        }
    }
    return false;
}

int hungarian() {
    fill(match, match + MAXN, -1);
    int result = 0;

    for (int i = 1; i <= n; i++) {
        if (color[i] == 1) {
            fill(visited, visited + MAXN, false);
            if (dfs(i)) result++;
        }
    }
    return result;
}

int main() {
    cout << "输入顶点数和边数：";
    cin >> n >> m;

    for (int i = 0; i < m; i++) {
        cout << "输入边（用边所连接的两个顶点代替）：";
        int u, v;
        cin >> u >> v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    fill(color, color + MAXN, 0);

    bool is_bipartite = true;
    for (int i = 1; i <= n; i++) {
        if (color[i] == 0) {
            if (!isBipartite(i)) {
                is_bipartite = false;
                break;
            }
        }
    }

    if (!is_bipartite) {
        cout << "不是二分图" << endl;
    }
    else {
        int max_matching = hungarian();
        cout << "最大匹配: " << max_matching << endl;
    }

    return 0;
}
