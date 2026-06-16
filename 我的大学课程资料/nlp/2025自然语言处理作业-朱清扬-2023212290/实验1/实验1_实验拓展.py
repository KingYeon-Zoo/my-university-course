#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实验一：语料库处理与词向量表示 - 实验拓展
作者：[学生姓名]
日期：2025-10-30

实验拓展内容：
1. 使用预训练词向量
2. 词向量聚类分析
3. 词向量用于文本相似度计算
4. 探索不同参数对词向量质量的影响
"""

import os
import re
import jieba
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from gensim.models import Word2Vec, KeyedVectors
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置seaborn样式
sns.set_style("whitegrid")

# ================================
# 工具函数
# ================================

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")

# 创建输出目录
OUTPUT_DIR = "output_extension"
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")

ensure_dir(OUTPUT_DIR)
ensure_dir(FIGURES_DIR)
ensure_dir(MODELS_DIR)
ensure_dir(DATA_DIR)


def load_corpus(file_path, encoding='utf-8'):
    """加载语料库文件"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
            print(f"✓ 成功使用 {enc} 编码读取文件: {file_path}")
            return content
        except (UnicodeDecodeError, FileNotFoundError) as e:
            if isinstance(e, FileNotFoundError):
                print(f"✗ 文件不存在: {file_path}")
                return None
            continue
    
    print(f"✗ 无法识别文件编码: {file_path}")
    return None


def clean_text(text):
    """清洗文本"""
    if text is None:
        return ""
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def segment_text(text):
    """分词"""
    words = jieba.lcut(text)
    words = [word for word in words if word.strip()]
    return words


def prepare_sentences(words, window_size=20):
    """准备训练数据"""
    sentences = []
    for i in range(0, len(words), window_size):
        sentence = words[i:i+window_size]
        if len(sentence) >= 2:
            sentences.append(sentence)
    return sentences


# ================================
# 拓展1: 使用预训练词向量
# ================================

def load_pretrained_vectors(file_path, binary=False, limit=None):
    """
    加载预训练词向量
    
    参数:
        file_path: 词向量文件路径
        binary: 是否为二进制格式
        limit: 加载词数限制
    
    返回:
        KeyedVectors对象
    """
    print(f"\n加载预训练词向量: {file_path}")
    
    try:
        if binary:
            wv = KeyedVectors.load_word2vec_format(file_path, binary=True, limit=limit)
        else:
            wv = KeyedVectors.load_word2vec_format(file_path, binary=False, limit=limit)
        
        print(f"✓ 成功加载预训练词向量")
        print(f"  - 词汇量: {len(wv.index_to_key)}")
        print(f"  - 向量维度: {wv.vector_size}")
        
        return wv
    except Exception as e:
        print(f"✗ 加载失败: {e}")
        print("  提示: 可以从以下渠道下载中文预训练词向量:")
        print("  1. 腾讯AI Lab: https://ai.tencent.com/ailab/nlp/embedding.html")
        print("  2. 哈工大讯飞: https://github.com/Embedding/Chinese-Word-Vectors")
        return None


def compare_pretrained_and_custom(pretrained_wv, custom_model, test_words):
    """
    比较预训练词向量和自训练词向量
    
    参数:
        pretrained_wv: 预训练词向量
        custom_model: 自训练Word2Vec模型
        test_words: 测试词列表
    """
    print("\n" + "="*70)
    print("预训练词向量 vs 自训练词向量对比")
    print("="*70)
    
    results = []
    
    for word in test_words:
        result = {'词语': word}
        
        # 预训练词向量
        if pretrained_wv and word in pretrained_wv:
            similar_pretrained = pretrained_wv.most_similar(word, topn=5)
            result['预训练-相似词'] = ', '.join([w for w, _ in similar_pretrained])
            result['预训练-平均相似度'] = np.mean([s for _, s in similar_pretrained])
        else:
            result['预训练-相似词'] = 'N/A'
            result['预训练-平均相似度'] = 0
        
        # 自训练词向量
        if word in custom_model.wv:
            similar_custom = custom_model.wv.most_similar(word, topn=5)
            result['自训练-相似词'] = ', '.join([w for w, _ in similar_custom])
            result['自训练-平均相似度'] = np.mean([s for _, s in similar_custom])
        else:
            result['自训练-相似词'] = 'N/A'
            result['自训练-平均相似度'] = 0
        
        results.append(result)
    
    df = pd.DataFrame(results)
    print("\n对比结果:")
    print(df.to_string(index=False))
    
    # 保存结果
    df.to_csv(os.path.join(DATA_DIR, 'pretrained_vs_custom.csv'), 
              index=False, encoding='utf-8-sig')
    
    return df


