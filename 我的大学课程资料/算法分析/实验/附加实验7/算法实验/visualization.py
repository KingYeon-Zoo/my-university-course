"""
可视化模块
生成训练过程和模型对比的可视化图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix
import json
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def plot_training_history(histories, model_names, save_path='results/training_history.png'):
    """
    绘制训练历史曲线
    
    Args:
        histories: 训练历史字典列表
        model_names: 模型名称列表
        save_path: 保存路径
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 训练损失
    ax = axes[0, 0]
    for history, name in zip(histories, model_names):
        epochs = range(1, len(history['train_loss']) + 1)
        ax.plot(epochs, history['train_loss'], marker='o', label=name)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('训练损失对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 验证损失
    ax = axes[0, 1]
    for history, name in zip(histories, model_names):
        epochs = range(1, len(history['val_loss']) + 1)
        ax.plot(epochs, history['val_loss'], marker='s', label=name)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('验证损失对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 训练准确率
    ax = axes[1, 0]
    for history, name in zip(histories, model_names):
        epochs = range(1, len(history['train_acc']) + 1)
        ax.plot(epochs, history['train_acc'], marker='o', label=name)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('训练准确率对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 验证准确率
    ax = axes[1, 1]
    for history, name in zip(histories, model_names):
        epochs = range(1, len(history['val_acc']) + 1)
        ax.plot(epochs, history['val_acc'], marker='s', label=name)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('验证准确率对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"训练历史图表已保存至: {save_path}")
    plt.close()


def plot_model_comparison(results_dict, save_path='results/model_comparison.png'):
    """
    绘制模型性能对比图
    
    Args:
        results_dict: 结果字典 {model_name: results}
        save_path: 保存路径
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    model_names = list(results_dict.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    
    # 性能指标对比
    ax = axes[0]
    x = np.arange(len(model_names))
    width = 0.2
    
    for i, metric in enumerate(metrics):
        values = [results_dict[name][metric] for name in model_names]
        ax.bar(x + i * width, values, width, label=metric.capitalize())
    
    ax.set_xlabel('模型', fontsize=12)
    ax.set_ylabel('分数', fontsize=12)
    ax.set_title('模型性能指标对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, rotation=15, ha='right')
    ax.legend()
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3, axis='y')
    
    # 训练时间对比
    ax = axes[1]
    times = [results_dict[name]['avg_epoch_time'] for name in model_names]
    bars = ax.bar(model_names, times, color=sns.color_palette("husl", len(model_names)))
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}s',
                ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('模型', fontsize=12)
    ax.set_ylabel('平均Epoch时间 (秒)', fontsize=12)
    ax.set_title('训练速度对比', fontsize=14, fontweight='bold')
    ax.set_xticklabels(model_names, rotation=15, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"模型对比图表已保存至: {save_path}")
    plt.close()


def plot_confusion_matrix(y_true, y_pred, model_name, save_path='results/confusion_matrix.png'):
    """
    绘制混淆矩阵
    
    Args:
        y_true: 真实标签
        y_pred: 预测标签
        model_name: 模型名称
        save_path: 保存路径
    """
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Negative', 'Positive'],
                yticklabels=['Negative', 'Positive'])
    plt.xlabel('预测标签', fontsize=12)
    plt.ylabel('真实标签', fontsize=12)
    plt.title(f'{model_name} - 混淆矩阵', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"混淆矩阵已保存至: {save_path}")
    plt.close()


def plot_data_augmentation_comparison(baseline_results, aug_results, 
                                      save_path='results/augmentation_comparison.png'):
    """
    绘制数据增强效果对比
    
    Args:
        baseline_results: 基线结果
        aug_results: 数据增强后结果
        save_path: 保存路径
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    baseline_values = [baseline_results[m] for m in metrics]
    aug_values = [aug_results[m] for m in metrics]
    
    # 性能对比
    ax = axes[0]
    x = np.arange(len(metrics))
    width = 0.35
    
    ax.bar(x - width/2, baseline_values, width, label='无数据增强', alpha=0.8)
    ax.bar(x + width/2, aug_values, width, label='数据增强', alpha=0.8)
    
    ax.set_xlabel('评估指标', fontsize=12)
    ax.set_ylabel('分数', fontsize=12)
    ax.set_title('数据增强效果对比', fontsize=14, fontweight='bold')
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
    bars = ax.bar(metrics, improvements, color=colors, alpha=0.7)
    
    # 添加数值标签
    for bar, imp in zip(bars, improvements):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{imp:+.2f}%',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlabel('评估指标', fontsize=12)
    ax.set_ylabel('性能提升 (%)', fontsize=12)
    ax.set_title('数据增强带来的性能提升', fontsize=14, fontweight='bold')
    ax.set_xticklabels([m.capitalize() for m in metrics])
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"数据增强对比图表已保存至: {save_path}")
    plt.close()


def generate_all_plots(results_dir='results'):
    """
    生成所有可视化图表
    
    Args:
        results_dir: 结果目录
    """
    # 读取所有结果文件
    history_files = [f for f in os.listdir(results_dir) if f.endswith('_history.json')]
    result_files = [f for f in os.listdir(results_dir) if f.endswith('_results.json') 
                   and not f.endswith('_history.json')]
    
    # 加载历史和结果
    histories = []
    model_names = []
    results_dict = {}
    
    for hist_file, res_file in zip(sorted(history_files), sorted(result_files)):
        model_name = hist_file.replace('_history.json', '')
        
        with open(os.path.join(results_dir, hist_file), 'r') as f:
            histories.append(json.load(f))
        
        with open(os.path.join(results_dir, res_file), 'r') as f:
            results_dict[model_name] = json.load(f)
        
        model_names.append(model_name)
    
    # 生成图表
    if histories and model_names:
        plot_training_history(histories, model_names, 
                            os.path.join(results_dir, 'training_history.png'))
        plot_model_comparison(results_dict, 
                            os.path.join(results_dir, 'model_comparison.png'))
    
    print("所有可视化图表生成完成！")

