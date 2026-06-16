"""
数据预处理模块
功能：数据加载、异常值检测处理、可视化分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    """数据预处理类"""
    
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.outlier_stats = {}
        
    def load_data(self, train_path='train.csv', test_path='test.csv'):
        """
        加载训练和测试数据
        
        参数:
            train_path: 训练数据路径
            test_path: 测试数据路径
            
        返回:
            train_df, test_df: 训练和测试数据框
        """
        print("Loading data...")
        
        # 加载数据
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        print(f"训练集形状: {train_df.shape}")
        print(f"测试集形状: {test_df.shape}")
        
        return train_df, test_df
    
    def basic_statistics(self, df, dataset_name="数据集"):
        """
        生成基础统计信息
        
        参数:
            df: 数据框
            dataset_name: 数据集名称
        """
        print(f"\n=== {dataset_name} Basic Statistics ===")
        print(f"Data shape: {df.shape}")
        print(f"\nData types:")
        print(df.dtypes)
        
        print(f"\nMissing values:")
        missing_stats = df.isnull().sum()
        if missing_stats.sum() == 0:
            print("No missing values")
        else:
            print(missing_stats[missing_stats > 0])
        
        print(f"\nDescriptive statistics for numeric features:")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        print(df[numeric_cols].describe())
        
        if 'Sex' in df.columns:
            print(f"\nGender distribution:")
            print(df['Sex'].value_counts())
            
        if 'Calories' in df.columns:
            print(f"\nTarget variable distribution:")
            print(df['Calories'].describe())
    
    def detect_outliers(self, df, columns=None, method='iqr'):
        """
        检测异常值
        
        参数:
            df: 数据框
            columns: 要检测的列，None表示所有数值列
            method: 检测方法 ('iqr' 或 'zscore')
            
        返回:
            outliers_dict: 异常值统计字典
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
            # 排除id列
            columns = [col for col in columns if col != 'id']
        
        outliers_dict = {}
        
        for col in columns:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = df[z_scores > 3]
            
            outliers_dict[col] = {
                'count': len(outliers),
                'percentage': len(outliers) / len(df) * 100,
                'indices': outliers.index.tolist()
            }
            
        self.outlier_stats = outliers_dict
        return outliers_dict
    
    def print_outlier_stats(self, outliers_dict):
        """打印异常值统计"""
        print("\n=== Outlier Detection Results ===")
        for col, stats in outliers_dict.items():
            print(f"{col}: {stats['count']} outliers ({stats['percentage']:.2f}%)")
    
    def encode_categorical(self, train_df, test_df, categorical_cols=['Sex']):
        """
        编码分类变量
        
        参数:
            train_df: 训练数据
            test_df: 测试数据
            categorical_cols: 分类列名列表
            
        返回:
            编码后的训练和测试数据
        """
        train_encoded = train_df.copy()
        test_encoded = test_df.copy()
        
        for col in categorical_cols:
            if col in train_df.columns:
                # 合并训练和测试数据进行编码，确保一致性
                combined_values = pd.concat([train_df[col], test_df[col]])
                self.label_encoder.fit(combined_values)
                
                train_encoded[col] = self.label_encoder.transform(train_df[col])
                test_encoded[col] = self.label_encoder.transform(test_df[col])
                
                print(f"Encoded {col}: {dict(zip(self.label_encoder.classes_, self.label_encoder.transform(self.label_encoder.classes_)))}")
        
        return train_encoded, test_encoded
    
    def create_visualizations(self, df, save_plots=True):
        """
        创建数据可视化图表
        
        参数:
            df: 数据框
            save_plots: 是否保存图表
        """
        print("\nGenerating visualization charts...")
        
        # 创建图片输出文件夹
        import os
        if save_plots:
            if not os.path.exists('figures'):
                os.makedirs('figures')
                print("Created figures directory")
        
        # 设置图表样式
        plt.style.use('default')
        
        # 1. 目标变量分布
        if 'Calories' in df.columns:
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))
            
            # 直方图
            axes[0].hist(df['Calories'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0].set_title('Calorie Consumption Distribution')
            axes[0].set_xlabel('Calories')
            axes[0].set_ylabel('Frequency')
            
            # 箱线图
            axes[1].boxplot(df['Calories'])
            axes[1].set_title('Calorie Consumption Box Plot')
            axes[1].set_ylabel('Calories')
            
            plt.tight_layout()
            if save_plots:
                plt.savefig('figures/calories_distribution.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 2. 数值特征分布
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in ['id', 'Calories']]
        
        if numeric_cols:
            n_cols = 3
            n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
            axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else axes
            
            for i, col in enumerate(numeric_cols):
                if i < len(axes):
                    axes[i].hist(df[col], bins=30, alpha=0.7, edgecolor='black')
                    axes[i].set_title(f'{col} Distribution')
                    axes[i].set_xlabel(col)
                    axes[i].set_ylabel('Frequency')
            
            # 隐藏多余的子图
            for i in range(len(numeric_cols), len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            if save_plots:
                plt.savefig('figures/features_distribution.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 3. 相关性热力图
        if 'Calories' in df.columns:
            numeric_df = df.select_dtypes(include=[np.number])
            correlation_matrix = numeric_df.corr()
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, fmt='.2f', cbar_kws={'label': 'Correlation Coefficient'})
            plt.title('Feature Correlation Heatmap')
            plt.tight_layout()
            if save_plots:
                plt.savefig('figures/correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 4. 性别vs卡路里箱线图
        if 'Sex' in df.columns and 'Calories' in df.columns:
            plt.figure(figsize=(8, 6))
            df.boxplot(column='Calories', by='Sex')
            plt.title('Calorie Consumption by Gender')
            plt.xlabel('Gender')
            plt.ylabel('Calories')
            plt.tight_layout()
            if save_plots:
                plt.savefig('figures/calories_by_sex.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def preprocess_pipeline(self, train_path='train.csv', test_path='test.csv'):
        """
        完整的数据预处理流程
        
        参数:
            train_path: 训练数据路径
            test_path: 测试数据路径
            
        返回:
            处理后的训练和测试数据
        """
        # 1. 加载数据
        train_df, test_df = self.load_data(train_path, test_path)
        
        # 2. 基础统计分析
        self.basic_statistics(train_df, "训练集")
        self.basic_statistics(test_df, "测试集")
        
        # 3. 异常值检测
        outliers = self.detect_outliers(train_df)
        self.print_outlier_stats(outliers)
        
        # 4. 可视化分析
        self.create_visualizations(train_df)
        
        # 5. 分类变量编码
        train_encoded, test_encoded = self.encode_categorical(train_df, test_df)
        
        print("\nData preprocessing completed!")
        return train_encoded, test_encoded

def main():
    """主函数"""
    preprocessor = DataPreprocessor()
    train_df, test_df = preprocessor.preprocess_pipeline()
    
    # 保存预处理后的数据
    train_df.to_csv('train_preprocessed.csv', index=False)
    test_df.to_csv('test_preprocessed.csv', index=False)
    print("Preprocessed data saved to train_preprocessed.csv and test_preprocessed.csv")

if __name__ == "__main__":
    main() 