# ================================
# 拓展2: 词向量聚类分析
# ================================

def cluster_word_vectors(model, n_clusters=5, method='kmeans', top_n=200):
    """
    对词向量进行聚类分析
    
    参数:
        model: Word2Vec模型
        n_clusters: 聚类数量
        method: 聚类方法 ('kmeans', 'hierarchical')
        top_n: 使用前N个高频词
    
    返回:
        聚类结果
    """
    print(f"\n{'='*70}")
    print(f"词向量聚类分析 (方法: {method}, 聚类数: {n_clusters})")
    print(f"{'='*70}")
    
    # 获取词和向量
    words = list(model.wv.index_to_key[:top_n])
    vectors = np.array([model.wv[word] for word in words])
    
    print(f"\n聚类词数: {len(words)}")
    print(f"向量维度: {vectors.shape[1]}")
    
    # 聚类
    if method.lower() == 'kmeans':
        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = clusterer.fit_predict(vectors)
    elif method.lower() == 'hierarchical':
        clusterer = AgglomerativeClustering(n_clusters=n_clusters)
        labels = clusterer.fit_predict(vectors)
    else:
        raise ValueError("method must be 'kmeans' or 'hierarchical'")
    
    # 评估聚类质量
    silhouette = silhouette_score(vectors, labels)
    davies_bouldin = davies_bouldin_score(vectors, labels)
    
    print(f"\n聚类质量评估:")
    print(f"  轮廓系数 (Silhouette Score): {silhouette:.4f} (越接近1越好)")
    print(f"  Davies-Bouldin指数: {davies_bouldin:.4f} (越小越好)")
    
    # 分析每个聚类
    cluster_info = []
    for cluster_id in range(n_clusters):
        cluster_words = [words[i] for i in range(len(words)) if labels[i] == cluster_id]
        cluster_info.append({
            '聚类ID': cluster_id,
            '词数': len(cluster_words),
            '示例词': ', '.join(cluster_words[:10])
        })
    
    df_clusters = pd.DataFrame(cluster_info)
    print("\n各聚类详情:")
    print(df_clusters.to_string(index=False))
    
    # 保存结果
    results_df = pd.DataFrame({
        '词语': words,
        '聚类': labels
    })
    results_df.to_csv(
        os.path.join(DATA_DIR, f'word_clusters_{method}.csv'),
        index=False, encoding='utf-8-sig'
    )
    
    return words, vectors, labels, silhouette, davies_bouldin


