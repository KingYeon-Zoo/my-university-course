"""
测试集预测和提交模块
功能：使用训练好的模型对测试集进行预测并生成提交文件
"""

import pandas as pd
import numpy as np
import joblib
import torch
import warnings
warnings.filterwarnings('ignore')

# 导入自定义模块
from data_preprocessing import DataPreprocessor
from feature_engineering import FeatureEngineer
from model_ensemble import ModelEnsemble

class PredictionSubmission:
    """预测提交类"""
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.ensemble = ModelEnsemble(random_state=random_state)
        
    def load_test_data(self, test_path='test.csv'):
        """
        加载测试数据
        
        参数:
            test_path: 测试数据路径
            
        返回:
            测试数据DataFrame
        """
        print("加载测试数据...")
        test_df = pd.read_csv(test_path)
        print(f"测试集形状: {test_df.shape}")
        print(f"测试集列名: {test_df.columns.tolist()}")
        
        return test_df
    
    def preprocess_test_data(self, test_df):
        """
        预处理测试数据
        
        参数:
            test_df: 原始测试数据
            
        返回:
            预处理后的测试数据
        """
        print("预处理测试数据...")
        
        # 对于测试数据，只需要进行分类编码
        test_processed = test_df.copy()
        
        # 手动编码 Sex 列 (假设 Female=0, Male=1)
        if 'Sex' in test_processed.columns:
            test_processed['Sex'] = test_processed['Sex'].map({'Female': 0, 'Male': 1})
            print("已编码 Sex 列: Female=0, Male=1")
        
        print(f"预处理后测试集形状: {test_processed.shape}")
        
        return test_processed
    
    def engineer_test_features(self, test_df):
        """
        对测试数据进行特征工程
        
        参数:
            test_df: 预处理后的测试数据
            
        返回:
            特征工程后的测试数据
        """
        print("对测试数据进行特征工程...")
        
        # 分步生成新特征
        test_features = self.feature_engineer.create_physiological_features(test_df)
        test_features = self.feature_engineer.create_interaction_features(test_features)
        test_features = self.feature_engineer.create_polynomial_features(test_features, degree=2)
        test_features = self.feature_engineer.create_statistical_features(test_features)
        
        # 加载训练时的标准化器和特征选择器
        try:
            scaler = joblib.load('models/feature_scaler.pkl')
            selector = joblib.load('models/feature_selector.pkl')
            
            # 标准化特征
            feature_cols = [col for col in test_features.columns if col not in ['id']]
            test_features[feature_cols] = scaler.transform(test_features[feature_cols])
            
            # 特征选择
            selected_features = selector.get_support(indices=True)
            selected_feature_names = [feature_cols[i] for i in selected_features]
            
            # 保留id列和选择的特征
            final_features = ['id'] + selected_feature_names
            test_features = test_features[final_features]
            
            print(f"特征工程后测试集形状: {test_features.shape}")
            print(f"选择的特征数量: {len(selected_feature_names)}")
            
        except FileNotFoundError as e:
            print(f"警告: 未找到预处理文件 {e}")
            print("使用原始特征...")
        
        return test_features
    
    def make_predictions(self, test_features):
        """
        使用集成模型进行预测
        
        参数:
            test_features: 特征工程后的测试数据
            
        返回:
            预测结果
        """
        print("开始预测...")
        
        # 准备特征数据
        feature_cols = [col for col in test_features.columns if col != 'id']
        X_test = test_features[feature_cols]
        
        # 加载机器学习模型
        self.ensemble.load_ml_models()
        
        # 尝试加载深度学习模型（如果存在）
        try:
            self.ensemble.load_dl_models(input_size=len(feature_cols))
        except Exception as e:
            print(f"深度学习模型加载失败: {e}")
            print("仅使用机器学习模型进行预测")
        
        # 加载模型权重
        try:
            weights = joblib.load('models/ensemble_weights.pkl')
            self.ensemble.ensemble_weights = weights
            print("已加载集成权重")
        except FileNotFoundError:
            print("未找到集成权重，使用简单平均")
        
        # 进行集成预测
        if self.ensemble.ml_models:
            predictions = self.ensemble.ensemble_predict(X_test, method='weighted_average')
        else:
            print("错误: 没有可用的模型")
            return None
        
        print(f"预测完成，预测数量: {len(predictions)}")
        print(f"预测统计: 最小值={predictions.min():.2f}, 最大值={predictions.max():.2f}, 平均值={predictions.mean():.2f}")
        
        return predictions
    
    def create_submission(self, test_df, predictions, submission_path='submission.csv'):
        """
        创建提交文件
        
        参数:
            test_df: 测试数据（包含id列）
            predictions: 预测结果
            submission_path: 提交文件路径
            
        返回:
            提交DataFrame
        """
        print("创建提交文件...")
        
        # 创建提交DataFrame
        submission_df = pd.DataFrame({
            'id': test_df['id'],
            'Calories': predictions
        })
        
        # 确保预测值为正数
        submission_df['Calories'] = np.maximum(submission_df['Calories'], 0.1)
        
        # 保存提交文件
        submission_df.to_csv(submission_path, index=False)
        
        print(f"提交文件已保存到: {submission_path}")
        print(f"提交文件形状: {submission_df.shape}")
        print(f"提交文件前5行:")
        print(submission_df.head())
        
        # 检查提交文件格式
        sample_submission = pd.read_csv('sample_submission.csv')
        
        if submission_df.shape == sample_submission.shape and list(submission_df.columns) == list(sample_submission.columns):
            print("✓ 提交文件格式正确")
        else:
            print("✗ 提交文件格式不匹配")
            print(f"期望形状: {sample_submission.shape}, 实际形状: {submission_df.shape}")
            print(f"期望列名: {sample_submission.columns.tolist()}, 实际列名: {submission_df.columns.tolist()}")
        
        return submission_df
    
    def analyze_predictions(self, predictions):
        """
        分析预测结果
        
        参数:
            predictions: 预测结果
        """
        print("\n预测结果分析:")
        print(f"预测数量: {len(predictions)}")
        print(f"最小值: {predictions.min():.4f}")
        print(f"最大值: {predictions.max():.4f}")
        print(f"平均值: {predictions.mean():.4f}")
        print(f"中位数: {np.median(predictions):.4f}")
        print(f"标准差: {predictions.std():.4f}")
        
        # 检查异常值
        q1 = np.percentile(predictions, 25)
        q3 = np.percentile(predictions, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = np.sum((predictions < lower_bound) | (predictions > upper_bound))
        print(f"异常值数量: {outliers} ({outliers/len(predictions)*100:.2f}%)")
        
        # 分布分析
        print(f"\n分位数分析:")
        for p in [10, 25, 50, 75, 90, 95, 99]:
            print(f"{p}%分位数: {np.percentile(predictions, p):.4f}")
    
    def run_prediction_pipeline(self):
        """
        运行完整的预测流水线
        
        返回:
            提交DataFrame
        """
        print("开始运行预测流水线...")
        
        # 检查是否存在已处理的测试特征文件
        try:
            print("尝试加载已处理的测试特征...")
            test_features = pd.read_csv('test_features.csv')
            print(f"成功加载测试特征，形状: {test_features.shape}")
            
            # 1. 加载原始测试数据 (用于获取id)
            test_df = self.load_test_data()
            
        except FileNotFoundError:
            print("未找到已处理的测试特征文件，进行实时处理...")
            # 1. 加载测试数据
            test_df = self.load_test_data()
            
            # 2. 预处理测试数据
            test_processed = self.preprocess_test_data(test_df)
            
            # 3. 特征工程
            test_features = self.engineer_test_features(test_processed)
        
        # 4. 进行预测
        predictions = self.make_predictions(test_features)
        
        if predictions is None:
            print("预测失败")
            return None
        
        # 5. 分析预测结果
        self.analyze_predictions(predictions)
        
        # 6. 创建提交文件
        submission_df = self.create_submission(test_df, predictions)
        
        print("预测流水线完成!")
        
        return submission_df

def main():
    """主函数"""
    # 创建预测提交器
    predictor = PredictionSubmission(random_state=42)
    
    # 运行预测流水线
    submission_df = predictor.run_prediction_pipeline()
    
    if submission_df is not None:
        print("预测和提交文件生成成功!")
    else:
        print("预测失败!")

if __name__ == "__main__":
    main() 