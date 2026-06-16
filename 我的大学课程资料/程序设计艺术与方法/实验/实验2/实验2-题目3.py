"""
实验2-题目3：矩形数量
使用深度优先搜索（DFS）或广度优先搜索（BFS）统计画面上的矩形数量
"""

def count_rectangles_dfs(grid, n, m):
    """
    使用DFS统计矩形数量
    """
    visited = [[False] * m for _ in range(n)]
    count = 0
    
    for i in range(n):
        for j in range(m):
            if grid[i][j] == '#' and not visited[i][j]:
                # 发现一个新的矩形
                dfs(grid, visited, i, j, n, m)
                count += 1
    
    return count


def dfs(grid, visited, i, j, n, m):
    """
    深度优先搜索，标记连通的'#'区域
    """
    # 边界检查
    if i < 0 or i >= n or j < 0 or j >= m:
        return
    
    # 如果已访问或不是'#'，返回
    if visited[i][j] or grid[i][j] != '#':
        return
    
    # 标记为已访问
    visited[i][j] = True
    
    # 递归访问四个方向
    dfs(grid, visited, i - 1, j, n, m)  # 上
    dfs(grid, visited, i + 1, j, n, m)  # 下
    dfs(grid, visited, i, j - 1, n, m)  # 左
    dfs(grid, visited, i, j + 1, n, m)  # 右


def count_rectangles_bfs(grid, n, m):
    """
    使用BFS统计矩形数量（备选方法）
    """
    from collections import deque
    
    visited = [[False] * m for _ in range(n)]
    count = 0
    
    for i in range(n):
        for j in range(m):
            if grid[i][j] == '#' and not visited[i][j]:
                # 发现一个新的矩形，进行BFS
                queue = deque([(i, j)])
                visited[i][j] = True
                
                while queue:
                    x, y = queue.popleft()
                    
                    # 检查四个方向
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        
                        if 0 <= nx < n and 0 <= ny < m:
                            if grid[nx][ny] == '#' and not visited[nx][ny]:
                                visited[nx][ny] = True
                                queue.append((nx, ny))
                
                count += 1
    
    return count


def main():
    # 读取输入
    first_line = input().split()
    n = int(first_line[0])
    m = int(first_line[1])
    
    # 读取画面
    grid = []
    for i in range(n):
        row = input().strip()
        # 处理可能的空格
        row = row.replace(' ', '')
        grid.append(list(row))
    
    # 统计矩形数量（使用DFS）
    result = count_rectangles_dfs(grid, n, m)
    
    # 输出结果
    print(result)


if __name__ == "__main__":
    main()

