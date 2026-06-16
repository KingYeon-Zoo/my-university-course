#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分支预测实验结果可视化分析
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False
rcParams['font.size'] = 10

# 读取数据
df = pd.read_csv('new_output.txt')

# 数据预处理
predictors_order = ['taken_always', 'nottaken_always', 'bimod_512', 'bimod_1024', 
                    '2lev_1_64_6_1', '2lev_1_1024_8_0']
predictor_labels = {
    'taken_always': 'Always Taken',
    'nottaken_always': 'Always Not Taken',
    'bimod_512': 'Bimod(512)',
    'bimod_1024': 'Bimod(1024)',
    '2lev_1_64_6_1': '2-Level(1,64,6,1)',
    '2lev_1_1024_8_0': '2-Level(1,1024,8,0)'
}

# 创建图表
fig = plt.figure(figsize=(16, 10))

# 1. 准确率对比柱状图（按程序分组）
ax1 = plt.subplot(2, 3, 1)
benchmarks = ['bzip2', 'gcc', 'mcf']
x = np.arange(len(predictors_order))
width = 0.25

for i, bench in enumerate(benchmarks):
    bench_data = df[df['Benchmark'] == bench]
    accuracies = [bench_data[bench_data['Predictor'] == p]['Accuracy'].values[0] * 100 
                  for p in predictors_order]
    ax1.bar(x + i*width, accuracies, width, label=bench, alpha=0.8)

ax1.set_xlabel('预测器类型')
ax1.set_ylabel('准确率 (%)')
ax1.set_title('不同预测器在各程序上的准确率对比')
ax1.set_xticks(x + width)
ax1.set_xticklabels([predictor_labels[p] for p in predictors_order], rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 2. 错误率对比柱状图
ax2 = plt.subplot(2, 3, 2)
for i, bench in enumerate(benchmarks):
    bench_data = df[df['Benchmark'] == bench]
    miss_rates = [bench_data[bench_data['Predictor'] == p]['MissRate'].values[0] * 100 
                  for p in predictors_order]
    ax2.bar(x + i*width, miss_rates, width, label=bench, alpha=0.8)

ax2.set_xlabel('预测器类型')
ax2.set_ylabel('错误率 (%)')
ax2.set_title('不同预测器在各程序上的错误率对比')
ax2.set_xticks(x + width)
ax2.set_xticklabels([predictor_labels[p] for p in predictors_order], rotation=45, ha='right')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# 3. 各程序的准确率折线图
ax3 = plt.subplot(2, 3, 3)
for bench in benchmarks:
    bench_data = df[df['Benchmark'] == bench]
    accuracies = [bench_data[bench_data['Predictor'] == p]['Accuracy'].values[0] * 100 
                  for p in predictors_order]
    ax3.plot(range(len(predictors_order)), accuracies, marker='o', label=bench, linewidth=2)

ax3.set_xlabel('预测器类型')
ax3.set_ylabel('准确率 (%)')
ax3.set_title('各程序在不同预测器下的准确率趋势')
ax3.set_xticks(range(len(predictors_order)))
ax3.set_xticklabels([predictor_labels[p] for p in predictors_order], rotation=45, ha='right')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. 错误预测数对比（对数坐标）
ax4 = plt.subplot(2, 3, 4)
for i, bench in enumerate(benchmarks):
    bench_data = df[df['Benchmark'] == bench]
    mispreds = [bench_data[bench_data['Predictor'] == p]['Mispredictions'].values[0] 
                for p in predictors_order]
    ax4.bar(x + i*width, mispreds, width, label=bench, alpha=0.8)

ax4.set_xlabel('预测器类型')
ax4.set_ylabel('错误预测次数')
ax4.set_title('不同预测器的错误预测次数对比')
ax4.set_xticks(x + width)
ax4.set_xticklabels([predictor_labels[p] for p in predictors_order], rotation=45, ha='right')
ax4.set_yscale('log')
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

# 5. 各预测器的平均准确率
ax5 = plt.subplot(2, 3, 5)
avg_accuracies = []
for p in predictors_order:
    pred_data = df[df['Predictor'] == p]
    avg_acc = pred_data['Accuracy'].mean() * 100
    avg_accuracies.append(avg_acc)

colors = plt.cm.viridis(np.linspace(0, 1, len(predictors_order)))
bars = ax5.bar(range(len(predictors_order)), avg_accuracies, color=colors, alpha=0.8)
ax5.set_xlabel('预测器类型')
ax5.set_ylabel('平均准确率 (%)')
ax5.set_title('各预测器在所有程序上的平均准确率')
ax5.set_xticks(range(len(predictors_order)))
ax5.set_xticklabels([predictor_labels[p] for p in predictors_order], rotation=45, ha='right')
ax5.grid(axis='y', alpha=0.3)

# 在柱状图上添加数值标签
for bar in bars:
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}%', ha='center', va='bottom', fontsize=9)

