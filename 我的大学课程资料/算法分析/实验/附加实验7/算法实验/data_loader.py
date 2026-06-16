"""
数据加载和预处理模块
用于加载IMDB数据集并进行预处理
"""

import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split
import os


class IMDBDataset(Dataset):
    """IMDB数据集类"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        """
        初始化数据集
        
        Args:
            texts: 文本列表
            labels: 标签列表
            tokenizer: 分词器
            max_length: 最大序列长度
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # 使用tokenizer进行编码
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def load_imdb_data(data_path='IMDB Dataset.csv', test_size=0.2, random_state=42):
    """
    加载IMDB数据集
    
    Args:
        data_path: 数据文件路径
        test_size: 测试集比例
        random_state: 随机种子
        
    Returns:
        train_texts, val_texts, train_labels, val_labels
    """
    print("正在加载数据集...")
    
    # 读取CSV文件
    df = pd.read_csv(data_path)
    
    # 将sentiment转换为二分类标签 (positive: 1, negative: 0)
    df['label'] = df['sentiment'].apply(lambda x: 1 if x == 'positive' else 0)
    
    # 提取文本和标签
    texts = df['review'].tolist()
    labels = df['label'].tolist()
    
    # 划分训练集和验证集
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, 
        test_size=test_size, 
        random_state=random_state,
        stratify=labels
    )
    
    print(f"数据集加载完成！")
    print(f"训练集大小: {len(train_texts)}")
    print(f"验证集大小: {len(val_texts)}")
    print(f"正面评论比例: {sum(labels)/len(labels)*100:.2f}%")
    
    return train_texts, val_texts, train_labels, val_labels


def create_data_loaders(train_texts, val_texts, train_labels, val_labels, 
                        tokenizer, batch_size=16, max_length=512):
    """
    创建数据加载器
    
    Args:
        train_texts, val_texts: 训练和验证文本
        train_labels, val_labels: 训练和验证标签
        tokenizer: 分词器
        batch_size: 批次大小
        max_length: 最大序列长度
        
    Returns:
        train_loader, val_loader
    """
    # 创建数据集
    train_dataset = IMDBDataset(train_texts, train_labels, tokenizer, max_length)
    val_dataset = IMDBDataset(val_texts, val_labels, tokenizer, max_length)
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=2
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2
    )
    
    return train_loader, val_loader

