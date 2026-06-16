"""
实验5-题目2：青蛙过河
动态规划求青蛙过河最少踩到的石子数
"""

def frog_crossing(L, S, T, M, stones):
    """
    使用动态规划求解青蛙过河问题
    """
    if M == 0:
        return 0
    
    # 特殊情况：S == T，青蛙只能跳固定距离
    if S == T:
        # 检查是否所有距离为S的倍数的石子都要踩
        count = 0
        for stone in stones:
            if stone % S == 0:
                count += 1
        return count
    
    # 优化：如果石子间距很大，可以压缩距离
    # 当间距 > S*T 时，青蛙可以跳过去而不踩石子
    stones.sort()
    compressed_stones = []
    compressed_pos = 0
    
    for i in range(M):
        if i == 0:
            gap = stones[i]
        else:
            gap = stones[i] - stones[i-1]
        
        # 如果间距太大，压缩到S*T
        if gap > S * T:
            compressed_pos += S * T
        else:
            compressed_pos += gap
        
        compressed_stones.append(compressed_pos)
    
    # 新的终点位置
    if M > 0:
        last_stone = stones[-1]
        remaining = L - last_stone
        if remaining > S * T:
            new_L = compressed_pos + S * T
        else:
            new_L = compressed_pos + remaining
    else:
        new_L = L
    
    # DP数组
    # dp[i] = 到达位置i最少踩到的石子数
    # 初始化为无穷大
    dp = [float('inf')] * (new_L + 1)
    dp[0] = 0
    
    # 标记石子位置
    stone_set = set(compressed_stones)
    
    # 动态规划
    for i in range(new_L + 1):
        if dp[i] == float('inf'):
            continue
        
        # 当前位置的石子数
        current_stones = dp[i]
        if i in stone_set:
            current_stones += 1
        
        # 尝试跳S到T的距离
        for jump in range(S, T + 1):
            next_pos = i + jump
            
            if next_pos > new_L:
                # 已经过河
                # 更新答案（不需要踩next_pos的石子）
                if i in stone_set:
                    dp[new_L] = min(dp[new_L], dp[i] + 1)
                else:
                    dp[new_L] = min(dp[new_L], dp[i])
            else:
                # 更新next_pos
                if next_pos in stone_set:
                    dp[next_pos] = min(dp[next_pos], dp[i] + 1)
                else:
                    dp[next_pos] = min(dp[next_pos], dp[i])
    
    # 找最小值：从L-T+1到L的任意位置跳出
    result = float('inf')
    for i in range(max(0, new_L - T + 1), new_L + 1):
        if dp[i] != float('inf'):
            result = min(result, dp[i])
    
    return result if result != float('inf') else 0


def main():
    # 读取输入
    L = int(input())
    S, T, M = map(int, input().split())
    
    if M > 0:
        stones = list(map(int, input().split()))
    else:
        stones = []
    
    # 计算结果
    result = frog_crossing(L, S, T, M, stones)
    
    # 输出
    print(result)


if __name__ == "__main__":
    main()