def visualize_clusters(words, vectors, labels, method='PCA', save_path=None):
    """
    可视化聚类结果
    
    参数:
        words: 词列表
        vectors: 词向量数组
        labels: 聚类标签
        method: 降维方法 ('PCA' or 'TSNE')
        save_path: 保存路径
    """
    print(f"\n生成聚类可视化图 (降维方法: {method})...")
    
    # 降维
    if method.upper() == 'PCA':
        reducer = PCA(n_components=2, random_state=42)
        vectors_2d = reducer.fit_transform(vectors)
        title_suffix = f'(PCA, 解释方差: {sum(reducer.explained_variance_ratio_):.2%})'
    else:
        reducer = TSNE(n_components=2, random_state=42, perplexity=30)
        vectors_2d = reducer.fit_transform(vectors)
        title_suffix = '(t-SNE)'
    
    # 绘图
    plt.figure(figsize=(16, 12))
    
    # 使用不同颜色表示不同聚类
    unique_labels = np.unique(labels)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))
    
    for label, color in zip(unique_labels, colors):
        mask = labels == label
        plt.scatter(
            vectors_2d[mask, 0],
            vectors_2d[mask, 1],
            c=[color],
            label=f'聚类 {label}',
            s=100,
            alpha=0.6,
            edgecolors='black',
            linewidth=0.5
        )
    
    # 添加词标签（只标注部分词以避免拥挤）
    sample_indices = np.random.choice(len(words), min(50, len(words)), replace=False)
    for idx in sample_indices:
        plt.annotate(
            words[idx],
            xy=(vectors_2d[idx, 0], vectors_2d[idx, 1]),
            xytext=(3, 3),
            textcoords='offset points',
            fontsize=9,
            alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.2', facecolor=colors[labels[idx]], alpha=0.3)
        )
    
    plt.legend(loc='best', fontsize=10)
    plt.title(f'词向量聚类可视化 {title_suffix}', fontsize=14, fontweight='bold')
    plt.xlabel('维度1', fontsize=12)
    plt.ylabel('维度2', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 图表已保存: {save_path}")
    
    plt.show()


def plot_dendrogram_analysis(vectors, words, max_samples=100, save_path=None):
    """
    绘制层次聚类树状图
    
    参数:
        vectors: 词向量数组
        words: 词列表
        max_samples: 最大样本数
        save_path: 保存路径
    """
    print(f"\n生成层次聚类树状图...")
    
    # 限制样本数以提高可读性
    if len(words) > max_samples:
        indices = np.random.choice(len(words), max_samples, replace=False)
        vectors_sample = vectors[indices]
        words_sample = [words[i] for i in indices]
    else:
        vectors_sample = vectors
        words_sample = words
    
    # 计算层次聚类
    linkage_matrix = linkage(vectors_sample, method='ward')
    
    # 绘图
    plt.figure(figsize=(16, 10))
    dendrogram(
        linkage_matrix,
        labels=words_sample,
        leaf_font_size=8,
        leaf_rotation=90
    )
    plt.title('词向量层次聚类树状图', fontsize=14, fontweight='bold')
    plt.xlabel('词语', fontsize=12)
    plt.ylabel('距离', fontsize=12)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 图表已保存: {save_path}")
    
    plt.show()


# ================================
# 拓展3: 词向量用于文本相似度计算
# ================================

def sentence_to_vector(sentence, model, method='average'):
    """
    将句子转换为向量
    
    参数:
        sentence: 句子（词列表或字符串）
        model: Word2Vec模型
        method: 转换方法 ('average', 'tfidf', 'max')
    
    返回:
        句子向量
    """
    if isinstance(sentence, str):
        sentence = jieba.lcut(sentence)
    
    vectors = []
    for word in sentence:
        if word in model.wv:
            vectors.append(model.wv[word])
    
    if not vectors:
        return np.zeros(model.wv.vector_size)
    
    if method == 'average':
        return np.mean(vectors, axis=0)
    elif method == 'max':
        return np.max(vectors, axis=0)
    elif method == 'tfidf':
        # 简化版TF-IDF加权
        word_counts = Counter(sentence)
        weighted_vectors = []
        for word in sentence:
            if word in model.wv:
                weight = word_counts[word]  # 简化的TF
                weighted_vectors.append(model.wv[word] * weight)
        return np.mean(weighted_vectors, axis=0) if weighted_vectors else np.zeros(model.wv.vector_size)
    else:
        raise ValueError("method must be 'average', 'max', or 'tfidf'")


def calculate_text_similarity(text1, text2, model, method='average'):
    """
    计算两个文本的相似度
    
    参数:
        text1, text2: 文本字符串
        model: Word2Vec模型
        method: 向量化方法
    
    返回:
        相似度分数
    """
    vec1 = sentence_to_vector(text1, model, method)
    vec2 = sentence_to_vector(text2, model, method)
    
    similarity = cosine_similarity([vec1], [vec2])[0][0]
    return similarity


def text_similarity_demo(model, test_pairs):
    """
    文本相似度计算演示
    
    参数:
        model: Word2Vec模型
        test_pairs: 测试文本对列表
    """
    print("\n" + "="*70)
    print("文本相似度计算演示")
    print("="*70)
    
    results = []
    methods = ['average', 'max', 'tfidf']
    
    for idx, (text1, text2) in enumerate(test_pairs, 1):
        print(f"\n【测试对 {idx}】")
        print(f"文本1: {text1}")
        print(f"文本2: {text2}")
        print("-" * 70)
        
        result = {
            '测试对ID': idx,
            '文本1': text1,
            '文本2': text2
        }
        
        for method in methods:
            sim = calculate_text_similarity(text1, text2, model, method)
            result[f'相似度({method})'] = sim
            print(f"  {method:10s}: {sim:.4f}")
        
        results.append(result)
    
    df = pd.DataFrame(results)
    df.to_csv(
        os.path.join(DATA_DIR, 'text_similarity_results.csv'),
        index=False, encoding='utf-8-sig'
    )
    
    return df


def find_most_similar_texts(query, corpus, model, top_n=5, method='average'):
    """
    在语料库中查找最相似的文本
    
    参数:
        query: 查询文本
        corpus: 语料库（文本列表）
        model: Word2Vec模型
        top_n: 返回前N个最相似文本
        method: 向量化方法
    
    返回:
        相似文本列表
    """
    print(f"\n查询文本: {query}")
    print(f"语料库大小: {len(corpus)}")
    print("-" * 70)
    
    query_vec = sentence_to_vector(query, model, method)
    
    similarities = []
    for text in corpus:
        text_vec = sentence_to_vector(text, model, method)
        sim = cosine_similarity([query_vec], [text_vec])[0][0]
        similarities.append((text, sim))
    
    # 排序并返回top_n
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n最相似的 {top_n} 个文本:")
    for rank, (text, sim) in enumerate(similarities[:top_n], 1):
        print(f"  {rank}. 相似度={sim:.4f}: {text[:50]}...")
    
    return similarities[:top_n]


# ================================
# 拓展4: 探索不同参数对词向量质量的影响
# ================================

def train_word2vec_with_params(sentences, **kwargs):
    """
    训练Word2Vec模型（参数化版本）
    
    参数:
        sentences: 句子列表
        **kwargs: Word2Vec参数
    
    返回:
        训练好的模型
    """
    default_params = {
        'vector_size': 100,
        'window': 5,
        'min_count': 5,
        'sg': 0,
        'epochs': 10,
        'workers': 4
    }
    
    # 更新参数
    params = {**default_params, **kwargs}
    
    model = Word2Vec(sentences=sentences, **params)
    return model


def evaluate_word2vec_quality(model, test_words):
    """
    评估Word2Vec模型质量
    
    参数:
        model: Word2Vec模型
        test_words: 测试词列表
    
    返回:
        评估指标字典
    """
    metrics = {
        '词汇表大小': len(model.wv.index_to_key),
        '向量维度': model.wv.vector_size
    }
    
    # 计算测试词的平均相似度
    similarities = []
    for word in test_words:
        if word in model.wv:
            similar = model.wv.most_similar(word, topn=10)
            avg_sim = np.mean([sim for _, sim in similar])
            similarities.append(avg_sim)
    
    if similarities:
        metrics['平均相似度'] = np.mean(similarities)
        metrics['相似度标准差'] = np.std(similarities)
    else:
        metrics['平均相似度'] = 0
        metrics['相似度标准差'] = 0
    
    # 词汇覆盖率
    coverage = sum(1 for word in test_words if word in model.wv) / len(test_words)
    metrics['词汇覆盖率'] = coverage
    
    return metrics


def parameter_sensitivity_analysis(sentences, test_words):
    """
    参数敏感性分析
    
    参数:
        sentences: 训练句子
        test_words: 测试词列表
    """
    print("\n" + "="*70)
    print("Word2Vec参数敏感性分析")
    print("="*70)
    
    results = []
    
    # 1. 向量维度影响
    print("\n【1】向量维度影响")
    print("-" * 70)
    for vector_size in [50, 100, 150, 200, 300]:
        print(f"\n训练模型: vector_size={vector_size}")
        model = train_word2vec_with_params(sentences, vector_size=vector_size)
        metrics = evaluate_word2vec_quality(model, test_words)
        metrics['参数类型'] = '向量维度'
        metrics['参数值'] = vector_size
        results.append(metrics)
        
        print(f"  词汇表大小: {metrics['词汇表大小']}")
        print(f"  平均相似度: {metrics['平均相似度']:.4f}")
        print(f"  词汇覆盖率: {metrics['词汇覆盖率']:.2%}")
    
    # 2. 窗口大小影响
    print("\n【2】窗口大小影响")
    print("-" * 70)
    for window in [2, 5, 8, 10, 15]:
        print(f"\n训练模型: window={window}")
        model = train_word2vec_with_params(sentences, window=window)
        metrics = evaluate_word2vec_quality(model, test_words)
        metrics['参数类型'] = '窗口大小'
        metrics['参数值'] = window
        results.append(metrics)
        
        print(f"  词汇表大小: {metrics['词汇表大小']}")
        print(f"  平均相似度: {metrics['平均相似度']:.4f}")
    
    # 3. 最小词频影响
    print("\n【3】最小词频影响")
    print("-" * 70)
    for min_count in [1, 3, 5, 10, 20]:
        print(f"\n训练模型: min_count={min_count}")
        model = train_word2vec_with_params(sentences, min_count=min_count)
        metrics = evaluate_word2vec_quality(model, test_words)
        metrics['参数类型'] = '最小词频'
        metrics['参数值'] = min_count
        results.append(metrics)
        
        print(f"  词汇表大小: {metrics['词汇表大小']}")
        print(f"  平均相似度: {metrics['平均相似度']:.4f}")
    
    # 4. 算法对比 (CBOW vs Skip-gram)
    print("\n【4】算法对比")
    print("-" * 70)
    for sg, name in [(0, 'CBOW'), (1, 'Skip-gram')]:
        print(f"\n训练模型: {name}")
        model = train_word2vec_with_params(sentences, sg=sg, epochs=10)
        metrics = evaluate_word2vec_quality(model, test_words)
        metrics['参数类型'] = '算法类型'
        metrics['参数值'] = name
        results.append(metrics)
        
        print(f"  词汇表大小: {metrics['词汇表大小']}")
        print(f"  平均相似度: {metrics['平均相似度']:.4f}")
    
    # 5. 训练轮数影响
    print("\n【5】训练轮数影响")
    print("-" * 70)
    for epochs in [5, 10, 20, 30, 50]:
        print(f"\n训练模型: epochs={epochs}")
        model = train_word2vec_with_params(sentences, epochs=epochs)
        metrics = evaluate_word2vec_quality(model, test_words)
        metrics['参数类型'] = '训练轮数'
        metrics['参数值'] = epochs
        results.append(metrics)
        
        print(f"  词汇表大小: {metrics['词汇表大小']}")
        print(f"  平均相似度: {metrics['平均相似度']:.4f}")
    
    # 保存结果
    df = pd.DataFrame(results)
    df.to_csv(
        os.path.join(DATA_DIR, 'parameter_sensitivity.csv'),
        index=False, encoding='utf-8-sig'
    )
    
    print("\n✓ 参数敏感性分析结果已保存")
    
    return df


def visualize_parameter_impact(df, save_dir=None):
    """
    可视化参数影响
    
    参数:
        df: 参数敏感性分析结果DataFrame
        save_dir: 保存目录
    """
    print("\n生成参数影响可视化图...")
    
    param_types = df['参数类型'].unique()
    
    for param_type in param_types:
        data = df[df['参数类型'] == param_type]
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f'{param_type}对词向量质量的影响', fontsize=14, fontweight='bold')
        
        # 词汇表大小
        axes[0].plot(data['参数值'], data['词汇表大小'], marker='o', linewidth=2)
        axes[0].set_xlabel(param_type, fontsize=12)
        axes[0].set_ylabel('词汇表大小', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_title('词汇表大小')
        
        # 平均相似度
        axes[1].plot(data['参数值'], data['平均相似度'], marker='s', color='orange', linewidth=2)
        axes[1].set_xlabel(param_type, fontsize=12)
        axes[1].set_ylabel('平均相似度', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_title('平均相似度')
        
        # 词汇覆盖率
        axes[2].plot(data['参数值'], data['词汇覆盖率'], marker='^', color='green', linewidth=2)
        axes[2].set_xlabel(param_type, fontsize=12)
        axes[2].set_ylabel('词汇覆盖率', fontsize=12)
        axes[2].grid(True, alpha=0.3)
        axes[2].set_title('词汇覆盖率')
        
        plt.tight_layout()
        
        if save_dir:
            save_path = os.path.join(save_dir, f'param_impact_{param_type}.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 图表已保存: {save_path}")
        
        plt.show()


# ================================
# 主程序
# ================================

def main():
    """主函数：执行所有实验拓展"""
    print("="*70)
    print(" " * 15 + "实验一：实验拓展")
    print("="*70)
    
    # 加载语料
    print("\n【准备】加载语料库")
    print("-" * 70)
    
    # 加载新闻语料
    news_path = os.path.join('dataset', '1998-01-2003版-带音.txt')
    news_content = load_corpus(news_path)
    
    if news_content is None:
        print("✗ 语料库加载失败")
        return
    
    # 预处理
    clean_news = clean_text(news_content)
    news_words = segment_text(clean_news)
    news_sentences = prepare_sentences(news_words, window_size=20)
    
    print(f"✓ 语料处理完成")
    print(f"  词数: {len(news_words):,}")
    print(f"  句子数: {len(news_sentences):,}")
    
    # 训练基础模型
    print("\n训练基础Word2Vec模型...")
    base_model = train_word2vec_with_params(
        news_sentences,
        vector_size=100,
        window=5,
        min_count=5,
        sg=1,
        epochs=10
    )
    print(f"✓ 基础模型训练完成，词汇量: {len(base_model.wv.index_to_key)}")
    
    # -------------------- 拓展1: 预训练词向量 --------------------
    print("\n\n" + "="*70)
    print("拓展1：使用预训练词向量")
    print("="*70)
    
    print("\n由于预训练词向量文件较大，此处仅演示加载和比较的代码框架。")
    print("如需使用，请下载中文预训练词向量，如：")
    print("  - 腾讯AI Lab词向量: https://ai.tencent.com/ailab/nlp/embedding.html")
    print("  - 哈工大讯飞词向量: https://github.com/Embedding/Chinese-Word-Vectors")
    
    # 如果有预训练词向量，可以这样加载：
    # pretrained_path = 'path/to/pretrained/vectors.bin'
    # pretrained_wv = load_pretrained_vectors(pretrained_path, binary=True, limit=100000)
    # 
    # if pretrained_wv:
    #     test_words = ['中国', '经济', '发展', '技术', '政府']
    #     compare_pretrained_and_custom(pretrained_wv, base_model, test_words)
    
    # -------------------- 拓展2: 词向量聚类分析 --------------------
    print("\n\n" + "="*70)
    print("拓展2：词向量聚类分析")
    print("="*70)
    
    # K-means聚类
    print("\n2.1 K-means聚类")
    words_km, vectors_km, labels_km, sil_km, db_km = cluster_word_vectors(
        base_model,
        n_clusters=8,
        method='kmeans',
        top_n=200
    )
    
    # 可视化聚类结果
    visualize_clusters(
        words_km, vectors_km, labels_km,
        method='PCA',
        save_path=os.path.join(FIGURES_DIR, 'clusters_kmeans_pca.png')
    )
    
    visualize_clusters(
        words_km, vectors_km, labels_km,
        method='TSNE',
        save_path=os.path.join(FIGURES_DIR, 'clusters_kmeans_tsne.png')
    )
    
    # 层次聚类
    print("\n2.2 层次聚类")
    words_hc, vectors_hc, labels_hc, sil_hc, db_hc = cluster_word_vectors(
        base_model,
        n_clusters=8,
        method='hierarchical',
        top_n=200
    )
    
    # 树状图
    plot_dendrogram_analysis(
        vectors_hc, words_hc,
        max_samples=50,
        save_path=os.path.join(FIGURES_DIR, 'dendrogram.png')
    )
    
    # 聚类质量对比
    print("\n聚类质量对比:")
    print(f"  K-means    - 轮廓系数: {sil_km:.4f}, DB指数: {db_km:.4f}")
    print(f"  Hierarchical - 轮廓系数: {sil_hc:.4f}, DB指数: {db_hc:.4f}")
    
    # -------------------- 拓展3: 文本相似度计算 --------------------
    print("\n\n" + "="*70)
    print("拓展3：词向量用于文本相似度计算")
    print("="*70)
    
    # 测试文本对
    test_pairs = [
        ("中国经济持续增长", "中国经济快速发展"),
        ("计算机技术进步", "信息技术发展"),
        ("教育改革深化", "医疗改革推进"),
        ("环境保护重要", "经济发展迅速"),
        ("人工智能应用", "机器学习研究")
    ]
    
    similarity_df = text_similarity_demo(base_model, test_pairs)
    
    # 文本检索示例
    print("\n\n3.2 文本检索示例")
    print("-" * 70)
    
    # 构建小型语料库
    sample_corpus = [
        "中国经济保持平稳增长态势",
        "计算机技术推动社会进步",
        "教育改革不断深化发展",
        "人工智能改变生活方式",
        "环境保护刻不容缓",
        "科技创新驱动发展",
        "医疗卫生事业进步",
        "文化交流促进理解"
    ]
    
    query_text = "科技发展推动进步"
    similar_texts = find_most_similar_texts(
        query_text, sample_corpus, base_model,
        top_n=3, method='average'
    )
    
    # -------------------- 拓展4: 参数影响分析 --------------------
    print("\n\n" + "="*70)
    print("拓展4：探索不同参数对词向量质量的影响")
    print("="*70)
    
    # 测试词
    test_words = ['中国', '经济', '发展', '技术', '企业', '政府', '市场', 
                  '改革', '建设', '社会', '人民', '工作', '生产', '管理']
    
    # 参数敏感性分析
    param_df = parameter_sensitivity_analysis(
        news_sentences[:5000],  # 使用部分数据以加快速度
        test_words
    )
    
    # 可视化参数影响
    visualize_parameter_impact(param_df, save_dir=FIGURES_DIR)
    
    # 最佳参数建议
    print("\n\n参数选择建议:")
    print("="*70)
    print("""
    1. 向量维度 (vector_size):
       - 小语料库: 50-100维
       - 中等语料库: 100-200维
       - 大语料库: 200-300维
       - 建议: 根据任务和计算资源权衡
    
    2. 窗口大小 (window):
       - 语法相关任务: 2-5
       - 语义相关任务: 5-10
       - 建议: 5为常用默认值
    
    3. 最小词频 (min_count):
       - 大语料库: 5-10
       - 小语料库: 1-3
       - 建议: 过滤噪声但保留有用信息
    
    4. 算法选择:
       - CBOW: 速度快，适合大语料库
       - Skip-gram: 对低频词效果好，适合小语料库
       - 建议: Skip-gram通常效果更好
    
    5. 训练轮数 (epochs):
       - 一般: 5-10轮
       - 小数据: 10-20轮
       - 建议: 10轮为常用值
    """)
    
    # -------------------- 实验总结 --------------------
    print("\n\n" + "="*70)
    print(" " * 25 + "实验拓展完成!")
    print("="*70)
    print(f"\n所有输出文件已保存到: {OUTPUT_DIR}")
    print(f"  - 图表文件: {FIGURES_DIR}")
    print(f"  - 数据文件: {DATA_DIR}")
    
    print("\n实验拓展总结:")
    print("  1. 了解了预训练词向量的使用方法")
    print("  2. 完成了词向量聚类分析，发现词语的语义分组")
    print("  3. 实现了基于词向量的文本相似度计算和检索")
    print("  4. 系统分析了不同参数对词向量质量的影响")
    print("  5. 所有结果已保存，可用于撰写实验报告")
    print("="*70)


if __name__ == "__main__":
    main()

