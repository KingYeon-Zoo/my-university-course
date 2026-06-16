"""
经典动态规划算法实现
包含：最长公共子序列(LCS)和0-1背包问题
"""

import time
import numpy as np
from typing import List, Tuple, Any


class LCSAlgorithm:
    """最长公共子序列算法实现"""
    
    def __init__(self):
        self.dp_table = None
        self.comparisons = 0
        
    def lcs_length(self, X: str, Y: str) -> Tuple[int, List[List[int]]]:
        """
        计算两个序列的最长公共子序列长度
        
        参数:
            X: 第一个序列
            Y: 第二个序列
            
        返回:
            (LCS长度, DP表格)
        """
        m, n = len(X), len(Y)
        self.comparisons = 0
        
        # 创建DP表格
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # 填充DP表格
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                self.comparisons += 1
                if X[i-1] == Y[j-1]:
                    # 字符相同，LCS长度加1
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    # 字符不同，取两个方向的最大值
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        self.dp_table = dp
        return dp[m][n], dp
    
    def get_lcs_string(self, X: str, Y: str, dp: List[List[int]]) -> str:
        """
        根据DP表格回溯得到LCS字符串
        
        参数:
            X: 第一个序列
            Y: 第二个序列
            dp: DP表格
            
        返回:
            LCS字符串
        """
        result = []
        i, j = len(X), len(Y)
        
        # 从右下角回溯
        while i > 0 and j > 0:
            if X[i-1] == Y[j-1]:
                result.append(X[i-1])
                i -= 1
                j -= 1
            elif dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1
        
        return ''.join(reversed(result))
    
    def solve(self, X: str, Y: str) -> Tuple[int, str, List[List[int]]]:
        """
        完整求解LCS问题
        
        参数:
            X: 第一个序列
            Y: 第二个序列
            
        返回:
            (LCS长度, LCS字符串, DP表格)
        """
        length, dp = self.lcs_length(X, Y)
        lcs_str = self.get_lcs_string(X, Y, dp)
        return length, lcs_str, dp


class Knapsack01:
    """0-1背包问题算法实现"""
    
    def __init__(self):
        self.dp_table = None
        self.comparisons = 0
        
    def solve(self, weights: List[int], values: List[int], capacity: int) -> Tuple[int, List[List[int]]]:
        """
        求解0-1背包问题
        
        参数:
            weights: 物品重量列表
            values: 物品价值列表
            capacity: 背包容量
            
        返回:
            (最大价值, DP表格)
        """
        n = len(weights)
        self.comparisons = 0
        
        # 创建DP表格 dp[i][w]表示前i个物品在容量为w时的最大价值
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        
        # 填充DP表格
        for i in range(1, n + 1):
            for w in range(capacity + 1):
                # 不选第i个物品
                dp[i][w] = dp[i-1][w]
                
                # 如果能选第i个物品，比较选和不选
                if w >= weights[i-1]:
                    self.comparisons += 1
                    dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]] + values[i-1])
        
        self.dp_table = dp
        return dp[n][capacity], dp
    
    def get_selected_items(self, weights: List[int], values: List[int], 
                          capacity: int, dp: List[List[int]]) -> List[int]:
        """
        根据DP表格回溯得到选中的物品
        
        参数:
            weights: 物品重量列表
            values: 物品价值列表
            capacity: 背包容量
            dp: DP表格
            
        返回:
            选中的物品索引列表
        """
        n = len(weights)
        selected = []
        w = capacity
        
        # 从右下角回溯
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected.append(i-1)
                w -= weights[i-1]
        
        return list(reversed(selected))
    
    def solve_with_items(self, weights: List[int], values: List[int], 
                        capacity: int) -> Tuple[int, List[int], List[List[int]]]:
        """
        完整求解0-1背包问题，包括选中的物品
        
        参数:
            weights: 物品重量列表
            values: 物品价值列表
            capacity: 背包容量
            
        返回:
            (最大价值, 选中的物品索引, DP表格)
        """
        max_value, dp = self.solve(weights, values, capacity)
        selected = self.get_selected_items(weights, values, capacity, dp)
        return max_value, selected, dp


class BruteForceLCS:
    """最长公共子序列的暴力解法（用于对比）"""
    
    def __init__(self):
        self.comparisons = 0
    
    def lcs_length(self, X: str, Y: str) -> int:
        """递归求解LCS长度"""
        self.comparisons += 1
        
        if not X or not Y:
            return 0
        
        if X[-1] == Y[-1]:
            return 1 + self.lcs_length(X[:-1], Y[:-1])
        else:
            return max(self.lcs_length(X[:-1], Y), 
                      self.lcs_length(X, Y[:-1]))


class BruteForceKnapsack:
    """0-1背包的暴力解法（用于对比）"""
    
    def __init__(self):
        self.comparisons = 0
    
    def solve(self, weights: List[int], values: List[int], 
             capacity: int, n: int = None) -> int:
        """递归求解背包问题"""
        if n is None:
            n = len(weights)
        
        self.comparisons += 1
        
        # 基础情况
        if n == 0 or capacity == 0:
            return 0
        
        # 如果第n个物品的重量大于背包容量，不能放入
        if weights[n-1] > capacity:
            return self.solve(weights, values, capacity, n-1)
        
        # 返回两种情况的最大值：放入或不放入第n个物品
        else:
            include = values[n-1] + self.solve(weights, values, 
                                               capacity - weights[n-1], n-1)
            exclude = self.solve(weights, values, capacity, n-1)
            return max(include, exclude)


def measure_time(func, *args) -> Tuple[Any, float]:
    """
    测量函数执行时间
    
    参数:
        func: 要测量的函数
        *args: 函数参数
        
    返回:
        (函数返回值, 执行时间(秒))
    """
    start_time = time.perf_counter()
    result = func(*args)
    end_time = time.perf_counter()
    return result, end_time - start_time


if __name__ == "__main__":
    # 测试LCS算法
    print("=" * 60)
    print("测试最长公共子序列算法")
    print("=" * 60)
    
    lcs = LCSAlgorithm()
    X = "ABCDGH"
    Y = "AEDFHR"
    
    length, lcs_str, dp = lcs.solve(X, Y)
    print(f"序列X: {X}")
    print(f"序列Y: {Y}")
    print(f"LCS长度: {length}")
    print(f"LCS字符串: {lcs_str}")
    print(f"比较次数: {lcs.comparisons}")
    print(f"\nDP表格:")
    for row in dp:
        print(row)
    
    # 测试0-1背包算法
    print("\n" + "=" * 60)
    print("测试0-1背包问题")
    print("=" * 60)
    
    knapsack = Knapsack01()
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8
    
    max_value, selected, dp = knapsack.solve_with_items(weights, values, capacity)
    print(f"物品重量: {weights}")
    print(f"物品价值: {values}")
    print(f"背包容量: {capacity}")
    print(f"最大价值: {max_value}")
    print(f"选中物品索引: {selected}")
    print(f"选中物品重量: {[weights[i] for i in selected]}")
    print(f"选中物品价值: {[values[i] for i in selected]}")
    print(f"比较次数: {knapsack.comparisons}")
    print(f"\nDP表格(部分):")
    for i, row in enumerate(dp):
        if i <= 4:
            print(f"物品{i}: {row[:min(10, len(row))]}")

