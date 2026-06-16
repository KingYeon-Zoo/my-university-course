#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实验一：语料库处理与词向量表示 - 实验内容
作者：[学生姓名]
日期：2025-10-30

实验目的：
1. 理解词频统计和N-gram文法的概念
2. 掌握从文本中统计生成词典的技术
3. 了解文本不同的编码方式及处理方法
4. 学习现代词向量表示方法及其应用
"""

import os
import re
import jieba
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ================================
# 1. 环境准备与工具函数
# ================================

def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    
    参数:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")

# 创建输出目录
OUTPUT_DIR = "output"
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
DICTS_DIR = os.path.join(OUTPUT_DIR, "dicts")

ensure_dir(OUTPUT_DIR)
ensure_dir(FIGURES_DIR)
ensure_dir(MODELS_DIR)
ensure_dir(DICTS_DIR)

# ================================
# 2. 语料库预处理
# ================================

def load_corpus(file_path, encoding='utf-8'):
    """
    加载语料库文件（增强版：支持多种编码自动检测）
    
    参数:
        file_path: 语料库文件路径
        encoding: 文件编码
    
    返回:
        文本内容
    """
    # 尝试多种编码方式
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'utf-16']
    
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


def clean_text(text, keep_english=True, keep_numbers=True):
    """
    清洗文本，去除特殊字符、标点符号等（优化版）
    
    参数:
        text: 原始文本
        keep_english: 是否保留英文字母
        keep_numbers: 是否保留数字
    
    返回:
        清洗后的文本
    """
    if text is None:
        return ""
    
    # 构建保留字符的正则表达式
    pattern = r'[^\u4e00-\u9fa5'
    if keep_english:
        pattern += r'a-zA-Z'
    if keep_numbers:
        pattern += r'0-9'
    pattern += r']'
    
    # 去除特殊字符
    text = re.sub(pattern, ' ', text)
    # 去除多余的空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def segment_text(text, use_stopwords=False):
    """
    对文本进行分词（优化版：支持停用词过滤）
    
    参数:
        text: 原始文本
        use_stopwords: 是否使用停用词过滤
    
    返回:
        分词后的词列表
    """
    # 使用jieba进行分词
    words = jieba.lcut(text)
    
    # 过滤空字符和单字符（可选）
    words = [word for word in words if word.strip() and len(word) > 0]
    
    # 停用词过滤（可选）
    if use_stopwords:
        stopwords = load_stopwords()
        words = [word for word in words if word not in stopwords]
    
    return words


def load_stopwords():
    """
    加载停用词表（简化版）
    
    返回:
        停用词集合
    """
    # 简单的中文停用词表
    stopwords = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这', '那'
    }
    return stopwords


def analyze_corpus_statistics(text, words):
    """
    分析语料库统计信息（新增）
    
    参数:
        text: 原始文本
        words: 分词后的词列表
    
    返回:
        统计信息字典
    """
    stats = {
        '字符总数': len(text),
        '词语总数': len(words),
        '词汇表大小': len(set(words)),
        '平均词长': np.mean([len(word) for word in words]),
        '最长词': max(words, key=len) if words else '',
        '最长词长度': len(max(words, key=len)) if words else 0
    }
    return stats


# ================================
# 3. 词频统计与N-gram模型
# ================================

def count_word_frequency(words):
    """
    统计词频
    
    参数:
        words: 词列表
    
    返回:
        词频字典
    """
    return Counter(words)


def build_ngram_model(words, n=2):
    """
    构建N-gram模型（优化版：支持多种N值）
    
    参数:
        words: 词列表
        n: N-gram中的N值
    
    返回:
        N-gram及其频次的字典
    """
    if len(words) < n:
        print(f"警告: 词列表长度({len(words)})小于n值({n})")
        return Counter()
    
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    
    return Counter(ngrams)


def visualize_word_frequency(word_freq, title, top_n=20, save_path=None):
    """
    可视化词频分布（优化版：更美观的图表）
    
    参数:
        word_freq: 词频字典
        title: 图表标题
        top_n: 显示前N个高频词
        save_path: 保存路径
    """
    words, freqs = zip(*word_freq.most_common(top_n))
    
    plt.figure(figsize=(14, 6))
    bars = plt.bar(range(len(words)), freqs, color='steelblue', alpha=0.8)
    
    # 为最高的几个柱子添加特殊颜色
    for i in range(min(3, len(bars))):
        bars[i].set_color('coral')
    
    plt.xticks(range(len(words)), words, rotation=45, ha='right')
    plt.xlabel('词语', fontsize=12)
    plt.ylabel('频次', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 在柱子上添加数值标签
    for i, (word, freq) in enumerate(zip(words, freqs)):
        plt.text(i, freq, str(freq), ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 图表已保存: {save_path}")
    
    plt.show()


def save_dict_to_file(word_dict, file_path, top_n=None):
    """
    将词典保存到文件（优化版：添加统计信息）
    
    参数:
        word_dict: 词典（词及其频次）
        file_path: 保存路径
        top_n: 保存前N个高频词，None表示保存所有
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        # 写入统计信息
        total_words = sum(word_dict.values())
        unique_words = len(word_dict)
        f.write(f"# 总词数: {total_words}\n")
        f.write(f"# 词汇表大小: {unique_words}\n")
        f.write(f"# 格式: 词语\t频次\t频率\n")
        f.write("#" + "="*50 + "\n")
        
        # 写入词频数据
        for word, freq in word_dict.most_common(top_n):
            frequency = freq / total_words
            f.write(f"{word}\t{freq}\t{frequency:.6f}\n")
    
    print(f"✓ 词典已保存: {file_path} (共{len(word_dict.most_common(top_n))}个词)")


