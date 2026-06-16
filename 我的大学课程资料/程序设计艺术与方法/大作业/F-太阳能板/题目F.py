"""
题目F: 太阳能板
问题描述：
    n个仓库通过n-1条道路连接成树
    每个仓库i有原始材料，吸光能力为v[i]
    选择被道路直接相连的两个仓库的材料进行合成，得到的新材料吸光能力为v[i]*v[j]
    每种材料只能使用一次
    求合成的新材料吸光能力总和的最大值
    
解题思路：
    这是一个树上的最大权匹配问题，使用树形DP求解
    
状态定义：
    dp[u][0]: 以u为根的子树中，节点u不参与匹配时的最大吸光能力总和
    dp[u][1]: 以u为根的子树中，节点u已经与其父节点匹配时的最大吸光能力总和
    
状态转移：
    1. 当u不参与匹配时(dp[u][0])：
       - u的每个子节点v可以选择：
         a) 不参与匹配: dp[v][0]
         b) 与u匹配: dp[v][0] + value[u] * value[v]
       - 选择收益最大的方案
       - 但只能选择最多一个子节点与u匹配
    
    2. 当u已经匹配时(dp[u][1])：
       - 所有子节点都只能选择不参与匹配
       - dp[u][1] = sum(dp[v][0]) for all children v
    
最终答案：
    以任意节点为根的dp[root][0]
"""

import sys
from collections import defaultdict

def dfs(u, parent, graph, value, dp):
    """
    树形DP求解
    u: 当前节点
    parent: 父节点
    graph: 邻接表
    value: 每个节点的吸光能力
    dp: DP数组
    """
    # dp[u][0]: u不匹配的最大值
    # dp[u][1]: u与父节点匹配的最大值
    
    children = [v for v in graph[u] if v != parent]
    
    # 先递归计算所有子节点
    for v in children:
        dfs(v, u, graph, value, dp)
    
    # 情况1：u与父节点匹配
    # u不能再与子节点匹配，所有子节点只能选择"不匹配"状态
    dp[u][1] = sum(dp[v][0] for v in children)
    
    # 情况2：u不与父节点匹配
    # u可以选择：(a) 完全不匹配 (b) 与某个子节点匹配
    
    # (a) u完全不匹配，所有子节点选择最优
    dp[u][0] = sum(max(dp[v][0], dp[v][1]) for v in children)
    
    # (b) u与某个子节点v匹配
    for v in children:
        # u与v匹配：
        # - 收益: value[u] * value[v]
        # - v与父节点u匹配了，v的子树用dp[v][1]
        # - 其他子节点选择最优
        match_gain = value[u] * value[v] + dp[v][1]
        other_gain = sum(max(dp[w][0], dp[w][1]) for w in children if w != v)
        dp[u][0] = max(dp[u][0], match_gain + other_gain)

def solve():
    """
    主求解函数
    """
    n = int(input())
    
    # 构建图
    graph = defaultdict(list)
    for _ in range(n - 1):
        a, b = map(int, input().split())
        graph[a].append(b)
        graph[b].append(a)
    
    # 读取每个仓库的吸光能力
    values = [0] + list(map(int, input().split()))  # 1-indexed
    
    # DP数组
    dp = [[0, 0] for _ in range(n + 1)]
    
    # 以节点1为根进行树形DP
    dfs(1, -1, graph, values, dp)
    
    # 答案是根节点不参与匹配的最大值
    print(dp[1][0])

if __name__ == "__main__":
    solve()

