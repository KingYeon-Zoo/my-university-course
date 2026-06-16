"""
深度学习模型模块
功能：深度神经网络设计和训练
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import joblib
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class CalorieDataset(Dataset):
    """卡路里预测数据集类"""
    
    def __init__(self, X, y=None):
        self.X = torch.FloatTensor(X.values if hasattr(X, 'values') else X)
        self.y = torch.FloatTensor(y.values if y is not None and hasattr(y, 'values') else y) if y is not None else None
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        if self.y is not None:
            return self.X[idx], self.y[idx]
        return self.X[idx]

class DeepNeuralNetwork(nn.Module):
    """深度神经网络模型"""
    
    def __init__(self, input_size, hidden_sizes=[256, 128, 64], dropout_rate=0.3):
        super(DeepNeuralNetwork, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = hidden_size
        
        # 输出层
        layers.append(nn.Linear(prev_size, 1))
        
        self.network = nn.Sequential(*layers)
        
        # 权重初始化
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """权重初始化"""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        return self.network(x).squeeze()

class AttentionNetwork(nn.Module):
    """注意力增强网络"""
    
    def __init__(self, input_size, hidden_sizes=[256, 128, 64], dropout_rate=0.3, num_heads=4):
        super(AttentionNetwork, self).__init__()
        
        self.input_size = input_size
        self.num_heads = num_heads
        
        # 特征嵌入层
        self.feature_embedding = nn.Linear(input_size, hidden_sizes[0])
        
        # 多头自注意力
        self.multihead_attn = nn.MultiheadAttention(
            embed_dim=hidden_sizes[0], 
            num_heads=num_heads, 
            dropout=dropout_rate,
            batch_first=True
        )
        
        # 前馈网络
        layers = []
        prev_size = hidden_sizes[0]
        
        for hidden_size in hidden_sizes[1:]:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = hidden_size
        
        # 输出层
        layers.append(nn.Linear(prev_size, 1))
        
        self.feedforward = nn.Sequential(*layers)
        
        # 权重初始化
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """权重初始化"""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        # 特征嵌入
        embedded = self.feature_embedding(x)  # [batch_size, hidden_size]
        
        # 为注意力机制添加序列维度
        embedded = embedded.unsqueeze(1)  # [batch_size, 1, hidden_size]
        
        # 多头自注意力
        attn_output, _ = self.multihead_attn(embedded, embedded, embedded)
        attn_output = attn_output.squeeze(1)  # [batch_size, hidden_size]
        
        # 残差连接
        output = attn_output + embedded.squeeze(1)
        
        # 前馈网络
        output = self.feedforward(output).squeeze()
        
        return output

class DLModelTrainer:
    """深度学习模型训练器"""
    
    def __init__(self, device=None, random_state=42):
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.random_state = random_state
        self.models = {}
        self.scalers = {}
        self.training_history = {}
        
        # 设置随机种子
        torch.manual_seed(random_state)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(random_state)
        
        print(f"使用设备: {self.device}")
    
    def prepare_data(self, train_df, target_col='Calories', exclude_cols=['id'], test_size=0.2):
        """
        准备训练数据
        
        参数:
            train_df: 训练数据
            target_col: 目标列名
            exclude_cols: 排除的列
            test_size: 验证集比例
            
        返回:
            训练和验证数据加载器
        """
        feature_cols = [col for col in train_df.columns if col not in exclude_cols + [target_col]]
        X = train_df[feature_cols]
        y = train_df[target_col]
        
        print(f"特征数量: {len(feature_cols)}")
        print(f"样本数量: {len(X)}")
        
        # 分割数据
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        
        # 特征标准化
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        self.scalers['feature_scaler'] = scaler
        
        # 创建数据集
        train_dataset = CalorieDataset(X_train_scaled, y_train.values)
        val_dataset = CalorieDataset(X_val_scaled, y_val.values)
        
        # 创建数据加载器
        train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=256, shuffle=False)
        
        return train_loader, val_loader, len(feature_cols)
    
    def train_model(self, model, train_loader, val_loader, model_name='dnn', 
                   epochs=100, learning_rate=0.001, weight_decay=1e-5, patience=10):
        """
        训练模型
        
        参数:
            model: 模型实例
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            model_name: 模型名称
            epochs: 训练轮数
            learning_rate: 学习率
            weight_decay: 权重衰减
            patience: 早停耐心值
            
        返回:
            训练好的模型
        """
        model = model.to(self.device)
        
        # 损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
        
        # 训练历史
        history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': []
        }
        
        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state = None
        
        print(f"开始训练 {model_name} 模型...")
        
        for epoch in range(epochs):
            # 训练阶段
            model.train()
            train_losses = []
            
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_losses.append(loss.item())
            
            # 验证阶段
            model.eval()
            val_losses = []
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    val_losses.append(loss.item())
            
            # 计算平均损失
            avg_train_loss = np.mean(train_losses)
            avg_val_loss = np.mean(val_losses)
            current_lr = optimizer.param_groups[0]['lr']
            
            # 更新历史
            history['train_loss'].append(avg_train_loss)
            history['val_loss'].append(avg_val_loss)
            history['learning_rate'].append(current_lr)
            
            # 学习率调度
            scheduler.step(avg_val_loss)
            
            # 早停检查
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                best_model_state = model.state_dict().copy()
            else:
                patience_counter += 1
            
            # 打印进度
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {avg_train_loss:.4f}, '
                      f'Val Loss: {avg_val_loss:.4f}, LR: {current_lr:.6f}')
            
            # 早停
            if patience_counter >= patience:
                print(f'早停在第 {epoch+1} 轮，最佳验证损失: {best_val_loss:.4f}')
                break
        
        # 加载最佳模型
        if best_model_state is not None:
            model.load_state_dict(best_model_state)
        
        self.models[model_name] = model
        self.training_history[model_name] = history
        
        print(f"{model_name} 训练完成，最佳验证损失: {best_val_loss:.4f}")
        return model
    
    def evaluate_model(self, model, data_loader):
        """
        评估模型性能
        
        参数:
            model: 训练好的模型
            data_loader: 数据加载器
            
        返回:
            评估指标字典
        """
        model.eval()
        predictions = []
        targets = []
        
        with torch.no_grad():
            for batch_X, batch_y in data_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                outputs = model(batch_X)
                predictions.extend(outputs.cpu().numpy())
                targets.extend(batch_y.cpu().numpy())
        
        predictions = np.array(predictions)
        targets = np.array(targets)
        
        rmse = np.sqrt(mean_squared_error(targets, predictions))
        mae = mean_absolute_error(targets, predictions)
        r2 = r2_score(targets, predictions)
        
        metrics = {
            'RMSE': rmse,
            'MAE': mae,
            'R²': r2
        }
        
        return metrics
    
    def plot_training_history(self, model_name):
        """
        绘制训练历史
        
        参数:
            model_name: 模型名称
        """
        if model_name not in self.training_history:
            print(f"模型 {model_name} 的训练历史未找到")
            return
        
        history = self.training_history[model_name]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # 损失曲线
        ax1.plot(history['train_loss'], label='训练损失', color='blue')
        ax1.plot(history['val_loss'], label='验证损失', color='red')
        ax1.set_title(f'{model_name} 损失曲线')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # 学习率曲线
        ax2.plot(history['learning_rate'], label='学习率', color='green')
        ax2.set_title(f'{model_name} 学习率曲线')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Learning Rate')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'{model_name}_training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_models(self, save_dir='models/'):
        """保存训练好的模型"""
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            # 保存模型状态字典
            model_path = os.path.join(save_dir, f'{model_name}_model.pth')
            torch.save(model.state_dict(), model_path)
            print(f"已保存 {model_name} 模型到 {model_path}")
        
        # 保存标准化器
        if self.scalers:
            scaler_path = os.path.join(save_dir, 'dl_scalers.pkl')
            joblib.dump(self.scalers, scaler_path)
            print(f"已保存标准化器到 {scaler_path}")
    
    def train_all_models(self, train_loader, val_loader, input_size):
        """
        训练所有深度学习模型
        
        参数:
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            input_size: 输入特征数量
        """
        # 训练深度神经网络
        print(f"\n{'='*50}")
        print("训练深度神经网络 (DNN)")
        print(f"{'='*50}")
        
        dnn_model = DeepNeuralNetwork(
            input_size=input_size,
            hidden_sizes=[256, 128, 64],
            dropout_rate=0.3
        )
        
        self.train_model(
            dnn_model, train_loader, val_loader, 
            model_name='dnn', epochs=100, learning_rate=0.001
        )
        
        # 评估DNN模型
        dnn_metrics = self.evaluate_model(dnn_model, val_loader)
        print(f"DNN 验证集性能: RMSE={dnn_metrics['RMSE']:.4f}, MAE={dnn_metrics['MAE']:.4f}, R²={dnn_metrics['R²']:.4f}")
        
        # 绘制训练历史
        self.plot_training_history('dnn')
        
        # 训练注意力网络
        print(f"\n{'='*50}")
        print("训练注意力增强网络 (Attention)")
        print(f"{'='*50}")
        
        attention_model = AttentionNetwork(
            input_size=input_size,
            hidden_sizes=[256, 128, 64],
            dropout_rate=0.3,
            num_heads=4
        )
        
        self.train_model(
            attention_model, train_loader, val_loader,
            model_name='attention', epochs=100, learning_rate=0.001
        )
        
        # 评估注意力模型
        attn_metrics = self.evaluate_model(attention_model, val_loader)
        print(f"Attention 验证集性能: RMSE={attn_metrics['RMSE']:.4f}, MAE={attn_metrics['MAE']:.4f}, R²={attn_metrics['R²']:.4f}")
        
        # 绘制训练历史
        self.plot_training_history('attention')
        
        # 保存模型
        self.save_models()
        
        # 打印总结
        print(f"\n{'='*50}")
        print("深度学习模型训练总结")
        print(f"{'='*50}")
        print(f"DNN: RMSE={dnn_metrics['RMSE']:.4f}, MAE={dnn_metrics['MAE']:.4f}, R²={dnn_metrics['R²']:.4f}")
        print(f"Attention: RMSE={attn_metrics['RMSE']:.4f}, MAE={attn_metrics['MAE']:.4f}, R²={attn_metrics['R²']:.4f}")

def main():
    """主函数"""
    # 加载特征工程后的数据
    print("加载特征工程后的数据...")
    train_df = pd.read_csv('train_features.csv')
    
    # 创建深度学习训练器
    trainer = DLModelTrainer(random_state=42)
    
    # 准备数据
    train_loader, val_loader, input_size = trainer.prepare_data(train_df)
    
    # 训练所有模型
    trainer.train_all_models(train_loader, val_loader, input_size)
    
    print("深度学习模型训练完成!")

if __name__ == "__main__":
    main() 