# ================================
# 4. 词向量训练与可视化
# ================================

def prepare_sentences(words, window_size=20):
    """
    将词列表转换为句子列表，用于训练词向量
    
    参数:
        words: 词列表
        window_size: 每个句子的长度
    
    返回:
        句子列表，每个句子是一个词列表
    """
    sentences = []
    for i in range(0, len(words), window_size):
        sentence = words[i:i+window_size]
        if len(sentence) >= 2:  # 确保句子至少有2个词
            sentences.append(sentence)
    
    return sentences


def train_word2vec(sentences, vector_size=100, window=5, min_count=5, 
                   sg=0, epochs=10, workers=4):
    """
    训练Word2Vec模型（优化版：更多参数控制）
    
    参数:
        sentences: 句子列表，每个句子是一个词列表
        vector_size: 词向量维度
        window: 上下文窗口大小
        min_count: 词频阈值，低于该阈值的词将被忽略
        sg: 训练算法，0为CBOW，1为Skip-gram
        epochs: 训练轮数
        workers: 并行线程数
    
    返回:
        训练好的Word2Vec模型
    """
    print(f"\n开始训练Word2Vec模型...")
    print(f"  - 句子数: {len(sentences)}")
    print(f"  - 向量维度: {vector_size}")
    print(f"  - 窗口大小: {window}")
    print(f"  - 最小词频: {min_count}")
    print(f"  - 算法: {'Skip-gram' if sg else 'CBOW'}")
    print(f"  - 训练轮数: {epochs}")
    
    model = Word2Vec(
        sentences=sentences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        sg=sg,
        epochs=epochs,
        workers=workers
    )
    
    print(f"✓ 模型训练完成，词汇表大小: {len(model.wv.index_to_key)}")
    
    return model


