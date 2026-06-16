"""
重新生成图表（英文版）
使用已有的训练数据，无需重新训练模型
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 设置英文显示
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")

results_dir = 'results'

print("正在读取实验数据...")

# 读取训练历史
with open(f'{results_dir}/bert-base-uncased_history.json', 'r') as f:
    bert_history = json.load(f)

with open(f'{results_dir}/roberta-base_history.json', 'r') as f:
    roberta_history = json.load(f)

# 读取实验总结
with open(f'{results_dir}/experiment_summary.json', 'r') as f:
    summary = json.load(f)

all_experiments = summary['all_results']

print("开始重新生成图表...")

# ==================== 实验1：BERT混淆矩阵 ====================
# 注：混淆矩阵数据不在JSON中，这个图保持原样
print("实验1混淆矩阵保持不变（需要原始预测数据）")

# ==================== 实验2：模型对比 ====================
print("\n生成实验2图表...")

# 2.1 训练曲线对比
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

histories = [bert_history, roberta_history]
model_names = ['BERT', 'RoBERTa']

# 训练损失
ax = axes[0, 0]
for history, name in zip(histories, model_names):
    epochs = range(1, len(history['train_loss']) + 1)
    ax.plot(epochs, history['train_loss'], marker='o', label=name, linewidth=2)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Loss', fontsize=12)
ax.set_title('Training Loss Comparison', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# 验证损失
ax = axes[0, 1]
for history, name in zip(histories, model_names):
    epochs = range(1, len(history['val_loss']) + 1)
    ax.plot(epochs, history['val_loss'], marker='s', label=name, linewidth=2)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Loss', fontsize=12)
ax.set_title('Validation Loss Comparison', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# 训练准确率
ax = axes[1, 0]
for history, name in zip(histories, model_names):
    epochs = range(1, len(history['train_acc']) + 1)
    ax.plot(epochs, history['train_acc'], marker='o', label=name, linewidth=2)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('Training Accuracy Comparison', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# 验证准确率
ax = axes[1, 1]
for history, name in zip(histories, model_names):
    epochs = range(1, len(history['val_acc']) + 1)
    ax.plot(epochs, history['val_acc'], marker='s', label=name, linewidth=2)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('Validation Accuracy Comparison', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{results_dir}/exp2_training_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ exp2_training_comparison.png")
plt.close()

# 2.2 模型性能对比
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

comparison_results = {
    'BERT': all_experiments['bert_baseline'],
    'RoBERTa': all_experiments['roberta_baseline']
}

model_names_list = list(comparison_results.keys())
metrics = ['accuracy', 'precision', 'recall', 'f1']

# 性能指标对比
ax = axes[0]
x = np.arange(len(model_names_list))
width = 0.2

for i, metric in enumerate(metrics):
    values = [comparison_results[name][metric] for name in model_names_list]
    ax.bar(x + i * width, values, width, label=metric.capitalize())

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Model Performance Metrics Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(model_names_list)
ax.legend()
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3, axis='y')

# 训练时间对比
ax = axes[1]
times = [comparison_results[name]['avg_epoch_time'] for name in model_names_list]
bars = ax.bar(model_names_list, times, color=sns.color_palette("husl", len(model_names_list)))

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}s',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Average Epoch Time (seconds)', fontsize=12)
ax.set_title('Training Speed Comparison', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{results_dir}/exp2_model_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ exp2_model_comparison.png")
plt.close()

# ==================== 实验3：数据增强对比 ====================
print("\n生成实验3图表...")

# 3.1 BERT数据增强对比
baseline_results = all_experiments['bert_baseline']
aug_results = all_experiments['bert_augmented']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

metrics = ['accuracy', 'precision', 'recall', 'f1']
baseline_values = [baseline_results[m] for m in metrics]
aug_values = [aug_results[m] for m in metrics]

# 性能对比
ax = axes[0]
x = np.arange(len(metrics))
width = 0.35

ax.bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.8)
ax.bar(x + width/2, aug_values, width, label='Augmented', alpha=0.8)

ax.set_xlabel('Metrics', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('BERT - Data Augmentation Effect', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([m.capitalize() for m in metrics])
ax.legend()
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3, axis='y')

# 性能提升百分比
ax = axes[1]
improvements = [(aug_values[i] - baseline_values[i]) / baseline_values[i] * 100 
               for i in range(len(metrics))]
colors = ['green' if imp > 0 else 'red' for imp in improvements]
bars = ax.bar([m.capitalize() for m in metrics], improvements, color=colors, alpha=0.7)

for bar, imp in zip(bars, improvements):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{imp:+.2f}%',
            ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('Metrics', fontsize=12)
ax.set_ylabel('Performance Improvement (%)', fontsize=12)
ax.set_title('BERT - Performance Gain from Augmentation', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{results_dir}/exp3_bert_augmentation_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ exp3_bert_augmentation_comparison.png")
plt.close()

# 3.2 RoBERTa数据增强对比
baseline_results = all_experiments['roberta_baseline']
aug_results = all_experiments['roberta_augmented']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

baseline_values = [baseline_results[m] for m in metrics]
aug_values = [aug_results[m] for m in metrics]

# 性能对比
ax = axes[0]
x = np.arange(len(metrics))
width = 0.35

ax.bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.8)
ax.bar(x + width/2, aug_values, width, label='Augmented', alpha=0.8)

ax.set_xlabel('Metrics', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('RoBERTa - Data Augmentation Effect', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([m.capitalize() for m in metrics])
ax.legend()
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3, axis='y')

# 性能提升百分比
ax = axes[1]
improvements = [(aug_values[i] - baseline_values[i]) / baseline_values[i] * 100 
               for i in range(len(metrics))]
colors = ['green' if imp > 0 else 'red' for imp in improvements]
bars = ax.bar([m.capitalize() for m in metrics], improvements, color=colors, alpha=0.7)

for bar, imp in zip(bars, improvements):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{imp:+.2f}%',
            ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('Metrics', fontsize=12)
ax.set_ylabel('Performance Improvement (%)', fontsize=12)
ax.set_title('RoBERTa - Performance Gain from Augmentation', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{results_dir}/exp3_roberta_augmentation_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ exp3_roberta_augmentation_comparison.png")
plt.close()

# 3.3 总体对比
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# 准确率对比
ax = axes[0]
models = ['BERT\n(Baseline)', 'BERT\n(Augmented)', 'RoBERTa\n(Baseline)', 'RoBERTa\n(Augmented)']
accuracies = [
    all_experiments['bert_baseline']['accuracy'],
    all_experiments['bert_augmented']['accuracy'],
    all_experiments['roberta_baseline']['accuracy'],
    all_experiments['roberta_augmented']['accuracy']
]
colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
bars = ax.bar(models, accuracies, color=colors, alpha=0.8)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('Overall Data Augmentation Effect - Accuracy', fontsize=14, fontweight='bold')
ax.set_ylim([min(accuracies) - 0.02, max(accuracies) + 0.02])
ax.grid(True, alpha=0.3, axis='y')

# F1分数对比
ax = axes[1]
f1_scores = [
    all_experiments['bert_baseline']['f1'],
    all_experiments['bert_augmented']['f1'],
    all_experiments['roberta_baseline']['f1'],
    all_experiments['roberta_augmented']['f1']
]
bars = ax.bar(models, f1_scores, color=colors, alpha=0.8)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('F1 Score', fontsize=12)
ax.set_title('Overall Data Augmentation Effect - F1 Score', fontsize=14, fontweight='bold')
ax.set_ylim([min(f1_scores) - 0.02, max(f1_scores) + 0.02])
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{results_dir}/exp3_overall_augmentation_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ exp3_overall_augmentation_comparison.png")
plt.close()

print("\n" + "="*60)
print("✅ 所有图表已重新生成（英文版）！")
print("="*60)
print("\n生成的图表：")
print("  实验2:")
print("    - exp2_training_comparison.png")
print("    - exp2_model_comparison.png")
print("  实验3:")
print("    - exp3_bert_augmentation_comparison.png")
print("    - exp3_roberta_augmentation_comparison.png")
print("    - exp3_overall_augmentation_comparison.png")
print("\n注：混淆矩阵需要原始预测数据，暂时保持不变")

