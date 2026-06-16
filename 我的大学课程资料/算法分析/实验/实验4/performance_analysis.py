"""
算法性能分析与可视化
"""

import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from dp_algorithms import LCSAlgorithm, Knapsack01, BruteForceLCS, BruteForceKnapsack

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
rcParams['axes.unicode_minus'] = False


def analyze_lcs_performance():
    """分析LCS算法的性能"""
    print("=" * 80)
    print("最长公共子序列(LCS)性能分析")
    print("=" * 80)
    
    # 测试不同规模
    sizes = [10, 20, 30, 50, 75, 100, 150, 200, 300, 500]
    times = []
    comparisons_list = []
    
    random.seed(42)
    lcs = LCSAlgorithm()
    
    print(f"\n{'输入规模n':<12} {'运行时间(ms)':<15} {'比较次数':<15} "
          f"{'理论复杂度':<15} {'实际增长率':<15}")
    print("-" * 80)
    
    for i, n in enumerate(sizes):
        # 生成随机字符串
        X = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=n))
        Y = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=n))
        
        # 测量运行时间
        start_time = time.perf_counter()
        length, lcs_str, dp = lcs.solve(X, Y)
        end_time = time.perf_counter()
        
        elapsed_time = (end_time - start_time) * 1000  # 转换为毫秒
        times.append(elapsed_time)
        comparisons_list.append(lcs.comparisons)
        
        # 计算增长率
        if i > 0:
            time_ratio = elapsed_time / times[i-1]
            size_ratio = n / sizes[i-1]
            growth_rate = f"{time_ratio:.2f}x"
        else:
            growth_rate = "-"
        
        print(f"{n:<12} {elapsed_time:<15.4f} {lcs.comparisons:<15} "
              f"{'O(n^2)':<15} {growth_rate:<15}")
    
    return sizes, times, comparisons_list


def analyze_knapsack_performance():
    """分析0-1背包算法的性能"""
    print("\n" + "=" * 80)
    print("0-1背包问题性能分析")
    print("=" * 80)
    
    # 测试不同规模
    item_counts = [5, 10, 20, 30, 50, 75, 100, 150, 200, 300]
    capacity = 100
    times = []
    comparisons_list = []
    
    random.seed(42)
    knapsack = Knapsack01()
    
    print(f"\n{'物品数n':<12} {'背包容量':<12} {'运行时间(ms)':<15} {'比较次数':<15} "
          f"{'理论复杂度':<15} {'实际增长率':<15}")
    print("-" * 90)
    
    for i, n in enumerate(item_counts):
        # 生成随机物品
        weights = [random.randint(1, 20) for _ in range(n)]
        values = [random.randint(1, 50) for _ in range(n)]
        
        # 测量运行时间
        start_time = time.perf_counter()
        max_value, dp = knapsack.solve(weights, values, capacity)
        end_time = time.perf_counter()
        
        elapsed_time = (end_time - start_time) * 1000  # 转换为毫秒
        times.append(elapsed_time)
        comparisons_list.append(knapsack.comparisons)
        
        # 计算增长率
        if i > 0:
            time_ratio = elapsed_time / times[i-1]
            size_ratio = n / item_counts[i-1]
            growth_rate = f"{time_ratio:.2f}x"
        else:
            growth_rate = "-"
        
        print(f"{n:<12} {capacity:<12} {elapsed_time:<15.4f} {knapsack.comparisons:<15} "
              f"{'O(nW)':<15} {growth_rate:<15}")
    
    return item_counts, times, comparisons_list


