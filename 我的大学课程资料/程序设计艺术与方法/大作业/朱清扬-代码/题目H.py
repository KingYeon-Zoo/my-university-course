"""
题目H: 电能输送
问题描述：
    从发电站(节点1)到变电站(节点N)输送电力
    有N个站点，M条输电线路
    每条线路有容量限制，可以双向输送
    求最大输送电力
    
解题思路：
    这是一个经典的网络最大流问题
    使用Dinic算法求解
    
算法原理：
    1. 构建残留网络
    2. 使用BFS构建层次图
    3. 使用DFS在层次图中寻找增广路
    4. 重复2-3直到不存在增广路
    
时间复杂度：O(N^2 * M)
"""

from collections import deque, defaultdict

class MaxFlow:
    def __init__(self, n):
        """
        初始化最大流算法
        n: 节点数量
        """
        self.n = n
        self.graph = defaultdict(lambda: defaultdict(int))
        
    def add_edge(self, u, v, cap):
        """
        添加边
        u -> v，容量为cap
        """
        self.graph[u][v] += cap
        self.graph[v][u] += cap  # 无向图，双向都可以
    
    def bfs(self, s, t):
        """
        BFS构建层次图
        返回是否能从s到达t
        """
        self.level = [-1] * (self.n + 1)
        self.level[s] = 0
        queue = deque([s])
        
        while queue:
            u = queue.popleft()
            for v in self.graph[u]:
                if self.level[v] < 0 and self.graph[u][v] > 0:
                    self.level[v] = self.level[u] + 1
                    queue.append(v)
        
        return self.level[t] >= 0
    
    def dfs(self, u, t, flow):
        """
        DFS寻找增广路
        u: 当前节点
        t: 目标节点
        flow: 当前流量
        返回实际增加的流量
        """
        if u == t:
            return flow
        
        for v in list(self.graph[u].keys()):
            if self.level[v] == self.level[u] + 1 and self.graph[u][v] > 0:
                min_flow = min(flow, self.graph[u][v])
                pushed = self.dfs(v, t, min_flow)
                
                if pushed > 0:
                    self.graph[u][v] -= pushed
                    self.graph[v][u] += pushed
                    return pushed
        
        return 0
    
    def max_flow(self, s, t):
        """
        计算从s到t的最大流
        """
        total_flow = 0
        
        while self.bfs(s, t):
            while True:
                pushed = self.dfs(s, t, float('inf'))
                if pushed == 0:
                    break
                total_flow += pushed
        
        return total_flow

def solve():
    """
    主求解函数
    """
    # 读取输入
    N, M = map(int, input().split())
    
    # 创建最大流对象
    mf = MaxFlow(N)
    
    # 读取边
    for _ in range(M):
        u, v, cap = map(int, input().split())
        mf.add_edge(u, v, cap)
    
    # 计算最大流：从节点1到节点N
    result = mf.max_flow(1, N)
    
    print(result)

if __name__ == "__main__":
    solve()

