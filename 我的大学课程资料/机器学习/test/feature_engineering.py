"""
特征工程模块
功能：生理学特征构造、交互特征生成、特征标准化和选择
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    """特征工程类"""
    
    def __init__(self):
        self.scaler = RobustScaler()
        self.feature_selector = None
        self.feature_names = []
        self.selected_features = []
        
    def create_physiological_features(self, df):
        """
        创建基于生理学知识的特征
        
        参数:
            df: 输入数据框
            
        返回:
            添加新特征后的数据框
        """
        df_new = df.copy()
        
        print("Creating physiological features...")
        
        # 1. BMI指数 (Body Mass Index)
        df_new['BMI'] = df_new['Weight'] / (df_new['Height'] / 100) ** 2
        
        # 2. 基础代谢率估算 (Harris-Benedict公式)
        # 男性: BMR = 88.362 + (13.397 × weight) + (4.799 × height) - (5.677 × age)
        # 女性: BMR = 447.593 + (9.247 × weight) + (3.098 × height) - (4.330 × age)
        
        # 假设Sex已经编码: 0=female, 1=male
        bmr_male = 88.362 + (13.397 * df_new['Weight']) + (4.799 * df_new['Height']) - (5.677 * df_new['Age'])
        bmr_female = 447.593 + (9.247 * df_new['Weight']) + (3.098 * df_new['Height']) - (4.330 * df_new['Age'])
        
        # 根据性别选择对应的BMR
        df_new['BMR'] = np.where(df_new['Sex'] == 1, bmr_male, bmr_female)
        
        # 3. 运动强度指标
        # 目标心率区间百分比: (实际心率 - 静息心率) / (最大心率 - 静息心率)
        # 假设静息心率为60，最大心率为220-年龄
        resting_hr = 60
        max_hr = 220 - df_new['Age']
        df_new['Exercise_Intensity'] = (df_new['Heart_Rate'] - resting_hr) / (max_hr - resting_hr)
        
        # 4. 热效率指标
        # 体温变化与运动时长的比值
        normal_temp = 36.5
        df_new['Thermal_Efficiency'] = (df_new['Body_Temp'] - normal_temp) / df_new['Duration']
        
        # 5. 代谢效率
        # 每公斤体重每分钟的卡路里消耗（仅用于训练集）
        if 'Calories' in df_new.columns:
            df_new['Metabolic_Efficiency'] = df_new['Calories'] / (df_new['Weight'] * df_new['Duration'])
        
        # 6. 心率储备 (Heart Rate Reserve)
        df_new['HR_Reserve'] = max_hr - resting_hr
        
        # 7. 相对心率
        df_new['Relative_HR'] = df_new['Heart_Rate'] / max_hr
        
        # 8. 体重指数分类
        df_new['BMI_Category'] = pd.cut(df_new['BMI'], 
                                       bins=[0, 18.5, 25, 30, 100], 
                                       labels=[0, 1, 2, 3])  # 偏瘦、正常、超重、肥胖
        df_new['BMI_Category'] = df_new['BMI_Category'].astype(float)
        
        # 9. 年龄分组
        df_new['Age_Group'] = pd.cut(df_new['Age'], 
                                    bins=[0, 25, 35, 45, 55, 100], 
                                    labels=[0, 1, 2, 3, 4])  # 青年、青中年、中年、中老年、老年
        df_new['Age_Group'] = df_new['Age_Group'].astype(float)
        
        # 10. 运动时长分组
        df_new['Duration_Group'] = pd.cut(df_new['Duration'], 
                                         bins=[0, 10, 20, 30, 100], 
                                         labels=[0, 1, 2, 3])  # 短时、中时、长时、超长时
        df_new['Duration_Group'] = df_new['Duration_Group'].astype(float)
        
        print(f"Created {len([col for col in df_new.columns if col not in df.columns])} physiological features")
        return df_new
    
    def create_interaction_features(self, df):
        """
        创建交互特征
        
        参数:
            df: 输入数据框
            
        返回:
            添加交互特征后的数据框
        """
        df_new = df.copy()
        
        print("Creating interaction features...")
        
        # 1. 性别-年龄交互
        df_new['Sex_Age_Interaction'] = df_new['Sex'] * df_new['Age']
        
        # 2. 体重-心率交互
        df_new['Weight_HR_Interaction'] = df_new['Weight'] * df_new['Heart_Rate']
        
        # 3. 时长-强度交互
        df_new['Duration_Intensity_Interaction'] = df_new['Duration'] * df_new['Exercise_Intensity']
        
        # 4. 体温-代谢交互
        df_new['Temp_BMR_Interaction'] = df_new['Body_Temp'] * df_new['BMR']
        
        # 5. BMI-年龄交互
        df_new['BMI_Age_Interaction'] = df_new['BMI'] * df_new['Age']
        
        # 6. 心率-年龄交互
        df_new['HR_Age_Interaction'] = df_new['Heart_Rate'] * df_new['Age']
        
        # 7. 体重-身高比值交互
        df_new['Weight_Height_Ratio'] = df_new['Weight'] / df_new['Height']
        
        # 8. 运动强度-时长交互
        df_new['Intensity_Duration_Product'] = df_new['Exercise_Intensity'] * df_new['Duration']
        
        # 9. 性别-BMI交互
        df_new['Sex_BMI_Interaction'] = df_new['Sex'] * df_new['BMI']
        
        # 10. 心率-体温交互
        df_new['HR_Temp_Interaction'] = df_new['Heart_Rate'] * df_new['Body_Temp']
        
        print(f"Created 10 interaction features")
        return df_new
    
    def create_polynomial_features(self, df, degree=2, selected_cols=None):
        """
        创建多项式特征
        
        参数:
            df: 输入数据框
            degree: 多项式次数
            selected_cols: 选择的列，None表示使用重要特征
            
        返回:
            添加多项式特征后的数据框
        """
        df_new = df.copy()
        
        if selected_cols is None:
            # 选择重要的数值特征进行多项式变换
            selected_cols = ['Duration', 'Heart_Rate', 'BMI', 'Exercise_Intensity']
        
        print(f"Creating polynomial features of degree {degree}...")
        
        for col in selected_cols:
            if col in df_new.columns:
                for d in range(2, degree + 1):
                    df_new[f'{col}_poly_{d}'] = df_new[col] ** d
        
        return df_new
    
    def create_statistical_features(self, df):
        """
        创建统计特征
        
        参数:
            df: 输入数据框
            
        返回:
            添加统计特征后的数据框
        """
        df_new = df.copy()
        
        print("Creating statistical features...")
        
        # 选择数值特征
        numeric_cols = ['Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']
        
        # 计算特征组合的统计量
        feature_groups = [
            ['Height', 'Weight'],  # 身体特征
            ['Heart_Rate', 'Body_Temp'],  # 生理指标
            ['Age', 'Duration'],  # 时间相关
        ]
        
        for i, group in enumerate(feature_groups):
            group_cols = [col for col in group if col in df_new.columns]
            if len(group_cols) >= 2:
                # 计算组内特征的均值、标准差、最大值、最小值
                df_new[f'Group_{i}_Mean'] = df_new[group_cols].mean(axis=1)
                df_new[f'Group_{i}_Std'] = df_new[group_cols].std(axis=1)
                df_new[f'Group_{i}_Max'] = df_new[group_cols].max(axis=1)
                df_new[f'Group_{i}_Min'] = df_new[group_cols].min(axis=1)
                df_new[f'Group_{i}_Range'] = df_new[f'Group_{i}_Max'] - df_new[f'Group_{i}_Min']
        
        return df_new
    
    def scale_features(self, train_df, test_df, exclude_cols=['id', 'Calories']):
        """
        特征标准化
        
        参数:
            train_df: 训练数据
            test_df: 测试数据
            exclude_cols: 不需要标准化的列
            
        返回:
            标准化后的训练和测试数据
        """
        print("Scaling features...")
        
        train_scaled = train_df.copy()
        test_scaled = test_df.copy()
        
        # 选择需要标准化的数值特征，只考虑训练集和测试集都有的列
        train_numeric_cols = train_df.select_dtypes(include=[np.number]).columns
        test_numeric_cols = test_df.select_dtypes(include=[np.number]).columns
        
        # 找到两个数据集共有的数值列
        common_numeric_cols = list(set(train_numeric_cols) & set(test_numeric_cols))
        scale_cols = [col for col in common_numeric_cols if col not in exclude_cols]
        
        # 拟合标准化器
        self.scaler.fit(train_df[scale_cols])
        
        # 应用标准化
        train_scaled[scale_cols] = self.scaler.transform(train_df[scale_cols])
        test_scaled[scale_cols] = self.scaler.transform(test_df[scale_cols])
        
        print(f"Scaled {len(scale_cols)} features")
        print(f"Scaled features: {scale_cols[:10]}...")  # 只显示前10个特征名
        return train_scaled, test_scaled
    
    def select_features(self, train_df, target_col='Calories', k=20, method='f_regression'):
        """
        特征选择
        
        参数:
            train_df: 训练数据
            target_col: 目标列名
            k: 选择的特征数量
            method: 选择方法 ('f_regression' 或 'mutual_info')
            
        返回:
            选择的特征名列表
        """
        print(f"Performing feature selection, selecting top {k} important features...")
        
        # 准备特征和目标
        feature_cols = [col for col in train_df.columns if col not in ['id', target_col]]
        X = train_df[feature_cols]
        y = train_df[target_col]
        
        # 选择评分函数
        if method == 'f_regression':
            score_func = f_regression
        elif method == 'mutual_info':
            score_func = mutual_info_regression
        else:
            raise ValueError("method must be 'f_regression' or 'mutual_info'")
        
        # 创建特征选择器
        self.feature_selector = SelectKBest(score_func=score_func, k=k)
        
        # 拟合特征选择器
        self.feature_selector.fit(X, y)
        
        # 获取选择的特征
        selected_mask = self.feature_selector.get_support()
        self.selected_features = [feature_cols[i] for i, selected in enumerate(selected_mask) if selected]
        
        # 获取特征得分
        feature_scores = self.feature_selector.scores_
        feature_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Score': feature_scores,
            'Selected': selected_mask
        }).sort_values('Score', ascending=False)
        
        print("Top 10 important features:")
        print(feature_importance.head(10))
        
        return self.selected_features
    
    def feature_engineering_pipeline(self, train_df, test_df, feature_selection=True, k_features=25):
        """
        完整的特征工程流程
        
        参数:
            train_df: 训练数据
            test_df: 测试数据
            feature_selection: 是否进行特征选择
            k_features: 选择的特征数量
            
        返回:
            处理后的训练和测试数据
        """
        print("Starting feature engineering pipeline...")
        
        # 1. 创建生理学特征
        train_engineered = self.create_physiological_features(train_df)
        test_engineered = self.create_physiological_features(test_df)
        
        # 2. 创建交互特征
        train_engineered = self.create_interaction_features(train_engineered)
        test_engineered = self.create_interaction_features(test_engineered)
        
        # 3. 创建多项式特征
        train_engineered = self.create_polynomial_features(train_engineered, degree=2)
        test_engineered = self.create_polynomial_features(test_engineered, degree=2)
        
        # 4. 创建统计特征
        train_engineered = self.create_statistical_features(train_engineered)
        test_engineered = self.create_statistical_features(test_engineered)
        
        print(f"Training set shape after feature engineering: {train_engineered.shape}")
        print(f"Test set shape after feature engineering: {test_engineered.shape}")
        
        # 5. 特征标准化
        train_scaled, test_scaled = self.scale_features(train_engineered, test_engineered)
        
        # 6. 特征选择（可选）
        if feature_selection:
            selected_features = self.select_features(train_scaled, k=k_features)
            
            # 应用特征选择 - 只选择测试集中也存在的特征
            keep_cols = ['id', 'Calories'] if 'Calories' in train_scaled.columns else ['id']
            available_features = [f for f in selected_features if f in test_scaled.columns]
            
            train_final = train_scaled[available_features + [col for col in keep_cols if col in train_scaled.columns]]
            test_final = test_scaled[available_features + [col for col in keep_cols if col in test_scaled.columns]]
            
            print(f"Among selected features, {len(available_features)} are available in test set")
            print(f"Training set shape after feature selection: {train_final.shape}")
            print(f"Test set shape after feature selection: {test_final.shape}")
        else:
            train_final, test_final = train_scaled, test_scaled
        
        print("Feature engineering pipeline completed!")
        return train_final, test_final

def main():
    """主函数"""
    import os
    
    # 检查并删除已存在的特征文件
    feature_files = ['train_features.csv', 'test_features.csv']
    for file in feature_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed existing file: {file}")
    
    # 加载预处理后的数据
    train_df = pd.read_csv('train_preprocessed.csv')
    test_df = pd.read_csv('test_preprocessed.csv')
    
    # 创建特征工程器
    feature_engineer = FeatureEngineer()
    
    # 执行特征工程
    train_final, test_final = feature_engineer.feature_engineering_pipeline(
        train_df, test_df, feature_selection=True, k_features=25
    )
    
    # 保存特征工程后的数据
    train_final.to_csv('train_features.csv', index=False)
    test_final.to_csv('test_features.csv', index=False)
    print("Feature engineering data saved to train_features.csv and test_features.csv")

if __name__ == "__main__":
    main() 