# 6. 热力图：准确率矩阵
ax6 = plt.subplot(2, 3, 6)
accuracy_matrix = np.zeros((len(benchmarks), len(predictors_order)))
for i, bench in enumerate(benchmarks):
    for j, pred in enumerate(predictors_order):
        acc = df[(df['Benchmark'] == bench) & (df['Predictor'] == pred)]['Accuracy'].values[0]
        accuracy_matrix[i, j] = acc * 100

im = ax6.imshow(accuracy_matrix, cmap='YlGn', aspect='auto', vmin=0, vmax=100)
ax6.set_xticks(range(len(predictors_order)))
ax6.set_yticks(range(len(benchmarks)))
ax6.set_xticklabels([predictor_labels[p] for p in predictors_order], rotation=45, ha='right')
ax6.set_yticklabels(benchmarks)
ax6.set_title('准确率热力图 (%)')

# 添加数值标签
for i in range(len(benchmarks)):
    for j in range(len(predictors_order)):
        text = ax6.text(j, i, f'{accuracy_matrix[i, j]:.1f}',
                       ha="center", va="center", color="black", fontsize=8)

plt.colorbar(im, ax=ax6, label='准确率 (%)')

plt.tight_layout()
plt.savefig('experiment_analysis.png', dpi=300, bbox_inches='tight')
print("图表已保存为 experiment_analysis.png")

# 创建详细的准确率表格图
fig2, ax = plt.subplots(figsize=(12, 4))
ax.axis('tight')
ax.axis('off')

# 准备表格数据
table_data = []
header = ['程序'] + [predictor_labels[p] for p in predictors_order]
table_data.append(header)

for bench in benchmarks:
    row = [bench]
    for pred in predictors_order:
        acc = df[(df['Benchmark'] == bench) & (df['Predictor'] == pred)]['Accuracy'].values[0]
        row.append(f'{acc*100:.2f}%')
    table_data.append(row)

# 添加平均值行
avg_row = ['平均']
for pred in predictors_order:
    avg_acc = df[df['Predictor'] == pred]['Accuracy'].mean()
    avg_row.append(f'{avg_acc*100:.2f}%')
table_data.append(avg_row)

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.1] + [0.15]*len(predictors_order))
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# 设置表头样式
for i in range(len(header)):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置平均值行样式
for i in range(len(avg_row)):
    table[(len(table_data)-1, i)].set_facecolor('#E8F5E9')
    table[(len(table_data)-1, i)].set_text_props(weight='bold')

plt.title('分支预测准确率统计表', fontsize=14, weight='bold', pad=20)
plt.savefig('accuracy_table.png', dpi=300, bbox_inches='tight')
print("表格已保存为 accuracy_table.png")

# 打印统计分析
print("\n=== 实验结果统计分析 ===\n")
for bench in benchmarks:
    print(f"程序 {bench}:")
    bench_data = df[df['Benchmark'] == bench].sort_values('Accuracy', ascending=False)
    print(f"  最佳预测器: {predictor_labels[bench_data.iloc[0]['Predictor']]} "
          f"(准确率: {bench_data.iloc[0]['Accuracy']*100:.2f}%)")
    print(f"  最差预测器: {predictor_labels[bench_data.iloc[-1]['Predictor']]} "
          f"(准确率: {bench_data.iloc[-1]['Accuracy']*100:.2f}%)")
    print(f"  准确率提升: {(bench_data.iloc[0]['Accuracy'] - bench_data.iloc[-1]['Accuracy'])*100:.2f}%\n")

print("总体最佳预测器排名:")
avg_perf = df.groupby('Predictor')['Accuracy'].mean().sort_values(ascending=False)
for i, (pred, acc) in enumerate(avg_perf.items(), 1):
    print(f"  {i}. {predictor_labels[pred]}: {acc*100:.2f}%")

plt.show()