def visualize_word_vectors(model, top_n=50, method='PCA', save_path=None):
    """
    可视化词向量（优化版：支持多种降维方法）
    
    参数:
        model: Word2Vec模型
        top_n: 可视化前N个高频词
        method: 降维方法，'PCA'或'TSNE'
        save_path: 保存路径
    """
    # 获取词汇表中的词
    words = [word for word in list(model.wv.index_to_key)[:top_n]]
    # 获取对应的词向量
    word_vectors = [model.wv[word] for word in words]
    
    # 降维
    if method.upper() == 'PCA':
        from sklearn.decomposition import PCA
        reducer = PCA(n_components=2)
        result = reducer.fit_transform(word_vectors)
        title_suffix = f'(PCA降维，解释方差: {sum(reducer.explained_variance_ratio_):.2%})'
    elif method.upper() == 'TSNE':
        from sklearn.manifold import TSNE
        reducer = TSNE(n_components=2, random_state=42)
        result = reducer.fit_transform(word_vectors)
        title_suffix = '(t-SNE降维)'
    else:
        raise ValueError("method必须是'PCA'或'TSNE'")
    
    # 可视化
    plt.figure(figsize=(16, 12))
    
    # 绘制散点
    scatter = plt.scatter(result[:, 0], result[:, 1], 
                         c=range(len(words)), cmap='viridis',
                         s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    
    # 添加词标签
    for i, word in enumerate(words):
        plt.annotate(word, xy=(result[i, 0], result[i, 1]),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=10, alpha=0.8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    
    plt.colorbar(scatter, label='词频排名')
    plt.title(f'词向量空间可视化 {title_suffix}', fontsize=14, fontweight='bold')
    plt.xlabel('维度1', fontsize=12)
    plt.ylabel('维度2', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ 图表已保存: {save_path}")
    
    plt.show()


def analyze_word_similarity(model, words, topn=10):
    """
    分析词向量相似度（优化版：更详细的输出）
    
    参数:
        model: Word2Vec模型
        words: 待分析的词列表
        topn: 显示前N个相似词
    """
    results = []
    
    for word in words:
        if word in model.wv:
            print(f"\n与'{word}'最相似的{topn}个词:")
            print("-" * 50)
            similar_words = model.wv.most_similar(word, topn=topn)
            
            for rank, (similar_word, similarity) in enumerate(similar_words, 1):
                print(f"  {rank:2d}. {similar_word:10s} - 相似度: {similarity:.4f}")
                results.append({
                    '查询词': word,
                    '排名': rank,
                    '相似词': similar_word,
                    '相似度': similarity
                })
        else:
            print(f"\n✗ '{word}'不在词汇表中")
    
    return pd.DataFrame(results) if results else None


def word_analogy(model, positive, negative, topn=5):
    """
    词向量类比推理（新增功能）
    例如：king - man + woman = queen
    
    参数:
        model: Word2Vec模型
        positive: 正向词列表
        negative: 负向词列表
        topn: 返回前N个结果
    
    返回:
        类比结果列表
    """
    try:
        results = model.wv.most_similar(positive=positive, negative=negative, topn=topn)
        print(f"\n词向量类比: {' + '.join(positive)} - {' - '.join(negative)}")
        print("-" * 50)
        for rank, (word, score) in enumerate(results, 1):
            print(f"  {rank}. {word:10s} - 得分: {score:.4f}")
        return results
    except KeyError as e:
        print(f"✗ 词不在词汇表中: {e}")
        return []


# ================================
# 5. 比较词袋模型与词向量模型
# ================================

def compare_bow_word2vec(sentences, w2v_model, sample_size=100):
    """
    比较词袋模型与词向量模型（优化版：更详细的比较）
    
    参数:
        sentences: 句子列表
        w2v_model: Word2Vec模型
        sample_size: 样本大小
    """
    print("\n" + "="*60)
    print("词袋模型 vs 词向量模型对比分析")
    print("="*60)
    
    # 限制句子数量
    sentences_sample = sentences[:min(sample_size, len(sentences))]
    
    # 将句子列表转换为文本列表
    texts = [' '.join(sentence) for sentence in sentences_sample]
    
    # 1. 词袋模型（CountVectorizer）
    print("\n1. 词袋模型 (Bag of Words)")
    print("-" * 60)
    bow_vectorizer = CountVectorizer()
    bow_matrix = bow_vectorizer.fit_transform(texts)
    
    print(f"  - 特征矩阵维度: {bow_matrix.shape}")
    print(f"  - 词汇表大小: {len(bow_vectorizer.vocabulary_)}")
    print(f"  - 矩阵稀疏度: {1 - bow_matrix.nnz / (bow_matrix.shape[0] * bow_matrix.shape[1]):.2%}")
    print(f"  - 特点: 高维稀疏，不考虑词序，无语义信息")
    
    # 2. TF-IDF模型
    print("\n2. TF-IDF模型")
    print("-" * 60)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    
    print(f"  - 特征矩阵维度: {tfidf_matrix.shape}")
    print(f"  - 词汇表大小: {len(tfidf_vectorizer.vocabulary_)}")
    print(f"  - 矩阵稀疏度: {1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]):.2%}")
    print(f"  - 特点: 考虑词的重要性，但仍无语义信息")
    
    # 3. 词向量模型
    print("\n3. 词向量模型 (Word2Vec)")
    print("-" * 60)
    print(f"  - 向量维度: {w2v_model.wv.vector_size}")
    print(f"  - 词汇表大小: {len(w2v_model.wv.index_to_key)}")
    print(f"  - 特点: 低维稠密，包含语义信息，支持词语运算")
    
    # 4. 相似度计算对比
    if len(sentences_sample) >= 2:
        print("\n4. 句子相似度计算对比")
        print("-" * 60)
        
        # 词袋模型相似度
        bow_sim = cosine_similarity(bow_matrix[0:1], bow_matrix[1:2])[0][0]
        print(f"  - 词袋模型相似度: {bow_sim:.4f}")
        
        # TF-IDF相似度
        tfidf_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        print(f"  - TF-IDF相似度: {tfidf_sim:.4f}")
        
        # 词向量模型相似度
        def sentence_vector(sentence, model):
            vectors = [model.wv[word] for word in sentence if word in model.wv]
            if vectors:
                return np.mean(vectors, axis=0)
            else:
                return np.zeros(model.wv.vector_size)
        
        sent1_vec = sentence_vector(sentences_sample[0], w2v_model)
        sent2_vec = sentence_vector(sentences_sample[1], w2v_model)
        w2v_sim = cosine_similarity([sent1_vec], [sent2_vec])[0][0]
        print(f"  - 词向量模型相似度: {w2v_sim:.4f}")
        
        print(f"\n  句子1: {' '.join(sentences_sample[0][:10])}...")
        print(f"  句子2: {' '.join(sentences_sample[1][:10])}...")
    
    print("\n" + "="*60)


def generate_comparison_table():
    """
    生成模型对比表格（新增）
    """
    comparison_data = {
        '特性': ['表示方法', '维度', '稀疏性', '语义信息', '词序信息', '计算复杂度', '存储需求'],
        '词袋模型': ['离散', '高(词汇表大小)', '高度稀疏', '无', '无', '低', '低'],
        'TF-IDF': ['离散', '高(词汇表大小)', '高度稀疏', '部分(权重)', '无', '低', '低'],
        '词向量': ['连续', '低(50-300)', '稠密', '丰富', '部分', '高', '中等']
    }
    
    df = pd.DataFrame(comparison_data)
    print("\n模型特性对比表:")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    
    return df


# ================================
# 主程序
# ================================

def main():
    """
    主函数：执行所有实验步骤
    """
    print("="*70)
    print(" " * 15 + "实验一：语料库处理与词向量表示")
    print("="*70)
    
    # -------------------- 步骤1: 加载语料库 --------------------
    print("\n【步骤1】加载语料库")
    print("-" * 70)
    
    # 加载宋词语料
    ci_path = os.path.join('dataset', 'Ci.txt')
    ci_content = load_corpus(ci_path)
    
    # 加载新闻语料
    news_path = os.path.join('dataset', '1998-01-2003版-带音.txt')
    news_content = load_corpus(news_path)
    
    if ci_content is None or news_content is None:
        print("✗ 语料库加载失败，请检查文件路径")
        return
    
    print(f"\n语料库基本信息:")
    print(f"  宋词语料长度: {len(ci_content):,} 字符")
    print(f"  新闻语料长度: {len(news_content):,} 字符")
    print(f"  宋词语料前100字符: {ci_content[:100]}")
    print(f"  新闻语料前100字符: {news_content[:100]}")
    
    # -------------------- 步骤2: 文本清洗 --------------------
    print("\n【步骤2】文本清洗")
    print("-" * 70)
    
    clean_ci = clean_text(ci_content)
    clean_news = clean_text(news_content)
    
    print(f"清洗后宋词语料长度: {len(clean_ci):,} 字符")
    print(f"清洗后新闻语料长度: {len(clean_news):,} 字符")
    print(f"清洗后宋词语料前100字符: {clean_ci[:100]}")
    
    # -------------------- 步骤3: 分词处理 --------------------
    print("\n【步骤3】分词处理")
    print("-" * 70)
    
    ci_words = segment_text(clean_ci)
    news_words = segment_text(clean_news)
    
    print(f"宋词语料分词结果前20个: {ci_words[:20]}")
    print(f"新闻语料分词结果前20个: {news_words[:20]}")
    
    # 统计信息
    ci_stats = analyze_corpus_statistics(clean_ci, ci_words)
    news_stats = analyze_corpus_statistics(clean_news, news_words)
    
    print(f"\n宋词语料统计:")
    for key, value in ci_stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n新闻语料统计:")
    for key, value in news_stats.items():
        print(f"  {key}: {value}")
    
    # -------------------- 步骤4: 词频统计 --------------------
    print("\n【步骤4】词频统计")
    print("-" * 70)
    
    ci_word_freq = count_word_frequency(ci_words)
    news_word_freq = count_word_frequency(news_words)
    
    print("宋词语料最常见的20个词:")
    for word, freq in ci_word_freq.most_common(20):
        print(f"  {word:8s}: {freq:6d}")
    
    print("\n新闻语料最常见的20个词:")
    for word, freq in news_word_freq.most_common(20):
        print(f"  {word:8s}: {freq:6d}")
    
    # 可视化词频分布
    visualize_word_frequency(
        ci_word_freq, 
        '宋词语料词频分布',
        save_path=os.path.join(FIGURES_DIR, 'ci_word_freq.png')
    )
    
    visualize_word_frequency(
        news_word_freq,
        '新闻语料词频分布',
        save_path=os.path.join(FIGURES_DIR, 'news_word_freq.png')
    )
    
    # -------------------- 步骤5: N-gram模型 --------------------
    print("\n【步骤5】构建N-gram模型")
    print("-" * 70)
    
    # 2-gram
    ci_bigrams = build_ngram_model(ci_words, 2)
    news_bigrams = build_ngram_model(news_words, 2)
    
    print("宋词语料最常见的10个2-gram:")
    for bigram, freq in ci_bigrams.most_common(10):
        print(f"  {bigram:20s}: {freq:6d}")
    
    print("\n新闻语料最常见的10个2-gram:")
    for bigram, freq in news_bigrams.most_common(10):
        print(f"  {bigram:20s}: {freq:6d}")
    
    # 3-gram
    ci_trigrams = build_ngram_model(ci_words, 3)
    news_trigrams = build_ngram_model(news_words, 3)
    
    print("\n宋词语料最常见的10个3-gram:")
    for trigram, freq in ci_trigrams.most_common(10):
        print(f"  {trigram:30s}: {freq:6d}")
    
    # -------------------- 步骤6: 保存词典 --------------------
    print("\n【步骤6】保存词典和N-gram模型")
    print("-" * 70)
    
    save_dict_to_file(ci_word_freq, os.path.join(DICTS_DIR, 'ci_word_dict.txt'))
    save_dict_to_file(news_word_freq, os.path.join(DICTS_DIR, 'news_word_dict.txt'))
    save_dict_to_file(ci_bigrams, os.path.join(DICTS_DIR, 'ci_bigram_dict.txt'))
    save_dict_to_file(news_bigrams, os.path.join(DICTS_DIR, 'news_bigram_dict.txt'))
    save_dict_to_file(ci_trigrams, os.path.join(DICTS_DIR, 'ci_trigram_dict.txt'))
    save_dict_to_file(news_trigrams, os.path.join(DICTS_DIR, 'news_trigram_dict.txt'))
    
    # -------------------- 步骤7: 准备训练数据 --------------------
    print("\n【步骤7】准备词向量训练数据")
    print("-" * 70)
    
    ci_sentences = prepare_sentences(ci_words, window_size=20)
    news_sentences = prepare_sentences(news_words, window_size=20)
    
    print(f"宋词语料句子数: {len(ci_sentences)}")
    print(f"新闻语料句子数: {len(news_sentences)}")
    print(f"宋词语料第一个句子: {ci_sentences[0][:10]}...")
    
    # -------------------- 步骤8: 训练Word2Vec模型 --------------------
    print("\n【步骤8】训练Word2Vec模型")
    print("-" * 70)
    
    # 训练宋词Word2Vec模型
    ci_w2v_model = train_word2vec(
        ci_sentences,
        vector_size=100,
        window=5,
        min_count=3,
        sg=0,  # CBOW
        epochs=10
    )
    
    # 训练新闻Word2Vec模型
    news_w2v_model = train_word2vec(
        news_sentences,
        vector_size=100,
        window=5,
        min_count=5,
        sg=1,  # Skip-gram
        epochs=10
    )
    
    # 保存模型
    ci_model_path = os.path.join(MODELS_DIR, 'ci_word2vec.model')
    news_model_path = os.path.join(MODELS_DIR, 'news_word2vec.model')
    
    ci_w2v_model.save(ci_model_path)
    news_w2v_model.save(news_model_path)
    
    print(f"\n✓ 模型已保存:")
    print(f"  - {ci_model_path}")
    print(f"  - {news_model_path}")
    
    # -------------------- 步骤9: 词向量可视化 --------------------
    print("\n【步骤9】词向量可视化")
    print("-" * 70)
    
    # 可视化宋词词向量
    print("\n宋词词向量可视化:")
    visualize_word_vectors(
        ci_w2v_model,
        top_n=50,
        method='PCA',
        save_path=os.path.join(FIGURES_DIR, 'ci_word_vectors_pca.png')
    )
    
    # 可视化新闻词向量
    print("\n新闻词向量可视化:")
    visualize_word_vectors(
        news_w2v_model,
        top_n=50,
        method='PCA',
        save_path=os.path.join(FIGURES_DIR, 'news_word_vectors_pca.png')
    )
    
    # -------------------- 步骤10: 词向量相似度分析 --------------------
    print("\n【步骤10】词向量相似度分析")
    print("-" * 70)
    
    # 分析宋词词向量
    print("\n宋词词向量相似度分析:")
    ci_similarity_df = analyze_word_similarity(
        ci_w2v_model,
        ['春', '月', '花', '人', '风', '水'],
        topn=10
    )
    
    if ci_similarity_df is not None:
        ci_similarity_df.to_csv(
            os.path.join(OUTPUT_DIR, 'ci_word_similarity.csv'),
            index=False,
            encoding='utf-8-sig'
        )
    
    # 分析新闻词向量
    print("\n新闻词向量相似度分析:")
    news_similarity_df = analyze_word_similarity(
        news_w2v_model,
        ['中国', '经济', '发展', '技术', '政府'],
        topn=10
    )
    
    if news_similarity_df is not None:
        news_similarity_df.to_csv(
            os.path.join(OUTPUT_DIR, 'news_word_similarity.csv'),
            index=False,
            encoding='utf-8-sig'
        )
    
    # 词向量类比推理（新增）
    print("\n词向量类比推理示例:")
    if '北京' in news_w2v_model.wv and '中国' in news_w2v_model.wv:
        word_analogy(news_w2v_model, ['北京', '中国'], ['上海'])
    
    # -------------------- 步骤11: 比较词袋模型与词向量模型 --------------------
    print("\n【步骤11】比较词袋模型与词向量模型")
    print("-" * 70)
    
    compare_bow_word2vec(ci_sentences[:100], ci_w2v_model, sample_size=100)
    compare_bow_word2vec(news_sentences[:100], news_w2v_model, sample_size=100)
    
    # 生成对比表格
    comparison_df = generate_comparison_table()
    comparison_df.to_csv(
        os.path.join(OUTPUT_DIR, 'model_comparison.csv'),
        index=False,
        encoding='utf-8-sig'
    )
    
    # -------------------- 实验总结 --------------------
    print("\n" + "="*70)
    print(" " * 25 + "实验完成!")
    print("="*70)
    print(f"\n所有输出文件已保存到: {OUTPUT_DIR}")
    print(f"  - 图表文件: {FIGURES_DIR}")
    print(f"  - 模型文件: {MODELS_DIR}")
    print(f"  - 词典文件: {DICTS_DIR}")
    print("\n实验总结:")
    print("  1. 成功加载并预处理了宋词和新闻两个语料库")
    print("  2. 完成了词频统计和N-gram模型构建")
    print("  3. 训练了两个Word2Vec模型并进行了可视化")
    print("  4. 对比分析了词袋模型和词向量模型的特点")
    print("  5. 所有结果已保存，可用于撰写实验报告")
    print("="*70)


if __name__ == "__main__":
    main()

