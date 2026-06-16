"""
模型融合模块
功能：多模型预测融合、性能评估、结果分析
"""

import pandas as pd
import numpy as np
import joblib
import torch
import torch.nn as nn
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score, KFold
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 导入自定义模块
from dl_models import DeepNeuralNetwork, AttentionNetwork

class ModelEnsemble:
    """模型融合类"""
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.ml_models = {}
        self.dl_models = {}
        self.scalers = {}
        self.ensemble_weights = {}
        self.predictions = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_ml_models(self, model_dir='models/'):
        """
        加载机器学习模型
        
        参数:
            model_dir: 模型目录路径
        """
        import os
        
        model_files = {
            'xgboost': 'xgboost_model.pkl',
            'lightgbm': 'lightgbm_model.pkl',
            'catboost': 'catboost_model.pkl'
        }
        
        for model_name, filename in model_files.items():
            filepath = os.path.join(model_dir, filename)
            if os.path.exists(filepath):
                self.ml_models[model_name] = joblib.load(filepath)
                print(f"已加载 {model_name} 模型")
            else:
                print(f"警告: 未找到 {model_name} 模型文件: {filepath}")
    
    def load_dl_models(self, model_dir='models/', input_size=25):
        """
        加载深度学习模型
        
        参数:
            model_dir: 模型目录路径
            input_size: 输入特征数量
        """
        import os
        
        # 加载标准化器
        scaler_path = os.path.join(model_dir, 'dl_scalers.pkl')
        if os.path.exists(scaler_path):
            self.scalers = joblib.load(scaler_path)
            print("已加载深度学习标准化器")
        
        # 加载DNN模型
        dnn_path = os.path.join(model_dir, 'dnn_model.pth')
        if os.path.exists(dnn_path):
            dnn_model = DeepNeuralNetwork(input_size=input_size)
            dnn_model.load_state_dict(torch.load(dnn_path, map_location=self.device))
            dnn_model.eval()
            self.dl_models['dnn'] = dnn_model
            print("已加载 DNN 模型")
        
        # 加载注意力模型
        attn_path = os.path.join(model_dir, 'attention_model.pth')
        if os.path.exists(attn_path):
            attn_model = AttentionNetwork(input_size=input_size)
            attn_model.load_state_dict(torch.load(attn_path, map_location=self.device))
            attn_model.eval()
            self.dl_models['attention'] = attn_model
            print("已加载 Attention 模型")
    
    def predict_ml_models(self, X):
        """
        使用机器学习模型进行预测
        
        参数:
            X: 特征数据
            
        返回:
            预测结果字典
        """
        ml_predictions = {}
        
        for model_name, model in self.ml_models.items():
            try:
                pred = model.predict(X)
                ml_predictions[model_name] = pred
                print(f"{model_name} 预测完成")
            except Exception as e:
                print(f"{model_name} 预测失败: {e}")
        
        return ml_predictions
    
    def predict_dl_models(self, X):
        """
        使用深度学习模型进行预测
        
        参数:
            X: 特征数据
            
        返回:
            预测结果字典
        """
        dl_predictions = {}
        
        # 标准化特征
        if 'feature_scaler' in self.scalers:
            X_scaled = self.scalers['feature_scaler'].transform(X)
        else:
            X_scaled = X
        
        # 转换为tensor
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)
        
        for model_name, model in self.dl_models.items():
            try:
                with torch.no_grad():
                    pred = model(X_tensor).cpu().numpy()
                dl_predictions[model_name] = pred
                print(f"{model_name} 预测完成")
            except Exception as e:
                print(f"{model_name} 预测失败: {e}")
        
        return dl_predictions
    
    def calculate_model_weights(self, X_val, y_val):
        """
        基于验证集性能计算模型权重
        
        参数:
            X_val: 验证特征
            y_val: 验证目标
            
        返回:
            模型权重字典
        """
        print("计算模型权重...")
        
        # 获取所有模型的预测
        ml_preds = self.predict_ml_models(X_val)
        dl_preds = self.predict_dl_models(X_val)
        
        all_predictions = {**ml_preds, **dl_preds}
        
        # 计算每个模型的RMSE
        model_scores = {}
        for model_name, pred in all_predictions.items():
            rmse = np.sqrt(mean_squared_error(y_val, pred))
            model_scores[model_name] = rmse
            print(f"{model_name} RMSE: {rmse:.4f}")
        
        # 计算权重（RMSE越小权重越大）
        # 使用倒数权重方法
        total_inv_score = sum(1/score for score in model_scores.values())
        weights = {name: (1/score)/total_inv_score for name, score in model_scores.items()}
        
        self.ensemble_weights = weights
        
        print("\n模型权重:")
        for name, weight in weights.items():
            print(f"{name}: {weight:.4f}")
        
        return weights
    
    def ensemble_predict(self, X, method='weighted_average'):
        """
        集成预测
        
        参数:
            X: 特征数据
            method: 融合方法 ('weighted_average', 'simple_average')
            
        返回:
            集成预测结果
        """
        print(f"使用 {method} 方法进行集成预测...")
        
        # 获取所有模型的预测
        ml_preds = self.predict_ml_models(X)
        dl_preds = self.predict_dl_models(X)
        
        all_predictions = {**ml_preds, **dl_preds}
        self.predictions = all_predictions
        
        if method == 'simple_average':
            # 简单平均
            pred_array = np.array(list(all_predictions.values()))
            ensemble_pred = np.mean(pred_array, axis=0)
        
        elif method == 'weighted_average':
            # 加权平均
            if not self.ensemble_weights:
                print("警告: 未计算模型权重，使用简单平均")
                pred_array = np.array(list(all_predictions.values()))
                ensemble_pred = np.mean(pred_array, axis=0)
            else:
                ensemble_pred = np.zeros(len(list(all_predictions.values())[0]))
                for model_name, pred in all_predictions.items():
                    weight = self.ensemble_weights.get(model_name, 0)
                    ensemble_pred += weight * pred
        
        else:
            raise ValueError(f"不支持的融合方法: {method}")
        
        return ensemble_pred
    
    def evaluate_ensemble(self, y_true, y_pred):
        """
        评估集成模型性能
        
        参数:
            y_true: 真实值
            y_pred: 预测值
            
        返回:
            评估指标字典
        """
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        metrics = {
            'RMSE': rmse,
            'MAE': mae,
            'R²': r2
        }
        
        return metrics
    
    def compare_models(self, X_val, y_val):
        """
        比较所有模型性能
        
        参数:
            X_val: 验证特征
            y_val: 验证目标
            
        返回:
            性能比较结果
        """
        print("比较模型性能...")
        
        # 获取所有模型预测
        ml_preds = self.predict_ml_models(X_val)
        dl_preds = self.predict_dl_models(X_val)
        
        # 集成预测
        ensemble_pred = self.ensemble_predict(X_val, method='weighted_average')
        
        # 计算所有模型的性能
        results = {}
        
        # 机器学习模型
        for name, pred in ml_preds.items():
            metrics = self.evaluate_ensemble(y_val, pred)
            results[name] = metrics
        
        # 深度学习模型
        for name, pred in dl_preds.items():
            metrics = self.evaluate_ensemble(y_val, pred)
            results[name] = metrics
        
        # 集成模型
        ensemble_metrics = self.evaluate_ensemble(y_val, ensemble_pred)
        results['ensemble'] = ensemble_metrics
        
        # 创建比较表格
        comparison_df = pd.DataFrame(results).T
        comparison_df = comparison_df.round(4)
        comparison_df = comparison_df.sort_values('RMSE')
        
        print("\n模型性能比较:")
        print(comparison_df)
        
        return comparison_df
    
    def plot_predictions_comparison(self, y_true, save_plot=True):
        """
        绘制预测结果比较图
        
        参数:
            y_true: 真实值
            save_plot: 是否保存图片
        """
        if not self.predictions:
            print("错误: 没有预测结果可用于绘图")
            return
        
        # 准备数据
        n_models = len(self.predictions)
        fig, axes = plt.subplots(2, (n_models + 1) // 2, figsize=(15, 10))
        axes = axes.flatten() if n_models > 1 else [axes]
        
        for i, (model_name, y_pred) in enumerate(self.predictions.items()):
            if i < len(axes):
                axes[i].scatter(y_true, y_pred, alpha=0.5, s=1)
                axes[i].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
                axes[i].set_xlabel('真实值')
                axes[i].set_ylabel('预测值')
                axes[i].set_title(f'{model_name}')
                axes[i].grid(True)
        
        # 隐藏多余的子图
        for i in range(len(self.predictions), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        if save_plot:
            plt.savefig('predictions_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_residuals_analysis(self, y_true, y_pred, model_name='Ensemble'):
        """
        绘制残差分析图
        
        参数:
            y_true: 真实值
            y_pred: 预测值
            model_name: 模型名称
        """
        residuals = y_true - y_pred
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 残差vs预测值
        axes[0, 0].scatter(y_pred, residuals, alpha=0.5, s=1)
        axes[0, 0].axhline(y=0, color='r', linestyle='--')
        axes[0, 0].set_xlabel('预测值')
        axes[0, 0].set_ylabel('残差')
        axes[0, 0].set_title('残差 vs 预测值')
        axes[0, 0].grid(True)
        
        # 残差直方图
        axes[0, 1].hist(residuals, bins=50, alpha=0.7, edgecolor='black')
        axes[0, 1].set_xlabel('残差')
        axes[0, 1].set_ylabel('频次')
        axes[0, 1].set_title('残差分布')
        axes[0, 1].grid(True)
        
        # Q-Q图
        stats.probplot(residuals, dist="norm", plot=axes[1, 0])
        axes[1, 0].set_title('残差 Q-Q 图')
        axes[1, 0].grid(True)
        
        # 残差vs真实值
        axes[1, 1].scatter(y_true, residuals, alpha=0.5, s=1)
        axes[1, 1].axhline(y=0, color='r', linestyle='--')
        axes[1, 1].set_xlabel('真实值')
        axes[1, 1].set_ylabel('残差')
        axes[1, 1].set_title('残差 vs 真实值')
        axes[1, 1].grid(True)
        
        plt.suptitle(f'{model_name} 残差分析')
        plt.tight_layout()
        plt.savefig(f'{model_name}_residuals_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def feature_importance_ensemble(self):
        """
        集成特征重要性分析
        """
        print("分析集成模型特征重要性...")
        
        importance_data = {}
        
        # 收集机器学习模型的特征重要性
        for model_name, model in self.ml_models.items():
            if hasattr(model, 'feature_importances_'):
                importance_data[model_name] = model.feature_importances_
        
        if importance_data:
            # 创建特征重要性数据框
            importance_df = pd.DataFrame(importance_data)
            
            # 计算平均重要性
            importance_df['mean'] = importance_df.mean(axis=1)
            importance_df = importance_df.sort_values('mean', ascending=False)
            
            # 绘制前20个重要特征
            top_features = importance_df.head(20)
            
            plt.figure(figsize=(12, 8))
            plt.barh(range(len(top_features)), top_features['mean'])
            plt.yticks(range(len(top_features)), [f'Feature_{i}' for i in top_features.index])
            plt.xlabel('平均特征重要性')
            plt.title('集成模型特征重要性 (前20个)')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig('ensemble_feature_importance.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            return importance_df
        else:
            print("没有可用的特征重要性信息")
            return None

def main():
    """主函数"""
    # 加载数据
    print("加载数据...")
    train_df = pd.read_csv('train_features.csv')
    
    # 分割验证集
    from sklearn.model_selection import train_test_split
    
    feature_cols = [col for col in train_df.columns if col not in ['id', 'Calories']]
    X = train_df[feature_cols]
    y = train_df['Calories']
    
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 创建集成模型
    ensemble = ModelEnsemble(random_state=42)
    
    # 加载模型
    ensemble.load_ml_models()
    ensemble.load_dl_models(input_size=len(feature_cols))
    
    # 计算模型权重
    ensemble.calculate_model_weights(X_val, y_val)
    
    # 比较模型性能
    comparison_results = ensemble.compare_models(X_val, y_val)
    
    # 集成预测
    ensemble_pred = ensemble.ensemble_predict(X_val, method='weighted_average')
    
    # 绘制分析图
    ensemble.plot_predictions_comparison(y_val.values)
    ensemble.plot_residuals_analysis(y_val.values, ensemble_pred, 'Ensemble')
    
    # 特征重要性分析
    ensemble.feature_importance_ensemble()
    
    print("模型融合和评估完成!")

if __name__ == "__main__":
    main() 