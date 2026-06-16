"""
主程序
按照实验要求执行三个实验：
1. BERT基础实现
2. BERT vs RoBERTa模型对比
3. 数据增强效果对比（在两个模型上）
"""

import torch
import argparse
import os
import json
import numpy as np
from transformers import AutoTokenizer

from data_loader import load_imdb_data, create_data_loaders
from data_augmentation import DataAugmenter
from train import train_model
from visualization import (plot_training_history, plot_model_comparison, 
                          plot_confusion_matrix, plot_data_augmentation_comparison)


def set_seed(seed=42):
    """设置随机种子"""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    import random
    random.seed(seed)


def main(args):
    """主函数"""
    
    # 设置随机种子
    set_seed(args.seed)
    
    # 创建结果目录
    os.makedirs(args.results_dir, exist_ok=True)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 存储所有实验结果
    all_experiments = {}
    
    # ==================== 实验1：BERT基础实现 ====================
    print("\n" + "="*80)
    print("实验1：BERT情感分析基础实现")
    print("="*80)
    
    model_name = 'bert-base-uncased'
    print(f"\n训练模型: {model_name}")
    
    # 加载数据
    print("\n1. 加载数据集...")
    train_texts, val_texts, train_labels, val_labels = load_imdb_data(
        args.data_path, 
        test_size=0.2, 
        random_state=args.seed
    )
    
    # 创建数据加载器
    print(f"\n2. 创建tokenizer和数据加载器...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_loader, val_loader = create_data_loaders(
        train_texts, val_texts, train_labels, val_labels,
        tokenizer, 
        batch_size=args.batch_size,
        max_length=args.max_length
    )
    
    # 训练BERT
    print(f"\n3. 开始训练BERT...")
    bert_history, bert_results = train_model(
        model_name=model_name,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        save_dir=args.results_dir
    )
    
    # 保存BERT结果
    all_experiments['bert_baseline'] = {
        'model': 'bert-base-uncased',
        'accuracy': bert_results['accuracy'],
        'precision': bert_results['precision'],
        'recall': bert_results['recall'],
        'f1': bert_results['f1'],
        'avg_epoch_time': np.mean(bert_history['epoch_times'])
    }
    
    # 绘制BERT混淆矩阵
    plot_confusion_matrix(
        bert_results['true_labels'],
        bert_results['predictions'],
        'BERT-base',
        save_path=f"{args.results_dir}/exp1_bert_confusion_matrix.png"
    )
    
    print(f"\n实验1完成！")
    print(f"BERT准确率: {bert_results['accuracy']:.4f}")
    print(f"BERT F1分数: {bert_results['f1']:.4f}")
    
    # ==================== 实验2：BERT vs RoBERTa模型对比 ====================
    print("\n" + "="*80)
    print("实验2：不同预训练模型对比（BERT vs RoBERTa）")
    print("="*80)
    
    # 训练RoBERTa
    roberta_name = 'roberta-base'
    print(f"\n训练模型: {roberta_name}")
    
    # 创建RoBERTa的数据加载器
    print(f"\n1. 创建RoBERTa的tokenizer和数据加载器...")
    roberta_tokenizer = AutoTokenizer.from_pretrained(roberta_name)
    roberta_train_loader, roberta_val_loader = create_data_loaders(
        train_texts, val_texts, train_labels, val_labels,
        roberta_tokenizer, 
        batch_size=args.batch_size,
        max_length=args.max_length
    )
    
    # 训练RoBERTa
    print(f"\n2. 开始训练RoBERTa...")
    roberta_history, roberta_results = train_model(
        model_name=roberta_name,
        train_loader=roberta_train_loader,
        val_loader=roberta_val_loader,
        device=device,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        save_dir=args.results_dir
    )
    
    # 保存RoBERTa结果
    all_experiments['roberta_baseline'] = {
        'model': 'roberta-base',
        'accuracy': roberta_results['accuracy'],
        'precision': roberta_results['precision'],
        'recall': roberta_results['recall'],
        'f1': roberta_results['f1'],
        'avg_epoch_time': np.mean(roberta_history['epoch_times'])
    }
    
    # 绘制RoBERTa混淆矩阵
    plot_confusion_matrix(
        roberta_results['true_labels'],
        roberta_results['predictions'],
        'RoBERTa-base',
        save_path=f"{args.results_dir}/exp2_roberta_confusion_matrix.png"
    )
    
    # 生成模型对比图表
    print("\n3. 生成模型对比可视化...")
    
    # 训练曲线对比
    plot_training_history(
        [bert_history, roberta_history],
        ['BERT', 'RoBERTa'],
        save_path=f"{args.results_dir}/exp2_training_comparison.png"
    )
    
    # 性能指标对比
    comparison_results = {
        'BERT': all_experiments['bert_baseline'],
        'RoBERTa': all_experiments['roberta_baseline']
    }
    plot_model_comparison(
        comparison_results,
        save_path=f"{args.results_dir}/exp2_model_comparison.png"
    )
    
    print(f"\n实验2完成！")
    print(f"BERT准确率: {bert_results['accuracy']:.4f}, 平均训练时间: {all_experiments['bert_baseline']['avg_epoch_time']:.2f}秒/epoch")
    print(f"RoBERTa准确率: {roberta_results['accuracy']:.4f}, 平均训练时间: {all_experiments['roberta_baseline']['avg_epoch_time']:.2f}秒/epoch")
    
    # ==================== 实验3：数据增强对比 ====================
    print("\n" + "="*80)
    print("实验3：数据增强效果对比")
    print("="*80)
    
    print(f"\n将在BERT和RoBERTa上都应用数据增强方法: {args.aug_type}")
    
    # 应用数据增强
    print(f"\n1. 应用数据增强...")
    augmenter = DataAugmenter(aug_type=args.aug_type)
    aug_train_texts, aug_train_labels = augmenter.augment_data(
        train_texts, 
        train_labels, 
        aug_ratio=args.aug_ratio,
        num_aug=1
    )
    
    # --- 在BERT上测试数据增强 ---
    print(f"\n2. 使用增强数据训练BERT...")
    
    bert_aug_train_loader, bert_aug_val_loader = create_data_loaders(
        aug_train_texts, val_texts, aug_train_labels, val_labels,
        tokenizer,  # 使用之前的BERT tokenizer
        batch_size=args.batch_size,
        max_length=args.max_length
    )
    
    bert_aug_history, bert_aug_results = train_model(
        model_name='bert-base-uncased',
        train_loader=bert_aug_train_loader,
        val_loader=bert_aug_val_loader,
        device=device,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        save_dir=args.results_dir
    )
    
    # 保存BERT增强结果
    all_experiments['bert_augmented'] = {
        'model': 'bert-base-uncased (augmented)',
        'accuracy': bert_aug_results['accuracy'],
        'precision': bert_aug_results['precision'],
        'recall': bert_aug_results['recall'],
        'f1': bert_aug_results['f1'],
        'avg_epoch_time': np.mean(bert_aug_history['epoch_times'])
    }
    
    # 绘制BERT数据增强对比
    plot_data_augmentation_comparison(
        all_experiments['bert_baseline'],
        all_experiments['bert_augmented'],
        save_path=f"{args.results_dir}/exp3_bert_augmentation_comparison.png"
    )
    
    # 绘制BERT增强后的混淆矩阵
    plot_confusion_matrix(
        bert_aug_results['true_labels'],
        bert_aug_results['predictions'],
        'BERT (增强)',
        save_path=f"{args.results_dir}/exp3_bert_augmented_confusion_matrix.png"
    )
    
    print(f"\nBERT数据增强结果：")
    print(f"  基线准确率: {all_experiments['bert_baseline']['accuracy']:.4f}")
    print(f"  增强后准确率: {all_experiments['bert_augmented']['accuracy']:.4f}")
    print(f"  性能提升: {(all_experiments['bert_augmented']['accuracy'] - all_experiments['bert_baseline']['accuracy']) * 100:+.2f}%")
    
    # --- 在RoBERTa上测试数据增强 ---
    print(f"\n3. 使用增强数据训练RoBERTa...")
    
    roberta_aug_train_loader, roberta_aug_val_loader = create_data_loaders(
        aug_train_texts, val_texts, aug_train_labels, val_labels,
        roberta_tokenizer,  # 使用之前的RoBERTa tokenizer
        batch_size=args.batch_size,
        max_length=args.max_length
    )
    
    roberta_aug_history, roberta_aug_results = train_model(
        model_name='roberta-base',
        train_loader=roberta_aug_train_loader,
        val_loader=roberta_aug_val_loader,
        device=device,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        save_dir=args.results_dir
    )
    
    # 保存RoBERTa增强结果
    all_experiments['roberta_augmented'] = {
        'model': 'roberta-base (augmented)',
        'accuracy': roberta_aug_results['accuracy'],
        'precision': roberta_aug_results['precision'],
        'recall': roberta_aug_results['recall'],
        'f1': roberta_aug_results['f1'],
        'avg_epoch_time': np.mean(roberta_aug_history['epoch_times'])
    }
    
    # 绘制RoBERTa数据增强对比
    plot_data_augmentation_comparison(
        all_experiments['roberta_baseline'],
        all_experiments['roberta_augmented'],
        save_path=f"{args.results_dir}/exp3_roberta_augmentation_comparison.png"
    )
    
    # 绘制RoBERTa增强后的混淆矩阵
    plot_confusion_matrix(
        roberta_aug_results['true_labels'],
        roberta_aug_results['predictions'],
        'RoBERTa (增强)',
        save_path=f"{args.results_dir}/exp3_roberta_augmented_confusion_matrix.png"
    )
    
    print(f"\nRoBERTa数据增强结果：")
    print(f"  基线准确率: {all_experiments['roberta_baseline']['accuracy']:.4f}")
    print(f"  增强后准确率: {all_experiments['roberta_augmented']['accuracy']:.4f}")
    print(f"  性能提升: {(all_experiments['roberta_augmented']['accuracy'] - all_experiments['roberta_baseline']['accuracy']) * 100:+.2f}%")
    
    # 生成数据增强总体对比图（BERT和RoBERTa都包含）
    print("\n4. 生成数据增强总体对比图...")
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # 左图：准确率对比
    ax = axes[0]
    models = ['BERT\n(基线)', 'BERT\n(增强)', 'RoBERTa\n(基线)', 'RoBERTa\n(增强)']
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
    
    ax.set_ylabel('准确率', fontsize=12)
    ax.set_title('数据增强效果总体对比 - 准确率', fontsize=14, fontweight='bold')
    ax.set_ylim([min(accuracies) - 0.02, max(accuracies) + 0.02])
    ax.grid(True, alpha=0.3, axis='y')
    
    # 右图：F1分数对比
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
    
    ax.set_ylabel('F1分数', fontsize=12)
    ax.set_title('数据增强效果总体对比 - F1分数', fontsize=14, fontweight='bold')
    ax.set_ylim([min(f1_scores) - 0.02, max(f1_scores) + 0.02])
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f"{args.results_dir}/exp3_overall_augmentation_comparison.png", dpi=300, bbox_inches='tight')
    print(f"总体对比图已保存至: {args.results_dir}/exp3_overall_augmentation_comparison.png")
    plt.close()
    
    print(f"\n实验3完成！")
    
    # ==================== 生成实验总结报告 ====================
    print("\n" + "="*80)
    print("生成实验总结报告")
    print("="*80)
    
    summary = {
        'experiment_overview': {
            'exp1': 'BERT基础实现',
            'exp2': 'BERT vs RoBERTa模型对比',
            'exp3': '数据增强效果对比'
        },
        'all_results': all_experiments,
        'hyperparameters': {
            'batch_size': args.batch_size,
            'epochs': args.epochs,
            'learning_rate': args.learning_rate,
            'max_length': args.max_length,
            'augmentation_type': args.aug_type,
            'augmentation_ratio': args.aug_ratio
        },
        'key_findings': {
            'best_baseline_model': 'BERT' if all_experiments['bert_baseline']['accuracy'] > all_experiments['roberta_baseline']['accuracy'] else 'RoBERTa',
            'bert_improvement': (all_experiments['bert_augmented']['accuracy'] - all_experiments['bert_baseline']['accuracy']) * 100,
            'roberta_improvement': (all_experiments['roberta_augmented']['accuracy'] - all_experiments['roberta_baseline']['accuracy']) * 100
        }
    }
    
    with open(f'{args.results_dir}/experiment_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("所有实验完成！实验总结：")
    print("="*80)
    
    print("\n📊 实验1 - BERT基础实现：")
    print(f"  准确率: {all_experiments['bert_baseline']['accuracy']:.4f}")
    print(f"  F1分数: {all_experiments['bert_baseline']['f1']:.4f}")
    
    print("\n📊 实验2 - 模型对比：")
    print(f"  BERT     - 准确率: {all_experiments['bert_baseline']['accuracy']:.4f}, 训练速度: {all_experiments['bert_baseline']['avg_epoch_time']:.2f}秒/epoch")
    print(f"  RoBERTa  - 准确率: {all_experiments['roberta_baseline']['accuracy']:.4f}, 训练速度: {all_experiments['roberta_baseline']['avg_epoch_time']:.2f}秒/epoch")
    
    print("\n📊 实验3 - 数据增强效果：")
    print(f"  BERT     - 基线: {all_experiments['bert_baseline']['accuracy']:.4f}, 增强后: {all_experiments['bert_augmented']['accuracy']:.4f}, 提升: {summary['key_findings']['bert_improvement']:+.2f}%")
    print(f"  RoBERTa  - 基线: {all_experiments['roberta_baseline']['accuracy']:.4f}, 增强后: {all_experiments['roberta_augmented']['accuracy']:.4f}, 提升: {summary['key_findings']['roberta_improvement']:+.2f}%")
    
    print(f"\n📁 所有结果已保存至: {args.results_dir}")
    print("\n生成的图表文件：")
    print("  实验1: exp1_bert_confusion_matrix.png")
    print("  实验2: exp2_training_comparison.png, exp2_model_comparison.png, exp2_roberta_confusion_matrix.png")
    print("  实验3: exp3_bert/roberta_augmentation_comparison.png, exp3_overall_augmentation_comparison.png")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BERT情感分析完整实验')
    
    # 数据参数
    parser.add_argument('--data_path', type=str, default='IMDB Dataset.csv',
                      help='数据集路径')
    parser.add_argument('--results_dir', type=str, default='results',
                      help='结果保存目录')
    
    # 训练参数
    parser.add_argument('--batch_size', type=int, default=16,
                      help='批次大小')
    parser.add_argument('--epochs', type=int, default=3,
                      help='训练轮数')
    parser.add_argument('--learning_rate', type=float, default=2e-5,
                      help='学习率')
    parser.add_argument('--max_length', type=int, default=256,
                      help='最大序列长度')
    parser.add_argument('--seed', type=int, default=42,
                      help='随机种子')
    
    # 数据增强参数
    parser.add_argument('--aug_type', type=str, default='eda',
                      choices=['eda', 'synonym', 'back_translation'],
                      help='数据增强类型')
    parser.add_argument('--aug_ratio', type=float, default=0.1,
                      help='数据增强比例')
    
    args = parser.parse_args()
    
    main(args)