def plot_lcs_performance(sizes, times, comparisons_list):
    """绘制LCS性能图表"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 图1: 运行时间与输入规模关系
    ax1 = axes[0, 0]
    ax1.plot(sizes, times, 'bo-', label='实际运行时间', linewidth=2, markersize=6)
    
    # 添加理论曲线 O(n²)
    theoretical_n2 = [(n**2) / (sizes[0]**2) * times[0] for n in sizes]
    ax1.plot(sizes, theoretical_n2, 'r--', label='O(n²)理论曲线', linewidth=2, alpha=0.7)
    
    ax1.set_xlabel('输入规模 n', fontsize=12)
    ax1.set_ylabel('运行时间 (ms)', fontsize=12)
    ax1.set_title('图1 LCS算法运行时间与输入规模关系', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 比较次数与输入规模关系
    ax2 = axes[0, 1]
    ax2.plot(sizes, comparisons_list, 'go-', label='实际比较次数', linewidth=2, markersize=6)
    
    # 添加理论曲线 O(n²)
    theoretical_comp = [n**2 for n in sizes]
    ax2.plot(sizes, theoretical_comp, 'r--', label='n²理论曲线', linewidth=2, alpha=0.7)
    
    ax2.set_xlabel('输入规模 n', fontsize=12)
    ax2.set_ylabel('比较次数', fontsize=12)
    ax2.set_title('图2 LCS算法比较次数与输入规模关系', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 对数坐标下的时间复杂度验证
    ax3 = axes[1, 0]
    ax3.loglog(sizes, times, 'bo-', label='实际运行时间', linewidth=2, markersize=6)
    ax3.loglog(sizes, theoretical_n2, 'r--', label='O(n²)理论曲线', linewidth=2, alpha=0.7)
    
    ax3.set_xlabel('输入规模 n (对数)', fontsize=12)
    ax3.set_ylabel('运行时间 (ms, 对数)', fontsize=12)
    ax3.set_title('图3 LCS算法时间复杂度对数验证', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, which='both')
    
    # 图4: 单位规模平均时间
    ax4 = axes[1, 1]
    time_per_n2 = [t / (n**2) for t, n in zip(times, sizes)]
    ax4.plot(sizes, time_per_n2, 'mo-', linewidth=2, markersize=6)
    
    ax4.set_xlabel('输入规模 n', fontsize=12)
    ax4.set_ylabel('单位n²时间 (ms/n²)', fontsize=12)
    ax4.set_title('图4 LCS算法单位复杂度时间分析', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('LCS性能分析.png', dpi=300, bbox_inches='tight')
    print("\n已保存LCS性能分析图表: LCS性能分析.png")


def plot_knapsack_performance(item_counts, times, comparisons_list):
    """绘制0-1背包性能图表"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    capacity = 100
    
    # 图1: 运行时间与物品数关系
    ax1 = axes[0, 0]
    ax1.plot(item_counts, times, 'bo-', label='实际运行时间', linewidth=2, markersize=6)
    
    # 添加理论曲线 O(nW)
    theoretical_nw = [(n * capacity) / (item_counts[0] * capacity) * times[0] 
                      for n in item_counts]
    ax1.plot(item_counts, theoretical_nw, 'r--', label='O(nW)理论曲线', linewidth=2, alpha=0.7)
    
    ax1.set_xlabel('物品数 n', fontsize=12)
    ax1.set_ylabel('运行时间 (ms)', fontsize=12)
    ax1.set_title('图5 0-1背包算法运行时间与物品数关系', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 比较次数与物品数关系
    ax2 = axes[0, 1]
    ax2.plot(item_counts, comparisons_list, 'go-', label='实际比较次数', linewidth=2, markersize=6)
    
    # 添加理论曲线
    theoretical_comp = [n * capacity for n in item_counts]
    ax2.plot(item_counts, theoretical_comp, 'r--', label='n×W理论曲线', linewidth=2, alpha=0.7)
    
    ax2.set_xlabel('物品数 n', fontsize=12)
    ax2.set_ylabel('比较次数', fontsize=12)
    ax2.set_title('图6 0-1背包算法比较次数与物品数关系', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 对数坐标下的时间复杂度验证
    ax3 = axes[1, 0]
    ax3.loglog(item_counts, times, 'bo-', label='实际运行时间', linewidth=2, markersize=6)
    ax3.loglog(item_counts, theoretical_nw, 'r--', label='O(nW)理论曲线', linewidth=2, alpha=0.7)
    
    ax3.set_xlabel('物品数 n (对数)', fontsize=12)
    ax3.set_ylabel('运行时间 (ms, 对数)', fontsize=12)
    ax3.set_title('图7 0-1背包算法时间复杂度对数验证', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, which='both')
    
    # 图4: 单位规模平均时间
    ax4 = axes[1, 1]
    time_per_nw = [t / (n * capacity) for t, n in zip(times, item_counts)]
    ax4.plot(item_counts, time_per_nw, 'mo-', linewidth=2, markersize=6)
    
    ax4.set_xlabel('物品数 n', fontsize=12)
    ax4.set_ylabel('单位nW时间 (ms/(n×W))', fontsize=12)
    ax4.set_title('图8 0-1背包算法单位复杂度时间分析', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('背包性能分析.png', dpi=300, bbox_inches='tight')
    print("已保存0-1背包性能分析图表: 背包性能分析.png")


def compare_algorithms():
    """比较DP算法与暴力算法的性能"""
    print("\n" + "=" * 80)
    print("动态规划与暴力算法性能对比")
    print("=" * 80)
    
    sizes = [5, 7, 10, 12, 15]
    random.seed(42)
    
    # LCS对比
    print("\nLCS算法对比:")
    print(f"{'规模n':<8} {'DP时间(ms)':<15} {'暴力时间(ms)':<15} {'加速比':<10}")
    print("-" * 50)
    
    lcs_dp_times = []
    lcs_bf_times = []
    
    for n in sizes:
        X = ''.join(random.choices('ABCD', k=n))
        Y = ''.join(random.choices('ABCD', k=n))
        
        # DP算法
        lcs_dp = LCSAlgorithm()
        start = time.perf_counter()
        lcs_dp.solve(X, Y)
        dp_time = (time.perf_counter() - start) * 1000
        lcs_dp_times.append(dp_time)
        
        # 暴力算法
        lcs_bf = BruteForceLCS()
        start = time.perf_counter()
        lcs_bf.lcs_length(X, Y)
        bf_time = (time.perf_counter() - start) * 1000
        lcs_bf_times.append(bf_time)
        
        speedup = bf_time / dp_time if dp_time > 0 else 0
        print(f"{n:<8} {dp_time:<15.4f} {bf_time:<15.4f} {speedup:<10.2f}")
    
    # 绘制对比图
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # LCS对比
    ax1 = axes[0]
    ax1.plot(sizes, lcs_dp_times, 'bo-', label='动态规划', linewidth=2, markersize=8)
    ax1.plot(sizes, lcs_bf_times, 'rs-', label='暴力算法', linewidth=2, markersize=8)
    ax1.set_xlabel('输入规模 n', fontsize=12)
    ax1.set_ylabel('运行时间 (ms)', fontsize=12)
    ax1.set_title('图9 LCS算法对比', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # 0-1背包对比
    print("\n0-1背包算法对比:")
    print(f"{'物品数n':<8} {'DP时间(ms)':<15} {'暴力时间(ms)':<15} {'加速比':<10}")
    print("-" * 50)
    
    knap_dp_times = []
    knap_bf_times = []
    
    for n in sizes:
        weights = [random.randint(1, 10) for _ in range(n)]
        values = [random.randint(1, 20) for _ in range(n)]
        capacity = 20
        
        # DP算法
        knap_dp = Knapsack01()
        start = time.perf_counter()
        knap_dp.solve(weights, values, capacity)
        dp_time = (time.perf_counter() - start) * 1000
        knap_dp_times.append(dp_time)
        
        # 暴力算法
        knap_bf = BruteForceKnapsack()
        start = time.perf_counter()
        knap_bf.solve(weights, values, capacity)
        bf_time = (time.perf_counter() - start) * 1000
        knap_bf_times.append(bf_time)
        
        speedup = bf_time / dp_time if dp_time > 0 else 0
        print(f"{n:<8} {dp_time:<15.4f} {bf_time:<15.4f} {speedup:<10.2f}")
    
    ax2 = axes[1]
    ax2.plot(sizes, knap_dp_times, 'bo-', label='动态规划', linewidth=2, markersize=8)
    ax2.plot(sizes, knap_bf_times, 'rs-', label='暴力算法', linewidth=2, markersize=8)
    ax2.set_xlabel('物品数 n', fontsize=12)
    ax2.set_ylabel('运行时间 (ms)', fontsize=12)
    ax2.set_title('图10 0-1背包算法对比', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('算法对比.png', dpi=300, bbox_inches='tight')
    print("\n已保存算法对比图表: 算法对比.png")


if __name__ == "__main__":
    # LCS性能分析
    lcs_sizes, lcs_times, lcs_comparisons = analyze_lcs_performance()
    plot_lcs_performance(lcs_sizes, lcs_times, lcs_comparisons)
    
    # 0-1背包性能分析
    knap_sizes, knap_times, knap_comparisons = analyze_knapsack_performance()
    plot_knapsack_performance(knap_sizes, knap_times, knap_comparisons)
    
    # 算法对比
    compare_algorithms()
    
    print("\n" + "=" * 80)
    print("性能分析完成")
    print("=" * 80)

