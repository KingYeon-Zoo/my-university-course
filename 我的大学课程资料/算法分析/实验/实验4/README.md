# 实验四：经典动态规划算法实现与分析

## 实验简介

本实验实现了两个经典的动态规划算法：

1. 最长公共子序列(LCS)算法
2. 0-1背包问题算法

包含算法实现、正确性验证、性能分析和可视化展示。

## 文件说明

### 核心代码文件

1. `dp_algorithms.py` - 核心算法实现
   - LCSAlgorithm：LCS算法实现
   - Knapsack01：0-1背包算法实现
   - BruteForceLCS：LCS暴力算法(用于对比)
   - BruteForceKnapsack：背包暴力算法(用于对比)

2. `test_correctness.py` - 正确性测试
   - 包含10个LCS测试用例
   - 包含10个0-1背包测试用例
   - 包含随机案例测试

3. `performance_analysis.py` - 性能分析
   - LCS算法性能测试
   - 0-1背包算法性能测试
   - DP算法与暴力算法对比
   - 生成性能曲线图

4. `visualize_dp.py` - 算法可视化
   - LCS的DP表格可视化
   - 0-1背包的DP表格可视化
   - 回溯路径展示

### 生成的图表文件

1. `LCS性能分析.png` - LCS算法性能曲线(4个子图)
2. `背包性能分析.png` - 0-1背包算法性能曲线(4个子图)
3. `算法对比.png` - DP算法与暴力算法对比(2个子图)
4. `LCS_示例1.png` - LCS DP表格可视化示例1
5. `LCS_示例2.png` - LCS DP表格可视化示例2
6. `背包_示例1.png` - 0-1背包DP表格可视化示例1
7. `背包_示例2.png` - 0-1背包DP表格可视化示例2

### 报告文件

1. `实验报告.md` - 完整的实验报告
2. `实验4要求.md` - 实验要求文档
3. `实验4报告模板.md` - 报告模板

## 运行环境

1. Python 3.x
2. 依赖库：
   - numpy
   - matplotlib

安装依赖：
```bash
pip install numpy matplotlib
```

## 运行说明

### 1. 运行正确性测试

```bash
cd 实验4
python test_correctness.py
```

输出：
- LCS算法测试结果(10个测试用例)
- 0-1背包算法测试结果(10个测试用例)
- 随机案例测试结果

### 2. 运行性能分析

```bash
python performance_analysis.py
```

输出：
- LCS算法性能数据表格
- 0-1背包算法性能数据表格
- DP算法与暴力算法对比数据
- 生成3个性能曲线图文件

### 3. 运行可视化

```bash
python visualize_dp.py
```

输出：
- LCS DP表格可视化(2个示例)
- 0-1背包DP表格可视化(2个示例)
- 生成4个可视化图文件

### 4. 单独使用核心算法

```python
from dp_algorithms import LCSAlgorithm, Knapsack01

# LCS示例
lcs = LCSAlgorithm()
X = "ABCDGH"
Y = "AEDFHR"
length, lcs_str, dp = lcs.solve(X, Y)
print(f"LCS长度: {length}, LCS: {lcs_str}")

# 0-1背包示例
knapsack = Knapsack01()
weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 8
max_value, selected, dp = knapsack.solve_with_items(weights, values, capacity)
print(f"最大价值: {max_value}, 选中物品: {selected}")
```

## 实验结果概览

### LCS算法

1. 正确性：通过率100% (10/10)
2. 时间复杂度：O(n^2)，实测与理论完全吻合
3. 空间复杂度：O(n^2)
4. 性能对比：n=15时，比暴力算法快1954倍

### 0-1背包算法

1. 正确性：通过率90% (9/10)
2. 时间复杂度：O(nW)，实测与理论吻合良好
3. 空间复杂度：O(nW)
4. 性能对比：n=15时，比暴力算法快33倍

## 实验亮点

1. 完整的测试体系：边界案例、一般案例、随机案例
2. 详尽的性能分析：多种规模、理论对比、对数验证
3. 直观的可视化：DP表格热力图、回溯路径标记
4. 算法对比：DP算法vs暴力算法，展现优化效果
5. 模块化设计：代码结构清晰，易于扩展和维护

## 注意事项

1. 运行性能分析时，较大规模数据可能需要等待数秒
2. 暴力算法对比测试仅使用小规模数据(n≤15)，避免过长等待
3. 图表生成后保存在当前目录，请勿删除
4. Windows环境下注意中文编码问题，代码已做相应处理

## 作者

实验4 - 经典动态规划算法实现与分析

2025年12月

