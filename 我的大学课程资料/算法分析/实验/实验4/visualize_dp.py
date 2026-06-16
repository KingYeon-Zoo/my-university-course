"""
动态规划过程可视化
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, FancyArrowPatch
from dp_algorithms import LCSAlgorithm, Knapsack01

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
rcParams['axes.unicode_minus'] = False


def visualize_lcs_dp_table(X, Y, save_path='LCS_DP表格可视化.png'):
    """可视化LCS的DP表格填充过程"""
    lcs = LCSAlgorithm()
    length, lcs_str, dp = lcs.solve(X, Y)
    
    m, n = len(X), len(Y)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(max(12, n+2), max(10, m+2)))
    
    # 绘制表格
    for i in range(m + 2):
        for j in range(n + 2):
            # 确定单元格的值和颜色
            if i == 0 and j == 0:
                # 左上角空白
                value = ''
                color = 'lightgray'
            elif i == 0 and j == 1:
                # 第一行第二列空白
                value = ''
                color = 'lightgray'
            elif i == 1 and j == 0:
                # 第二行第一列空白
                value = ''
                color = 'lightgray'
            elif i == 0 and j > 1:
                # Y序列的字符
                value = Y[j-2]
                color = 'lightyellow'
            elif i > 1 and j == 0:
                # X序列的字符
                value = X[i-2]
                color = 'lightyellow'
            elif i == 1 or j == 1:
                # 第一行和第一列的0
                value = '0'
                color = 'lightblue'
            else:
                # DP表格的值
                dp_i, dp_j = i - 1, j - 1
                value = str(dp[dp_i][dp_j])
                
                # 根据值的大小设置颜色深度
                max_val = dp[m][n]
                if max_val > 0:
                    intensity = dp[dp_i][dp_j] / max_val
                    color = plt.cm.Blues(0.3 + 0.6 * intensity)
                else:
                    color = 'white'
            
            # 绘制单元格
            rect = Rectangle((j, m+1-i), 1, 1, 
                           facecolor=color, 
                           edgecolor='black', 
                           linewidth=1.5)
            ax.add_patch(rect)
            
            # 添加文本
            ax.text(j+0.5, m+1.5-i, str(value), 
                   ha='center', va='center', 
                   fontsize=14, fontweight='bold')
    
    # 回溯路径
    i, j = m, n
    path_cells = []
    while i > 0 and j > 0:
        path_cells.append((i, j))
        if X[i-1] == Y[j-1]:
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    # 高亮路径
    for pi, pj in path_cells:
        rect = Rectangle((pj+1, m+1-(pi+1)), 1, 1, 
                       facecolor='none', 
                       edgecolor='red', 
                       linewidth=3)
        ax.add_patch(rect)
    
    ax.set_xlim(0, n+2)
    ax.set_ylim(0, m+2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加标题和说明
    title = f'LCS动态规划表格可视化\nX = "{X}"  Y = "{Y}"\nLCS长度 = {length}  LCS = "{lcs_str}"'
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 添加图例
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='lightyellow', markersize=15, label='序列字符'),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='lightblue', markersize=15, label='初始值(0)'),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor=plt.cm.Blues(0.9), markersize=15, label='DP值(深色=较大)'),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='none', markeredgecolor='red', 
                  markersize=15, markeredgewidth=3, label='回溯路径')
    ]
    ax.legend(handles=legend_elements, loc='upper left', 
             bbox_to_anchor=(1.02, 1), fontsize=12)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"已保存LCS DP表格可视化: {save_path}")
    
    return dp


def visualize_knapsack_dp_table(weights, values, capacity, 
                                save_path='背包_DP表格可视化.png'):
    """可视化0-1背包的DP表格"""
    knapsack = Knapsack01()
    max_value, dp = knapsack.solve(weights, values, capacity)
    selected = knapsack.get_selected_items(weights, values, capacity, dp)
    
    n = len(weights)
    
    # 只显示部分容量以保证可视化清晰
    display_capacity = min(capacity, 30)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(max(14, display_capacity+3), max(10, n+3)))
    
    # 绘制表格
    for i in range(n + 2):
        for w in range(display_capacity + 2):
            # 确定单元格的值和颜色
            if i == 0 and w == 0:
                value = '物品\\容量'
                color = 'lightgray'
            elif i == 0 and w > 0:
                # 容量标签
                value = str(w-1) if w > 0 else ''
                color = 'lightyellow'
            elif i > 0 and w == 0:
                # 物品标签
                if i == 1:
                    value = '0'
                else:
                    value = f'{i-1}\nw={weights[i-2]}\nv={values[i-2]}'
                color = 'lightyellow'
            else:
                # DP表格的值
                dp_i, dp_w = i - 1, w - 1
                value = str(dp[dp_i][dp_w])
                
                # 根据值的大小设置颜色深度
                max_val = max_value
                if max_val > 0:
                    intensity = dp[dp_i][dp_w] / max_val
                    color = plt.cm.Greens(0.2 + 0.7 * intensity)
                else:
                    color = 'white'
            
            # 绘制单元格
            rect = Rectangle((w, n+1-i), 1, 1, 
                           facecolor=color, 
                           edgecolor='black', 
                           linewidth=1)
            ax.add_patch(rect)
            
            # 添加文本
            fontsize = 10 if i > 0 and w == 0 else 12
            ax.text(w+0.5, n+1.5-i, str(value), 
                   ha='center', va='center', 
                   fontsize=fontsize, fontweight='bold')
    
    # 高亮选中的物品
    for item_idx in selected:
        i = item_idx + 2  # 转换为表格中的行号
        rect = Rectangle((0, n+1-i), display_capacity+2, 1, 
                       facecolor='none', 
                       edgecolor='red', 
                       linewidth=3)
        ax.add_patch(rect)
    
    ax.set_xlim(0, display_capacity+2)
    ax.set_ylim(0, n+2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加标题和说明
    selected_info = f"选中物品: {selected}\n"
    selected_info += f"总重量: {sum(weights[i] for i in selected)}  "
    selected_info += f"总价值: {sum(values[i] for i in selected)}"
    
    title = f'0-1背包动态规划表格可视化\n背包容量 = {capacity}  最大价值 = {max_value}\n{selected_info}'
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 添加图例
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='lightyellow', markersize=15, label='物品/容量标签'),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor=plt.cm.Greens(0.9), markersize=15, label='DP值(深色=较大)'),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='none', markeredgecolor='red', 
                  markersize=15, markeredgewidth=3, label='选中的物品')
    ]
    ax.legend(handles=legend_elements, loc='upper left', 
             bbox_to_anchor=(1.02, 1), fontsize=12)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"已保存0-1背包DP表格可视化: {save_path}")
    
    return dp


def visualize_lcs_process():
    """可视化LCS算法的执行过程"""
    print("=" * 80)
    print("LCS算法过程可视化")
    print("=" * 80)
    
    # 示例1: 简单案例
    X1, Y1 = "ABCDGH", "AEDFHR"
    print(f"\n示例1: X = {X1}, Y = {Y1}")
    dp1 = visualize_lcs_dp_table(X1, Y1, 'LCS_示例1.png')
    
    # 示例2: 较复杂案例
    X2, Y2 = "AGGTAB", "GXTXAYB"
    print(f"\n示例2: X = {X2}, Y = {Y2}")
    dp2 = visualize_lcs_dp_table(X2, Y2, 'LCS_示例2.png')


def visualize_knapsack_process():
    """可视化0-1背包算法的执行过程"""
    print("\n" + "=" * 80)
    print("0-1背包算法过程可视化")
    print("=" * 80)
    
    # 示例1: 简单案例
    weights1 = [2, 3, 4, 5]
    values1 = [3, 4, 5, 6]
    capacity1 = 8
    print(f"\n示例1: 物品数={len(weights1)}, 容量={capacity1}")
    print(f"重量: {weights1}")
    print(f"价值: {values1}")
    dp1 = visualize_knapsack_dp_table(weights1, values1, capacity1, '背包_示例1.png')
    
    # 示例2: 较复杂案例
    weights2 = [1, 2, 3, 4, 5, 6]
    values2 = [10, 5, 15, 7, 6, 18]
    capacity2 = 15
    print(f"\n示例2: 物品数={len(weights2)}, 容量={capacity2}")
    print(f"重量: {weights2}")
    print(f"价值: {values2}")
    dp2 = visualize_knapsack_dp_table(weights2, values2, capacity2, '背包_示例2.png')


if __name__ == "__main__":
    # 可视化LCS过程
    visualize_lcs_process()
    
    # 可视化0-1背包过程
    visualize_knapsack_process()
    
    print("\n" + "=" * 80)
    print("可视化完成")
    print("=" * 80)

