"""
泰坦尼克号生存预测 - 简单逻辑回归模型
使用基础的线性/逻辑回归方法进行预测
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data():
    """
    加载和预处理数据
    """
    print("正在加载数据...")
    
    # 加载训练和测试数据
    train_df = pd.read_csv('train.csv')
    test_df = pd.read_csv('test.csv')
    
    print(f"训练集大小: {train_df.shape}")
    print(f"测试集大小: {test_df.shape}")
    
    # 合并数据以便统一处理
    test_df['Survived'] = -1  # 临时标记
    combined_df = pd.concat([train_df, test_df], ignore_index=True)
    
    print("数据加载完成")
    return combined_df, len(train_df)

def basic_preprocessing(df):
    """
    基础数据预处理
    """
    print("开始数据预处理...")
    
    # 处理缺失值
    print("处理缺失值...")
    
    # Age: 用中位数填充
    median_age = df['Age'].median()
    df['Age'].fillna(median_age, inplace=True)
    print(f"Age缺失值用中位数 {median_age:.1f} 填充")
    
    # Embarked: 用众数填充
    mode_embarked = df['Embarked'].mode()[0]
    df['Embarked'].fillna(mode_embarked, inplace=True)
    print(f"Embarked缺失值用众数 '{mode_embarked}' 填充")
    
    # Fare: 用中位数填充
    median_fare = df['Fare'].median()
    df['Fare'].fillna(median_fare, inplace=True)
    print(f"Fare缺失值用中位数 {median_fare:.1f} 填充")
    
    # 删除不需要的列
    columns_to_drop = ['PassengerId', 'Name', 'Ticket', 'Cabin']
    df = df.drop(columns=columns_to_drop)
    print(f"删除列: {columns_to_drop}")
    
    # 编码分类变量
    print("编码分类变量...")
    
    # 性别编码
    le_sex = LabelEncoder()
    df['Sex'] = le_sex.fit_transform(df['Sex'])
    print("Sex: female=0, male=1")
    
    # 登船港口编码
    le_embarked = LabelEncoder()
    df['Embarked'] = le_embarked.fit_transform(df['Embarked'])
    print("Embarked: C=0, Q=1, S=2")
    
    print("预处理完成")
    return df

def train_simple_model(X_train, y_train):
    """
    训练简单逻辑回归模型
    """
    print("训练逻辑回归模型...")
    
    # 创建逻辑回归模型
    model = LogisticRegression(random_state=42, max_iter=1000)
    
    # 训练模型
    model.fit(X_train, y_train)
    
    # 交叉验证评估
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"交叉验证准确率: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # 显示特征重要性（逻辑回归系数）
    feature_names = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
    coefficients = model.coef_[0]
    
    print("\n特征重要性（逻辑回归系数）:")
    for name, coef in zip(feature_names, coefficients):
        print(f"{name}: {coef:.4f}")
    
    return model

def predict_and_save(model, X_test, test_passenger_ids):
    """
    预测并保存结果
    """
    print("进行预测...")
    
    # 预测
    predictions = model.predict(X_test)
    
    # 创建提交格式的DataFrame
    submission = pd.DataFrame({
        'PassengerId': test_passenger_ids,
        'Survived': predictions
    })
    
    # 保存结果
    submission.to_csv('simple_model_submission.csv', index=False)
    print("预测结果已保存到 'simple_model_submission.csv'")
    
    # 显示预测统计
    survival_rate = predictions.mean()
    print(f"预测生存率: {survival_rate:.4f}")
    print(f"预测存活人数: {predictions.sum()}")
    print(f"预测死亡人数: {len(predictions) - predictions.sum()}")
    
    return predictions

def analyze_simple_model_performance(df, train_size):
    """
    分析简单模型的性能和局限性
    """
    print("\n=== 简单模型性能分析 ===")
    
    train_df = df[df['Survived'] != -1].copy()
    
    # 按性别分析生存率
    print("\n按性别分析生存率:")
    gender_survival = train_df.groupby('Sex')['Survived'].agg(['mean', 'count'])
    gender_labels = {0: 'Female', 1: 'Male'}
    for sex, stats in gender_survival.iterrows():
        print(f"{gender_labels[sex]}: {stats['mean']:.4f} ({stats['count']} 人)")
    
    # 按舱位等级分析生存率
    print("\n按舱位等级分析生存率:")
    class_survival = train_df.groupby('Pclass')['Survived'].agg(['mean', 'count'])
    for pclass, stats in class_survival.iterrows():
        print(f"等级 {pclass}: {stats['mean']:.4f} ({stats['count']} 人)")
    
    # 分析年龄分布
    print("\n年龄分布分析:")
    survived = train_df[train_df['Survived'] == 1]['Age']
    died = train_df[train_df['Survived'] == 0]['Age']
    print(f"存活者平均年龄: {survived.mean():.1f}")
    print(f"死亡者平均年龄: {died.mean():.1f}")

def main():
    """
    主函数
    """
    print("=== 泰坦尼克号生存预测 - 简单逻辑回归模型 ===\n")
    
    # 1. 加载数据
    combined_df, train_size = load_and_preprocess_data()
    
    # 2. 预处理
    processed_df = basic_preprocessing(combined_df)
    
    # 3. 分离训练和测试数据
    train_df = processed_df[:train_size].copy()
    test_df = processed_df[train_size:].copy()
    
    # 获取测试集的PassengerId（需要从原始数据获取）
    test_passenger_ids = pd.read_csv('test.csv')['PassengerId']
    
    # 准备训练数据
    X_train = train_df.drop('Survived', axis=1)
    y_train = train_df['Survived']
    
    # 准备测试数据
    X_test = test_df.drop('Survived', axis=1)
    
    print(f"\n训练特征形状: {X_train.shape}")
    print(f"测试特征形状: {X_test.shape}")
    
    # 4. 训练模型
    model = train_simple_model(X_train, y_train)
    
    # 5. 预测
    predictions = predict_and_save(model, X_test, test_passenger_ids)
    
    # 6. 分析模型性能
    analyze_simple_model_performance(processed_df, train_size)
    
    print("\n=== 简单模型分析完成 ===")

if __name__ == "__main__":
    main() 