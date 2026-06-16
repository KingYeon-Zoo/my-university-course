"""
快速测试脚本
使用小规模数据集进行快速测试，验证代码是否正常运行
"""

import torch
import pandas as pd
from transformers import AutoTokenizer
from data_loader import load_imdb_data, create_data_loaders
from train import train_model
from visualization import plot_training_history, plot_model_comparison
import os


def quick_test():
    """快速测试函数"""
    
    print("="*80)
    print("开始快速测试（使用小规模数据）")
    print("="*80)
    
    # 创建测试结果目录
    test_dir = 'test_results'
    os.makedirs(test_dir, exist_ok=True)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n使用设备: {device}")
    
    # 加载数据（只使用一小部分）
    print("\n1. 加载小规模测试数据...")
    df = pd.read_csv('IMDB Dataset.csv')
    
    # 只使用500条数据进行快速测试
    df_sample = df.sample(n=500, random_state=42)
    df_sample.to_csv('IMDB_test_subset.csv', index=False)
    
    train_texts, val_texts, train_labels, val_labels = load_imdb_data(
        'IMDB_test_subset.csv', 
        test_size=0.2, 
        random_state=42
    )
    
    # 测试单个模型
    model_name = 'bert-base-uncased'
    print(f"\n2. 测试模型: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_loader, val_loader = create_data_loaders(
        train_texts, val_texts, train_labels, val_labels,
        tokenizer, 
        batch_size=8,
        max_length=128
    )
    
    print(f"\n3. 开始训练（1个epoch）...")
    history, results = train_model(
        model_name=model_name,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        epochs=1,  # 只训练1个epoch
        learning_rate=2e-5,
        save_dir=test_dir
    )
    
    print("\n测试完成!")
    print(f"验证准确率: {results['accuracy']:.4f}")
    print(f"F1分数: {results['f1']:.4f}")
    
    # 清理测试文件
    if os.path.exists('IMDB_test_subset.csv'):
        os.remove('IMDB_test_subset.csv')
    
    print(f"\n测试结果已保存至: {test_dir}")
    print("\n如果测试成功，你可以运行完整实验了！")


if __name__ == '__main__':
    quick_test()

