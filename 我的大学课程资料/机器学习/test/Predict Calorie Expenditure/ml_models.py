"""
机器学习模型模块
功能：XGBoost/LightGBM/CatBoost训练和调优
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import optuna
import joblib
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class MLModelTrainer:
    """机器学习模型训练器"""
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.models = {}
        self.best_params = {}
        self.cv_scores = {}
        
    def prepare_data(self, train_df, target_col='Calories', exclude_cols=['id']):
        """
        准备训练数据
        
        参数:
            train_df: 训练数据
            target_col: 目标列名
            exclude_cols: 排除的列
            
        返回:
            X, y: 特征和目标变量
        """
        feature_cols = [col for col in train_df.columns if col not in exclude_cols + [target_col]]
        X = train_df[feature_cols]
        y = train_df[target_col]
        
        print(f"特征数量: {len(feature_cols)}")
        print(f"样本数量: {len(X)}")
        
        return X, y
    
    def xgboost_objective(self, trial, X, y, cv_folds=5):
        """XGBoost超参数优化目标函数"""
        
        params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'booster': 'gbtree',
            'random_state': self.random_state,
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=50),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        }
        
        model = xgb.XGBRegressor(**params)
        
        # 交叉验证
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        scores = cross_val_score(model, X, y, cv=kf, scoring='neg_root_mean_squared_error')
        
        return -scores.mean()  # 返回正的RMSE值
    
    def lightgbm_objective(self, trial, X, y, cv_folds=5):
        """LightGBM超参数优化目标函数"""
        
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'random_state': self.random_state,
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=50),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 10, 300),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
        }
        
        model = lgb.LGBMRegressor(**params, verbose=-1)
        
        # 交叉验证
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        scores = cross_val_score(model, X, y, cv=kf, scoring='neg_root_mean_squared_error')
        
        return -scores.mean()
    
    def catboost_objective(self, trial, X, y, cv_folds=5):
        """CatBoost超参数优化目标函数"""
        
        params = {
            'loss_function': 'RMSE',
            'random_state': self.random_state,
            'verbose': False,
            'iterations': trial.suggest_int('iterations', 100, 1000, step=50),
            'depth': trial.suggest_int('depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.6, 1.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        }
        
        model = cb.CatBoostRegressor(**params)
        
        # 交叉验证
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        scores = cross_val_score(model, X, y, cv=kf, scoring='neg_root_mean_squared_error')
        
        return -scores.mean()
    
    def optimize_hyperparameters(self, X, y, model_name='xgboost', n_trials=100):
        """
        超参数优化
        
        参数:
            X: 特征数据
            y: 目标变量
            model_name: 模型名称 ('xgboost', 'lightgbm', 'catboost')
            n_trials: 优化试验次数
            
        返回:
            最佳参数
        """
        print(f"开始 {model_name} 超参数优化，试验次数: {n_trials}")
        
        # 选择目标函数
        if model_name == 'xgboost':
            objective_func = lambda trial: self.xgboost_objective(trial, X, y)
        elif model_name == 'lightgbm':
            objective_func = lambda trial: self.lightgbm_objective(trial, X, y)
        elif model_name == 'catboost':
            objective_func = lambda trial: self.catboost_objective(trial, X, y)
        else:
            raise ValueError(f"不支持的模型: {model_name}")
        
        # 创建优化器
        study = optuna.create_study(direction='minimize')
        study.optimize(objective_func, n_trials=n_trials)
        
        best_params = study.best_params
        best_score = study.best_value
        
        print(f"{model_name} 最佳RMSE: {best_score:.4f}")
        print(f"{model_name} 最佳参数: {best_params}")
        
        self.best_params[model_name] = best_params
        return best_params
    
    def train_model(self, X, y, model_name='xgboost', params=None):
        """
        训练模型
        
        参数:
            X: 特征数据
            y: 目标变量
            model_name: 模型名称
            params: 模型参数
            
        返回:
            训练好的模型
        """
        if params is None:
            params = self.best_params.get(model_name, {})
        
        print(f"训练 {model_name} 模型...")
        
        if model_name == 'xgboost':
            model = xgb.XGBRegressor(**params, random_state=self.random_state)
        elif model_name == 'lightgbm':
            model = lgb.LGBMRegressor(**params, random_state=self.random_state, verbose=-1)
        elif model_name == 'catboost':
            model = cb.CatBoostRegressor(**params, random_state=self.random_state, verbose=False)
        else:
            raise ValueError(f"不支持的模型: {model_name}")
        
        # 训练模型
        model.fit(X, y)
        
        # 交叉验证评估
        kf = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(model, X, y, cv=kf, scoring='neg_root_mean_squared_error')
        cv_rmse = -cv_scores.mean()
        cv_std = cv_scores.std()
        
        print(f"{model_name} 交叉验证 RMSE: {cv_rmse:.4f} (+/- {cv_std:.4f})")
        
        self.models[model_name] = model
        self.cv_scores[model_name] = {'rmse': cv_rmse, 'std': cv_std}
        
        return model
    
    def evaluate_model(self, model, X, y):
        """
        评估模型性能
        
        参数:
            model: 训练好的模型
            X: 特征数据
            y: 目标变量
            
        返回:
            评估指标字典
        """
        predictions = model.predict(X)
        
        rmse = np.sqrt(mean_squared_error(y, predictions))
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)
        
        metrics = {
            'RMSE': rmse,
            'MAE': mae,
            'R²': r2
        }
        
        return metrics
    
    def plot_feature_importance(self, model_name, feature_names=None, top_n=20):
        """
        绘制特征重要性图
        
        参数:
            model_name: 模型名称
            feature_names: 特征名称列表
            top_n: 显示前N个重要特征
        """
        if model_name not in self.models:
            print(f"模型 {model_name} 未找到")
            return
        
        model = self.models[model_name]
        
        # 获取特征重要性
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            print(f"模型 {model_name} 不支持特征重要性")
            return
        
        # 创建特征重要性数据框
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(importances))]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False).head(top_n)
        
        # 绘图
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(importance_df)), importance_df['importance'])
        plt.yticks(range(len(importance_df)), importance_df['feature'])
        plt.xlabel('特征重要性')
        plt.title(f'{model_name} 特征重要性 (前{top_n}个)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(f'{model_name}_feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_models(self, save_dir='models/'):
        """保存训练好的模型"""
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            filepath = os.path.join(save_dir, f'{model_name}_model.pkl')
            joblib.dump(model, filepath)
            print(f"已保存 {model_name} 模型到 {filepath}")
    
    def train_all_models(self, X, y, optimize=True, n_trials=50):
        """
        训练所有模型
        
        参数:
            X: 特征数据
            y: 目标变量
            optimize: 是否进行超参数优化
            n_trials: 优化试验次数
        """
        models_to_train = ['xgboost', 'lightgbm', 'catboost']
        
        for model_name in models_to_train:
            print(f"\n{'='*50}")
            print(f"处理 {model_name.upper()} 模型")
            print(f"{'='*50}")
            
            if optimize:
                # 超参数优化
                self.optimize_hyperparameters(X, y, model_name, n_trials)
            
            # 训练模型
            model = self.train_model(X, y, model_name)
            
            # 绘制特征重要性
            self.plot_feature_importance(model_name, feature_names=X.columns.tolist())
        
        # 保存模型
        self.save_models()
        
        # 打印总结
        print(f"\n{'='*50}")
        print("模型训练总结")
        print(f"{'='*50}")
        for model_name, scores in self.cv_scores.items():
            print(f"{model_name}: RMSE = {scores['rmse']:.4f} (+/- {scores['std']:.4f})")

def main():
    """主函数"""
    # 加载特征工程后的数据
    print("加载特征工程后的数据...")
    train_df = pd.read_csv('train_features.csv')
    
    # 创建模型训练器
    trainer = MLModelTrainer(random_state=42)
    
    # 准备数据
    X, y = trainer.prepare_data(train_df)
    
    # 训练所有模型
    trainer.train_all_models(X, y, optimize=True, n_trials=30)
    
    print("机器学习模型训练完成!")

if __name__ == "__main__":
    main()
