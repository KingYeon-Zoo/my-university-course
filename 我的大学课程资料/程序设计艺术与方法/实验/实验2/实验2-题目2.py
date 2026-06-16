"""
实验2-题目2：货币系统
找到与原货币系统等价的最小货币系统
"""

def find_minimum_currency_system(n, currencies):
    """
    找到最小等价货币系统
    
    核心思想：
    如果一个面额可以由其他面额组合得到，那么这个面额是冗余的
    保留那些无法由其他面额组合得到的面额
    
    算法：
    1. 对面额从小到大排序
    2. 使用完全背包DP判断每个面额是否可以由更小的面额组成
    3. 如果不能组成，则该面额是必需的
    """
    # 排序
    currencies.sort()
    
    # 存储必需的货币面额
    essential = []
    
    for i in range(n):
        current = currencies[i]
        
        # 检查current是否可以由essential中的面额组成
        if not can_represent(essential, current):
            # 不能组成，说明这个面额是必需的
            essential.append(current)
    
    return len(essential)


def can_represent(coins, target):
    """
    使用完全背包判断target是否可以由coins中的面额组成
    coins: 可用的货币面额列表
    target: 目标金额
    返回: True如果可以组成，False如果不能组成
    """
    if not coins or target <= 0:
        return False
    
    # dp[i]表示金额i是否可以由coins组成
    dp = [False] * (target + 1)
    dp[0] = True  # 金额0可以组成（不选任何货币）
    
    # 完全背包
    for coin in coins:
        for i in range(coin, target + 1):
            if dp[i - coin]:
                dp[i] = True
    
    return dp[target]


def main():
    # 读取测试组数
    t = int(input())
    
    for _ in range(t):
        # 读取货币种数
        n = int(input())
        
        # 读取货币面额
        currencies = list(map(int, input().split()))
        
        # 计算最小货币系统
        result = find_minimum_currency_system(n, currencies)
        
        # 输出结果
        print(result)


if __name__ == "__main__":
    main()

