"""
模型训练模块
实现模型的训练和评估功能
"""

import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from tqdm import tqdm
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import time
import json
import os


class Trainer:
    """训练器类"""
    
    def __init__(self, model, train_loader, val_loader, device, 
                 learning_rate=2e-5, epochs=3, warmup_steps=0):
        """
        初始化训练器
        
        Args:
            model: 模型
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            device: 设备
            learning_rate: 学习率
            epochs: 训练轮数
            warmup_steps: 预热步数
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.epochs = epochs
        
        # 优化器
        self.optimizer = AdamW(model.parameters(), lr=learning_rate)
        
        # 学习率调度器
        total_steps = len(train_loader) * epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        # 损失函数
        self.criterion = nn.CrossEntropyLoss()
        
        # 训练历史
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
            'val_f1': [],
            'epoch_times': []
        }
    
    def train_epoch(self):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0
        predictions = []
        true_labels = []
        
        progress_bar = tqdm(self.train_loader, desc='Training')
        
        for batch in progress_bar:
            # 数据转移到设备
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # 清空梯度
            self.optimizer.zero_grad()
            
            # 前向传播
            logits = self.model(input_ids, attention_mask)
            loss = self.criterion(logits, labels)
            
            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            # 更新参数
            self.optimizer.step()
            self.scheduler.step()
            
            # 记录损失和预测
            total_loss += loss.item()
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            predictions.extend(preds)
            true_labels.extend(labels.cpu().numpy())
            
            # 更新进度条
            progress_bar.set_postfix({'loss': loss.item()})
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = accuracy_score(true_labels, predictions)
        
        return avg_loss, accuracy
    
    def evaluate(self):
        """评估模型"""
        self.model.eval()
        total_loss = 0
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in tqdm(self.val_loader, desc='Evaluating'):
                # 数据转移到设备
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # 前向传播
                logits = self.model(input_ids, attention_mask)
                loss = self.criterion(logits, labels)
                
                # 记录损失和预测
                total_loss += loss.item()
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                predictions.extend(preds)
                true_labels.extend(labels.cpu().numpy())
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary'
        )
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'predictions': predictions,
            'true_labels': true_labels
        }
    
    def train(self):
        """完整训练流程"""
        print("开始训练...")
        best_val_acc = 0
        
        for epoch in range(self.epochs):
            print(f"\nEpoch {epoch + 1}/{self.epochs}")
            
            # 记录epoch开始时间
            epoch_start_time = time.time()
            
            # 训练
            train_loss, train_acc = self.train_epoch()
            
            # 评估
            val_results = self.evaluate()
            
            # 记录epoch时间
            epoch_time = time.time() - epoch_start_time
            
            # 更新历史
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_results['loss'])
            self.history['val_acc'].append(val_results['accuracy'])
            self.history['val_f1'].append(val_results['f1'])
            self.history['epoch_times'].append(epoch_time)
            
            # 打印结果
            print(f"训练损失: {train_loss:.4f}, 训练准确率: {train_acc:.4f}")
            print(f"验证损失: {val_results['loss']:.4f}, 验证准确率: {val_results['accuracy']:.4f}")
            print(f"验证F1分数: {val_results['f1']:.4f}")
            print(f"Epoch用时: {epoch_time:.2f}秒")
            
            # 保存最佳模型
            if val_results['accuracy'] > best_val_acc:
                best_val_acc = val_results['accuracy']
                print(f"保存最佳模型 (验证准确率: {best_val_acc:.4f})")
        
        print(f"\n训练完成！最佳验证准确率: {best_val_acc:.4f}")
        
        return self.history


def train_model(model_name, train_loader, val_loader, device, 
                epochs=3, learning_rate=2e-5, save_dir='results'):
    """
    训练模型的便捷函数
    
    Args:
        model_name: 模型名称
        train_loader: 训练数据加载器
        val_loader: 验证数据加载器
        device: 设备
        epochs: 训练轮数
        learning_rate: 学习率
        save_dir: 结果保存目录
        
    Returns:
        history: 训练历史
        final_results: 最终评估结果
    """
    from model import get_model
    
    # 创建模型
    model = get_model(model_name)
    
    # 创建训练器
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        learning_rate=learning_rate,
        epochs=epochs
    )
    
    # 训练
    history = trainer.train()
    
    # 最终评估
    final_results = trainer.evaluate()
    
    # 保存结果
    os.makedirs(save_dir, exist_ok=True)
    
    # 保存训练历史
    model_simple_name = model_name.split('/')[-1]
    with open(f'{save_dir}/{model_simple_name}_history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    # 保存最终结果
    results_to_save = {
        'accuracy': final_results['accuracy'],
        'precision': final_results['precision'],
        'recall': final_results['recall'],
        'f1': final_results['f1'],
        'avg_epoch_time': np.mean(history['epoch_times'])
    }
    
    with open(f'{save_dir}/{model_simple_name}_results.json', 'w') as f:
        json.dump(results_to_save, f, indent=2)
    
    return history, final_results

