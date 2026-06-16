"""
实验5-题目3：数列位置匹配
擦掉某些数后，最多能有多少个数在自己的位置上（A[i] = i）
"""

def max_position_match(n, numbers):
    """
    使用动态规划求解
    dp[i][j] = 考虑前i个元素，选了j个，最多有多少个满足A[i]=i
    """
    # dp[i][j] 表示考虑前i个元素，选了j个，最多有多少个在正确位置
    # 空间优化：只需要记录当前行和上一行
    INF = -float('inf')
    
    # 初始化
    prev = [INF] * (n + 1)
    prev[0] = 0  # 选0个元素，0个满足条件
    
    for i in range(n):
        curr = [INF] * (n + 1)
        
        for j in range(i + 2):  # 最多选i+1个
            # 不选第i个元素
            if j <= i:
                curr[j] = max(curr[j], prev[j])
            
            # 选第i个元素（它成为第j+1个）
            if j < i + 1 and prev[j] != INF:
                # numbers[i]是1-based，j+1是新位置（1-based）
                if numbers[i] == j + 1:
                    # 满足条件
                    curr[j + 1] = max(curr[j + 1], prev[j] + 1)
                else:
                    # 不满足条件
                    curr[j + 1] = max(curr[j + 1], prev[j])
        
        prev = curr
    
    # 返回最大值
    result = 0
    for j in range(n + 1):
        if prev[j] != INF:
            result = max(result, prev[j])
    
    return result


def main():
    # 读取输入
    n = int(input())
    numbers = list(map(int, input().split()))
    
    # 计算结果
    result = max_position_match(n, numbers)
    
    # 输出
    print(result)


if __name__ == "__main__":
    main()
