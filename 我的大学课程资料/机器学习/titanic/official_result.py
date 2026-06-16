"""
泰坦尼克号生存预测 - 随机森林模型
基于Kaggle官方教程思想的高级实现
参考: https://www.kaggle.com/code/alexisbcook/titanic-tutorial
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder
import re
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """
    加载原始数据
    """
    print("正在加载数据...")
    
    train_df = pd.read_csv('train.csv')
    test_df = pd.read_csv('test.csv')
    
    print(f"训练集大小: {train_df.shape}")
    print(f"测试集大小: {test_df.shape}")
    print("数据加载完成")
    
    return train_df, test_df

def extract_title(name):
    """
    从姓名中提取头衔
    """
    title_search = re.search(' ([A-Za-z]+)\.', name)
    if title_search:
        return title_search.group(1)
    return ""

def advanced_feature_engineering(train_df, test_df):
    """
    高级特征工程
    基于官方教程的思想进行特征提取
    """
    print("开始高级特征工程...")
    
    # 合并数据以便统一处理
    test_df['Survived'] = -1  # 临时标记
    combined_df = pd.concat([train_df, test_df], ignore_index=True)
    train_size = len(train_df)
    
    # 1. 从姓名中提取头衔
    print("提取头衔特征...")
    combined_df['Title'] = combined_df['Name'].apply(extract_title)
    
    # 将稀少的头衔归类
    title_mapping = {
        'Mr': 'Mr',
        'Miss': 'Miss', 
        'Mrs': 'Mrs',
        'Master': 'Master',
        'Dr': 'Rare',
        'Rev': 'Rare',
        'Col': 'Rare',
        'Major': 'Rare',
        'Mlle': 'Miss',
        'Countess': 'Rare',
        'Ms': 'Miss',
        'Lady': 'Rare',
        'Jonkheer': 'Rare',
        'Don': 'Rare',
        'Dona': 'Rare',
        'Mme': 'Mrs',
        'Capt': 'Rare',
        'Sir': 'Rare'
    }
    
    combined_df['Title'] = combined_df['Title'].map(title_mapping)
    combined_df['Title'].fillna('Rare', inplace=True)
    
    print("头衔分布:")
    print(combined_df['Title'].value_counts())
    
    # 2. 创建家庭规模特征
    print("创建家庭规模特征...")
    combined_df['FamilySize'] = combined_df['SibSp'] + combined_df['Parch'] + 1
    
    # 创建是否独自一人的特征
    combined_df['IsAlone'] = (combined_df['FamilySize'] == 1).astype(int)
    
    # 3. 年龄分组
    print("创建年龄分组...")
    combined_df['AgeGroup'] = pd.cut(combined_df['Age'], 
                                   bins=[0, 12, 18, 35, 60, 100], 
                                   labels=['Child', 'Teen', 'Adult', 'MiddleAge', 'Senior'])
    
    # 4. 票价分组
    print("创建票价分组...")
    combined_df['FareGroup'] = pd.qcut(combined_df['Fare'], 
                                     q=4, 
                                     labels=['Low', 'Medium', 'High', 'VeryHigh'])
    
    # 5. 处理缺失值（更智能的方法）
    print("智能处理缺失值...")
    
    # Age: 根据头衔和舱位等级填充
    age_by_title_class = combined_df.groupby(['Title', 'Pclass'])['Age'].median()
    
    for index, row in combined_df.iterrows():
        if pd.isna(row['Age']):
            title = row['Title']
            pclass = row['Pclass']
            if (title, pclass) in age_by_title_class.index:
                combined_df.loc[index, 'Age'] = age_by_title_class[title, pclass]
            else:
                combined_df.loc[index, 'Age'] = combined_df['Age'].median()
    
    # Embarked: 用众数填充
    combined_df['Embarked'].fillna(combined_df['Embarked'].mode()[0], inplace=True)
    
    # Fare: 根据舱位等级填充
    fare_by_class = combined_df.groupby('Pclass')['Fare'].median()
    for index, row in combined_df.iterrows():
        if pd.isna(row['Fare']):
            combined_df.loc[index, 'Fare'] = fare_by_class[row['Pclass']]
    
    # 重新计算年龄和票价分组（因为缺失值已填充）
    combined_df['AgeGroup'] = pd.cut(combined_df['Age'], 
                                   bins=[0, 12, 18, 35, 60, 100], 
                                   labels=['Child', 'Teen', 'Adult', 'MiddleAge', 'Senior'])
    
    combined_df['FareGroup'] = pd.qcut(combined_df['Fare'], 
                                     q=4, 
                                     labels=['Low', 'Medium', 'High', 'VeryHigh'])
    
    print("特征工程完成")
    return combined_df, train_size

def prepare_features(df, train_size):
    """
    准备最终的特征集
    """
    print("准备特征集...")
    
    # 选择要使用的特征
    features_to_use = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 
                       'Embarked', 'Title', 'FamilySize', 'IsAlone']
    
    # 创建特征DataFrame
    feature_df = df[features_to_use].copy()
    
    # 编码分类变量
    categorical_features = ['Sex', 'Embarked', 'Title']
    
    for feature in categorical_features:
        le = LabelEncoder()
        feature_df[feature] = le.fit_transform(feature_df[feature])
        print(f"{feature} 编码完成")
    
    # 分离训练和测试集
    X_train = feature_df[:train_size]
    X_test = feature_df[train_size:]
    y_train = df[:train_size]['Survived']
    
    print(f"训练特征形状: {X_train.shape}")
    print(f"测试特征形状: {X_test.shape}")
    
    return X_train, X_test, y_train

def train_random_forest(X_train, y_train):
    """
    训练随机森林模型并进行超参数调优
    """
    print("训练随机森林模型...")
    
    # 基础随机森林模型
    rf_basic = RandomForestClassifier(random_state=42, n_estimators=100)
    
    # 基础模型交叉验证
    cv_scores_basic = cross_val_score(rf_basic, X_train, y_train, cv=5)
    print(f"基础随机森林交叉验证准确率: {cv_scores_basic.mean():.4f} (+/- {cv_scores_basic.std() * 2:.4f})")
    
    # 超参数调优
    print("进行超参数调优...")
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 5, 10, 15],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    print(f"最佳参数: {grid_search.best_params_}")
    print(f"最佳交叉验证分数: {grid_search.best_score_:.4f}")
    
    # 使用最佳参数训练最终模型
    best_rf = grid_search.best_estimator_
    
    # 特征重要性分析
    feature_names = X_train.columns
    importances = best_rf.feature_importances_
    
    print("\n特征重要性排序:")
    feature_importance = list(zip(feature_names, importances))
    feature_importance.sort(key=lambda x: x[1], reverse=True)
    
    for feature, importance in feature_importance:
        print(f"{feature}: {importance:.4f}")
    
    return best_rf

def predict_and_save_rf(model, X_test, test_passenger_ids, filename='random_forest_submission.csv'):
    """
    使用随机森林模型预测并保存结果
    """
    print("进行随机森林预测...")
    
    # 预测
    predictions = model.predict(X_test)
    
    # 创建提交格式的DataFrame
    submission = pd.DataFrame({
        'PassengerId': test_passenger_ids,
        'Survived': predictions
    })
    
    # 保存结果
    submission.to_csv(filename, index=False)
    print(f"预测结果已保存到 '{filename}'")
    
    # 显示预测统计
    survival_rate = predictions.mean()
    print(f"预测生存率: {survival_rate:.4f}")
    print(f"预测存活人数: {predictions.sum()}")
    print(f"预测死亡人数: {len(predictions) - predictions.sum()}")
    
    return predictions

def analyze_model_insights(model, X_train, feature_names):
    """
    分析模型的洞察
    """
    print("\n=== 随机森林模型洞察分析 ===")
    
    # 特征重要性深度分析
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("\n最重要的5个特征:")
    for i in range(min(5, len(feature_names))):
        idx = indices[i]
        print(f"{i+1}. {feature_names[idx]}: {importances[idx]:.4f}")
    
    print("\n随机森林的优势:")
    print("1. 自动捕捉特征交互：性别×舱位等级、年龄×头衔等")
    print("2. 处理非线性关系：年龄的复杂效应、家庭规模的最优点")
    print("3. 鲁棒性强：对异常值和缺失值不敏感")
    print("4. 集成学习：通过多个决策树减少过拟合")

def compare_predictions(simple_pred, rf_pred):
    """
    比较两个模型的预测结果
    """
    print("\n=== 模型预测结果对比 ===")
    
    # 预测一致性
    agreement = np.mean(simple_pred == rf_pred)
    print(f"两个模型预测一致性: {agreement:.4f}")
    
    # 生存率对比
    simple_survival_rate = np.mean(simple_pred)
    rf_survival_rate = np.mean(rf_pred)
    
    print(f"简单模型预测生存率: {simple_survival_rate:.4f}")
    print(f"随机森林预测生存率: {rf_survival_rate:.4f}")
    print(f"生存率差异: {abs(simple_survival_rate - rf_survival_rate):.4f}")
    
    # 分析差异
    disagreement_indices = np.where(simple_pred != rf_pred)[0]
    print(f"预测不一致的样本数: {len(disagreement_indices)}")

def main():
    """
    主函数 - 官方随机森林方法实现
    """
    print("=== 泰坦尼克号生存预测 - 随机森林模型（官方教程方法） ===\n")
    
    # 1. 加载数据
    train_df, test_df = load_data()
    
    # 2. 高级特征工程
    combined_df, train_size = advanced_feature_engineering(train_df, test_df)
    
    # 3. 准备特征
    X_train, X_test, y_train = prepare_features(combined_df, train_size)
    
    # 4. 训练随机森林模型
    rf_model = train_random_forest(X_train, y_train)
    
    # 5. 预测
    test_passenger_ids = test_df['PassengerId']
    rf_predictions = predict_and_save_rf(rf_model, X_test, test_passenger_ids)
    
    # 6. 分析模型洞察
    analyze_model_insights(rf_model, X_train, X_train.columns)
    
    # 7. 如果simple_model.py已运行，比较结果
    try:
        simple_submission = pd.read_csv('simple_model_submission.csv')
        simple_pred = simple_submission['Survived'].values
        compare_predictions(simple_pred, rf_predictions)
    except FileNotFoundError:
        print("\n注意: 未找到simple_model_submission.csv，无法进行模型对比")
        print("请先运行 simple_model.py")
    
    print("\n=== 随机森林模型分析完成 ===")
    print("随机森林相比简单模型的优势:")
    print("1. 能够自动发现复杂的特征交互关系")
    print("2. 处理非线性模式，如年龄的U型效应")
    print("3. 更好地利用所有特征信息")
    print("4. 通过集成学习提高预测稳定性")
    print("5. 对数据质量问题更加鲁棒")

if __name__ == "__main__":
    main() 