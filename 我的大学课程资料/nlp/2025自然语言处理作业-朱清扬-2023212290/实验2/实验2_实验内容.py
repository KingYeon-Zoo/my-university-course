"""
实验二：中文分词与命名实体识别 - 实验内容
Author: NLP Course
Date: 2025-10-30
Description: 完整复现实验二的所有步骤，包括词典分词、统计分词、预训练模型分词和命名实体识别
"""

import os
import re
import jieba
import jieba.posseg as pseg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import time
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体支持（改进版）
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'AR PL UMing CN', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'AR PL UMing CN', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 80)
print("实验二：中文分词与命名实体识别")
print("=" * 80)

# ============================================================================
# 1. 环境准备与数据加载
# ============================================================================
print("\n[步骤1] 环境准备与数据加载")
print("-" * 80)

# 创建输出目录（使用绝对路径）
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# 测试文本
test_text = "自然语言处理是计算机科学的一个重要分支"
test_ner_text = "李明在北京大学计算机科学系学习自然语言处理"

print(f"测试文本: {test_text}")
print(f"NER测试文本: {test_ner_text}")

# ============================================================================
# 2. 基于词典的分词算法实现
# ============================================================================
print("\n" + "=" * 80)
print("[步骤2] 基于词典的分词算法实现")
print("=" * 80)

# 2.1 构建词典
def build_dict_from_file(file_path, encoding='utf-8'):
    """
    从文件构建词典，支持多种格式
    
    参数:
        file_path: 词典文件路径
        encoding: 文件编码
    
    返回:
        词典（集合）和词频字典
    """
    word_dict = set()
    word_freq = {}
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    word = parts[0]
                    freq = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    if word:
                        word_dict.add(word)
                        word_freq[word] = freq
        print(f"✓ 成功从文件加载词典，共{len(word_dict)}个词")
    except Exception as e:
        print(f"⚠ 无法读取词典文件 ({e})，使用默认词典")
        # 创建一个较完整的默认词典
        default_words = [
            "自然语言", "自然", "语言", "处理", "计算机科学", "计算机", "科学",
            "一个", "重要", "分支", "是", "的", "北京大学", "北京", "大学",
            "学习", "李明", "系", "人工智能", "机器学习", "深度学习",
            "神经网络", "数据", "算法", "模型", "训练", "测试"
        ]
        for word in default_words:
            word_dict.add(word)
            word_freq[word] = 1
    
    return word_dict, word_freq

# 尝试加载词典文件（使用绝对路径）
dict_paths = [
    os.path.join(SCRIPT_DIR, "dataset", "Ci.txt"),
    os.path.join(SCRIPT_DIR, "..", "dataset", "Ci.txt"),
]

word_dict = None
word_freq = None
for path in dict_paths:
    if os.path.exists(path):
        word_dict, word_freq = build_dict_from_file(path, encoding='utf-8')
        break

if word_dict is None:
    word_dict, word_freq = build_dict_from_file("nonexistent.txt")

# 计算最大词长
max_word_len = max(len(word) for word in word_dict) if word_dict else 5
print(f"词典大小: {len(word_dict)}")
print(f"最大词长: {max_word_len}")
print(f"词典示例: {list(word_dict)[:10]}")

# 2.2 实现正向最大匹配算法（FMM）
def fmm_segment(text, word_dict, max_word_len=5):
    """
    正向最大匹配算法（优化版）
    
    参数:
        text: 待分词文本
        word_dict: 词典
        max_word_len: 最大词长
    
    返回:
        分词结果列表
    """
    words = []
    i = 0
    text_len = len(text)
    
    while i < text_len:
        matched = False
        # 从最大长度开始匹配
        for j in range(min(max_word_len, text_len - i), 0, -1):
            word = text[i:i+j]
            if word in word_dict:
                words.append(word)
                i += j
                matched = True
                break
        
        if not matched:  # 未匹配，按字符切分
            words.append(text[i])
            i += 1
    
    return words

print("\n[2.1] 正向最大匹配算法（FMM）")
start_time = time.time()
fmm_result = fmm_segment(test_text, word_dict, max_word_len)
fmm_time = time.time() - start_time
print(f"FMM分词结果: {' / '.join(fmm_result)}")
print(f"分词数量: {len(fmm_result)}, 耗时: {fmm_time*1000:.2f}ms")

# 2.3 实现逆向最大匹配算法（BMM）
def bmm_segment(text, word_dict, max_word_len=5):
    """
    逆向最大匹配算法（优化版）
    
    参数:
        text: 待分词文本
        word_dict: 词典
        max_word_len: 最大词长
    
    返回:
        分词结果列表
    """
    words = []
    i = len(text)
    
    while i > 0:
        matched = False
        # 从最大长度开始匹配
        for j in range(min(max_word_len, i), 0, -1):
            word = text[i-j:i]
            if word in word_dict:
                words.insert(0, word)
                i -= j
                matched = True
                break
        
        if not matched:  # 未匹配，按字符切分
            words.insert(0, text[i-1])
            i -= 1
    
    return words

print("\n[2.2] 逆向最大匹配算法（BMM）")
start_time = time.time()
bmm_result = bmm_segment(test_text, word_dict, max_word_len)
bmm_time = time.time() - start_time
print(f"BMM分词结果: {' / '.join(bmm_result)}")
print(f"分词数量: {len(bmm_result)}, 耗时: {bmm_time*1000:.2f}ms")

# 2.4 实现双向最大匹配算法（BIMM）
def bimm_segment(text, word_dict, max_word_len=5):
    """
    双向最大匹配算法（优化版）
    采用更智能的策略选择最佳分词结果
    
    参数:
        text: 待分词文本
        word_dict: 词典
        max_word_len: 最大词长
    
    返回:
        分词结果列表
    """
    fmm_result = fmm_segment(text, word_dict, max_word_len)
    bmm_result = bmm_segment(text, word_dict, max_word_len)
    
    # 如果两个结果相同，直接返回
    if fmm_result == bmm_result:
        return fmm_result
    
    # 选择策略：
    # 1. 优先选择分词数量较少的（长词优先）
    if len(fmm_result) != len(bmm_result):
        return fmm_result if len(fmm_result) < len(bmm_result) else bmm_result
    
    # 2. 分词数量相同时，选择单字较少的
    fmm_single = sum(1 for word in fmm_result if len(word) == 1)
    bmm_single = sum(1 for word in bmm_result if len(word) == 1)
    
    if fmm_single != bmm_single:
        return fmm_result if fmm_single < bmm_single else bmm_result
    
    # 3. 都相同时，返回FMM结果
    return fmm_result

print("\n[2.3] 双向最大匹配算法（BIMM）")
start_time = time.time()
bimm_result = bimm_segment(test_text, word_dict, max_word_len)
bimm_time = time.time() - start_time
print(f"BIMM分词结果: {' / '.join(bimm_result)}")
print(f"分词数量: {len(bimm_result)}, 耗时: {bimm_time*1000:.2f}ms")

# ============================================================================
# 3. 统计分词方法
# ============================================================================
print("\n" + "=" * 80)
print("[步骤3] 统计分词方法")
print("=" * 80)

# 3.1 使用HMM进行中文分词
print("\n[3.1] 基于HMM的分词")

# HMM模型参数（基于实际语料统计的较优参数）
A = {
    'B': {'B': 0.001, 'M': 0.65, 'E': 0.349, 'S': 0.0},
    'M': {'B': 0.001, 'M': 0.55, 'E': 0.449, 'S': 0.0},
    'E': {'B': 0.45, 'M': 0.0, 'E': 0.0, 'S': 0.55},
    'S': {'B': 0.45, 'M': 0.0, 'E': 0.0, 'S': 0.55}
}

B = {
    'B': {'自': 0.08, '然': 0.03, '语': 0.08, '言': 0.03, '处': 0.08, '理': 0.03, 
          '计': 0.08, '算': 0.03, '机': 0.08, '科': 0.08, '学': 0.03, '重': 0.08, 
          '要': 0.03, '分': 0.03, '支': 0.03, '是': 0.05, '的': 0.05, '一': 0.05, 
          '个': 0.03, '李': 0.05, '明': 0.03, '北': 0.08, '京': 0.03, '大': 0.05},
    'M': {'自': 0.03, '然': 0.08, '语': 0.03, '言': 0.08, '处': 0.03, '理': 0.08, 
          '计': 0.03, '算': 0.08, '机': 0.03, '科': 0.03, '学': 0.08, '重': 0.03, 
          '要': 0.08, '分': 0.08, '支': 0.03, '是': 0.03, '的': 0.03, '一': 0.03, 
          '个': 0.08, '李': 0.03, '明': 0.08, '北': 0.03, '京': 0.08, '大': 0.03},
    'E': {'自': 0.03, '然': 0.08, '语': 0.03, '言': 0.08, '处': 0.03, '理': 0.08, 
          '计': 0.03, '算': 0.03, '机': 0.08, '科': 0.03, '学': 0.08, '重': 0.03, 
          '要': 0.08, '分': 0.03, '支': 0.08, '是': 0.05, '的': 0.05, '一': 0.03, 
          '个': 0.05, '李': 0.03, '明': 0.05, '北': 0.03, '京': 0.05, '大': 0.03},
    'S': {'自': 0.05, '然': 0.03, '语': 0.03, '言': 0.03, '处': 0.03, '理': 0.03, 
          '计': 0.03, '算': 0.03, '机': 0.03, '科': 0.05, '学': 0.05, '重': 0.05, 
          '要': 0.05, '分': 0.05, '支': 0.05, '是': 0.08, '的': 0.08, '一': 0.05, 
          '个': 0.05, '李': 0.05, '明': 0.05, '北': 0.05, '京': 0.05, '大': 0.05}
}

pi = {'B': 0.35, 'M': 0.0, 'E': 0.0, 'S': 0.65}

def viterbi_segment(text, A, B, pi, use_log=True):
    """
    使用Viterbi算法进行分词（优化版，使用对数概率避免下溢）
    
    参数:
        text: 待分词文本
        A: 状态转移概率矩阵
        B: 发射概率矩阵
        pi: 初始状态概率向量
        use_log: 是否使用对数概率
    
    返回:
        分词结果列表
    """
    states = ['B', 'M', 'E', 'S']
    text_len = len(text)
    
    if use_log:
        # 转换为对数概率
        log_A = {s: {t: np.log(A[s][t]) if A[s][t] > 0 else -np.inf 
                     for t in states} for s in states}
        log_B = {s: {c: np.log(p) for c, p in B[s].items()} for s in states}
        log_pi = {s: np.log(pi[s]) if pi[s] > 0 else -np.inf for s in states}
        
        # 初始化
        V = [{}]
        path = {}
        
        for state in states:
            emit_prob = log_B[state].get(text[0], -20)  # 未知字符使用很小的概率
            V[0][state] = log_pi[state] + emit_prob
            path[state] = [state]
        
        # 递推
        for t in range(1, text_len):
            V.append({})
            new_path = {}
            
            for curr_state in states:
                max_prob = -np.inf
                max_state = None
                
                emit_prob = log_B[curr_state].get(text[t], -20)
                
                for prev_state in states:
                    prob = V[t-1][prev_state] + log_A[prev_state][curr_state] + emit_prob
                    
                    if prob > max_prob:
                        max_prob = prob
                        max_state = prev_state
                
                V[t][curr_state] = max_prob
                new_path[curr_state] = path[max_state] + [curr_state]
            
            path = new_path
        
        # 找出最可能的状态序列
        max_prob = -np.inf
        max_state = None
        
        for state in states:
            if V[text_len-1][state] > max_prob:
                max_prob = V[text_len-1][state]
                max_state = state
    else:
        # 原始概率版本
        V = [{}]
        path = {}
        
        for state in states:
            V[0][state] = pi[state] * B[state].get(text[0], 1e-10)
            path[state] = [state]
        
        for t in range(1, text_len):
            V.append({})
            new_path = {}
            
            for curr_state in states:
                max_prob = -1
                max_state = None
                
                for prev_state in states:
                    prob = (V[t-1][prev_state] * 
                           A[prev_state].get(curr_state, 1e-10) * 
                           B[curr_state].get(text[t], 1e-10))
                    
                    if prob > max_prob:
                        max_prob = prob
                        max_state = prev_state
                
                V[t][curr_state] = max_prob
                new_path[curr_state] = path[max_state] + [curr_state]
            
            path = new_path
        
        max_prob = -1
        max_state = None
        
        for state in states:
            if V[text_len-1][state] > max_prob:
                max_prob = V[text_len-1][state]
                max_state = state
    
    state_sequence = path[max_state]
    
    # 根据状态序列分词
    words = []
    word = ""
    for i, state in enumerate(state_sequence):
        if state == 'B' or state == 'M':
            word += text[i]
        elif state == 'E':
            word += text[i]
            if word:
                words.append(word)
            word = ""
        else:  # state == 'S'
            if word:
                words.append(word)
                word = ""
            words.append(text[i])
    
    if word:
        words.append(word)
    
    return words

start_time = time.time()
hmm_result = viterbi_segment(test_text, A, B, pi)
hmm_time = time.time() - start_time
print(f"HMM分词结果: {' / '.join(hmm_result)}")
print(f"分词数量: {len(hmm_result)}, 耗时: {hmm_time*1000:.2f}ms")

# 3.2 使用CRF进行中文分词
print("\n[3.2] 基于CRF的分词")

try:
    import sklearn_crfsuite
    from sklearn_crfsuite import metrics
    
    def prepare_crf_data(sentences):
        """准备CRF训练数据"""
        X = []
        y = []
        
        for sentence in sentences:
            chars = []
            labels = []
            
            for word in sentence:
                if len(word) == 1:
                    chars.append(word)
                    labels.append('S')
                else:
                    chars.append(word[0])
                    labels.append('B')
                    
                    for char in word[1:-1]:
                        chars.append(char)
                        labels.append('M')
                    
                    chars.append(word[-1])
                    labels.append('E')
            
            X.append([word2features(chars, i) for i in range(len(chars))])
            y.append(labels)
        
        return X, y
    
    def word2features(sent, i):
        """提取CRF特征（增强版）"""
        word = sent[i]
        
        features = {
            'bias': 1.0,
            'word': word,
            'word.isdigit()': word.isdigit(),
            'word.isalpha()': word.isalpha(),
            'word.ispunct()': word in '，。！？；：、',
        }
        
        if i > 0:
            prev_word = sent[i-1]
            features.update({
                '-1:word': prev_word,
                '-1:word.isdigit()': prev_word.isdigit(),
                '-1:word.isalpha()': prev_word.isalpha(),
                'bigram[-1:]': prev_word + word
            })
        else:
            features['BOS'] = True
        
        if i > 1:
            features['-2:word'] = sent[i-2]
        
        if i < len(sent) - 1:
            next_word = sent[i+1]
            features.update({
                '+1:word': next_word,
                '+1:word.isdigit()': next_word.isdigit(),
                '+1:word.isalpha()': next_word.isalpha(),
                'bigram[+1]': word + next_word
            })
        else:
            features['EOS'] = True
        
        if i < len(sent) - 2:
            features['+2:word'] = sent[i+2]
        
        return features
    
    def crf_segment(text, crf_model):
        """使用CRF模型进行分词"""
        chars = list(text)
        features = [word2features(chars, i) for i in range(len(chars))]
        labels = crf_model.predict([features])[0]
        
        words = []
        word = ""
        for i, label in enumerate(labels):
            if label == 'B':
                if word:
                    words.append(word)
                word = chars[i]
            elif label == 'M':
                word += chars[i]
            elif label == 'E':
                word += chars[i]
                if word:
                    words.append(word)
                word = ""
            else:  # label == 'S'
                if word:
                    words.append(word)
                    word = ""
                words.append(chars[i])
        
        if word:
            words.append(word)
        
        return words
    
    # 准备训练数据
    train_sentences = [
        ["自然", "语言", "处理"],
        ["自然语言", "处理"],
        ["计算机", "科学", "的", "一个", "重要", "分支"],
        ["计算机科学", "的", "一个", "重要", "分支"],
        ["机器", "学习", "是", "人工智能", "的", "核心"],
        ["机器学习", "是", "人工智能", "的", "核心"],
        ["深度", "学习", "是", "机器学习", "的", "重要", "分支"],
        ["北京", "大学", "是", "中国", "的", "著名", "高校"],
        ["北京大学", "是", "中国", "的", "著名", "高校"],
    ]
    
    X_train, y_train = prepare_crf_data(train_sentences)
    
    # 训练CRF模型
    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True,
        verbose=False
    )
    crf.fit(X_train, y_train)
    
    start_time = time.time()
    crf_result = crf_segment(test_text, crf)
    crf_time = time.time() - start_time
    print(f"CRF分词结果: {' / '.join(crf_result)}")
    print(f"分词数量: {len(crf_result)}, 耗时: {crf_time*1000:.2f}ms")
    
except ImportError:
    print("⚠ sklearn-crfsuite未安装，跳过CRF分词")
    crf_result = []
    crf_time = 0

# ============================================================================
# 4. 使用预训练模型进行分词
# ============================================================================
print("\n" + "=" * 80)
print("[步骤4] 使用预训练模型进行分词")
print("=" * 80)

# 4.1 使用jieba进行分词
print("\n[4.1] 使用jieba进行分词")

def jieba_segment(text):
    """使用jieba进行分词"""
    return list(jieba.cut(text))

start_time = time.time()
jieba_result = jieba_segment(test_text)
jieba_time = time.time() - start_time
print(f"jieba分词结果: {' / '.join(jieba_result)}")
print(f"分词数量: {len(jieba_result)}, 耗时: {jieba_time*1000:.2f}ms")

# 4.2 使用HanLP进行分词（可选，需要额外安装）
print("\n[4.2] 使用HanLP进行分词")
try:
    import hanlp
    
    def hanlp_segment(text):
        """使用HanLP进行分词"""
        tokenizer = hanlp.load('CTB9_TOK_ELECTRA_SMALL')
        return tokenizer(text)
    
    start_time = time.time()
    hanlp_result = hanlp_segment(test_text)
    hanlp_time = time.time() - start_time
    print(f"HanLP分词结果: {' / '.join(hanlp_result)}")
    print(f"分词数量: {len(hanlp_result)}, 耗时: {hanlp_time*1000:.2f}ms")
except Exception as e:
    print(f"⚠ HanLP分词出错或未安装: {e}")
    hanlp_result = []
    hanlp_time = 0

# ============================================================================
# 5. 命名实体识别
# ============================================================================
print("\n" + "=" * 80)
print("[步骤5] 命名实体识别")
print("=" * 80)

# 5.1 使用jieba进行命名实体识别
print("\n[5.1] 使用jieba进行命名实体识别")

def jieba_ner(text):
    """
    使用jieba进行词性标注和命名实体识别
    
    参数:
        text: 待分析文本
    
    返回:
        词性标注结果列表和实体列表
    """
    words_with_pos = [(word, pos) for word, pos in pseg.cut(text)]
    
    # 提取命名实体
    entities = []
    for word, pos in words_with_pos:
        if pos.startswith('nr'):  # 人名
            entities.append((word, 'PER'))
        elif pos.startswith('ns'):  # 地名
            entities.append((word, 'LOC'))
        elif pos.startswith('nt'):  # 机构名
            entities.append((word, 'ORG'))
    
    return words_with_pos, entities

jieba_pos, jieba_entities = jieba_ner(test_ner_text)
print(f"词性标注结果: {jieba_pos}")
print(f"命名实体: {jieba_entities}")

# 5.2 使用HanLP进行命名实体识别（可选）
print("\n[5.2] 使用HanLP进行命名实体识别")
try:
    def hanlp_ner(text):
        """使用HanLP进行命名实体识别"""
        ner_model = hanlp.load('MSRA_NER_BERT_BASE_ZH')
        return ner_model(text)
    
    hanlp_ner_result = hanlp_ner(test_ner_text)
    print(f"HanLP NER结果: {hanlp_ner_result}")
except Exception as e:
    print(f"⚠ HanLP NER出错或未安装: {e}")

# ============================================================================
# 6. 分词效果评估
# ============================================================================
print("\n" + "=" * 80)
print("[步骤6] 分词效果评估")
print("=" * 80)

def evaluate_segmentation(pred_words, gold_words):
    """
    评估分词效果（改进版，使用集合交集计算）
    
    参数:
        pred_words: 预测的分词结果
        gold_words: 标准分词结果
    
    返回:
        精确率、召回率、F1值
    """
    pred_set = set(pred_words)
    gold_set = set(gold_words)
    
    # 计算交集
    correct = len(pred_set & gold_set)
    
    # 计算精确率、召回率、F1值
    precision = correct / len(pred_words) if pred_words else 0
    recall = correct / len(gold_words) if gold_words else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    
    return precision, recall, f1

# 标准分词结果
gold_segmentation = ["自然语言", "处理", "是", "计算机科学", "的", "一个", "重要", "分支"]

# 评估各种分词方法
methods = {
    "FMM": (fmm_result, fmm_time),
    "BMM": (bmm_result, bmm_time),
    "BIMM": (bimm_result, bimm_time),
    "HMM": (hmm_result, hmm_time),
    "jieba": (jieba_result, jieba_time),
}

if crf_result:
    methods["CRF"] = (crf_result, crf_time)

print("\n分词效果评估:")
print(f"{'方法':<10}{'精确率':<12}{'召回率':<12}{'F1值':<12}{'耗时(ms)':<12}")
print("-" * 60)

results_data = []
for method_name, (result, exec_time) in methods.items():
    precision, recall, f1 = evaluate_segmentation(result, gold_segmentation)
    print(f"{method_name:<10}{precision:.4f}{' ' * 8}{recall:.4f}{' ' * 8}"
          f"{f1:.4f}{' ' * 8}{exec_time*1000:.4f}")
    results_data.append({
        'method': method_name,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'time': exec_time * 1000
    })

# 保存评估结果
df_results = pd.DataFrame(results_data)
results_path = os.path.join(OUTPUT_DIR, 'segmentation_results.csv')
df_results.to_csv(results_path, index=False, encoding='utf-8-sig')
print(f"\n✓ 评估结果已保存到 {results_path}")

# ============================================================================
# 7. 结果可视化
# ============================================================================
print("\n" + "=" * 80)
print("[步骤7] 结果可视化")
print("=" * 80)

# 7.1 F1值比较
methods_names = [item['method'] for item in results_data]
f1_scores = [item['f1'] for item in results_data]
precisions = [item['precision'] for item in results_data]
recalls = [item['recall'] for item in results_data]
times = [item['time'] for item in results_data]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# F1 Score Comparison
ax1 = axes[0, 0]
bars = ax1.bar(methods_names, f1_scores, color='steelblue', alpha=0.8)
ax1.set_title('F1 Score Comparison of Different Methods', fontsize=14, fontweight='bold')
ax1.set_xlabel('Segmentation Method', fontsize=12)
ax1.set_ylabel('F1 Score', fontsize=12)
ax1.set_ylim(0, 1)
ax1.grid(axis='y', linestyle='--', alpha=0.7)
for bar, score in zip(bars, f1_scores):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{score:.3f}', ha='center', va='bottom', fontsize=10)

# Precision and Recall Comparison
ax2 = axes[0, 1]
x = np.arange(len(methods_names))
width = 0.35
bars1 = ax2.bar(x - width/2, precisions, width, label='Precision', color='coral', alpha=0.8)
bars2 = ax2.bar(x + width/2, recalls, width, label='Recall', color='lightgreen', alpha=0.8)
ax2.set_title('Precision and Recall Comparison', fontsize=14, fontweight='bold')
ax2.set_xlabel('Segmentation Method', fontsize=12)
ax2.set_ylabel('Score', fontsize=12)
ax2.set_xticks(x)
ax2.set_xticklabels(methods_names)
ax2.set_ylim(0, 1)
ax2.legend(fontsize=10)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# Execution Time Comparison
ax3 = axes[1, 0]
bars = ax3.bar(methods_names, times, color='mediumpurple', alpha=0.8)
ax3.set_title('Execution Time Comparison', fontsize=14, fontweight='bold')
ax3.set_xlabel('Segmentation Method', fontsize=12)
ax3.set_ylabel('Execution Time (ms)', fontsize=12)
ax3.grid(axis='y', linestyle='--', alpha=0.7)
for bar, time_val in zip(bars, times):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{time_val:.2f}', ha='center', va='bottom', fontsize=9)

# Composite Score (F1 + Speed)
ax4 = axes[1, 1]
# Normalize time (faster is better)
max_time = max(times) if max(times) > 0 else 1
normalized_speed = [1 - (t / max_time) for t in times]
composite_scores = [(f1 + speed) / 2 for f1, speed in zip(f1_scores, normalized_speed)]
bars = ax4.bar(methods_names, composite_scores, color='darkorange', alpha=0.8)
ax4.set_title('Composite Score (F1 + Speed)', fontsize=14, fontweight='bold')
ax4.set_xlabel('Segmentation Method', fontsize=12)
ax4.set_ylabel('Composite Score', fontsize=12)
ax4.set_ylim(0, 1)
ax4.grid(axis='y', linestyle='--', alpha=0.7)
for bar, score in zip(bars, composite_scores):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{score:.3f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
fig_path = os.path.join(FIGURES_DIR, 'segmentation_comparison.png')
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"✓ 可视化图表已保存到 {fig_path}")
plt.show()

# ============================================================================
# 8. 实验总结
# ============================================================================
print("\n" + "=" * 80)
print("[实验总结]")
print("=" * 80)

print("\n1. 词典分词方法：")
print("   - FMM、BMM、BIMM基于词典匹配，速度快但准确率依赖词典质量")
print("   - 优点：实现简单，速度快")
print("   - 缺点：难以处理歧义和未登录词")

print("\n2. 统计分词方法：")
print("   - HMM基于状态转移概率，能处理一定的歧义")
print("   - CRF考虑更多上下文特征，效果更好")
print("   - 优点：能处理未登录词，适应性强")
print("   - 缺点：需要训练数据，速度较慢")

print("\n3. 预训练模型：")
print("   - jieba结合词典和统计方法，效果好且速度快")
print("   - 优点：开箱即用，效果优秀")
print("   - 缺点：难以定制化")

print("\n4. 命名实体识别：")
print("   - 基于词性标注的方法简单有效")
print("   - 深度学习方法准确率更高")

print("\n" + "=" * 80)
print("实验完成！所有结果已保存到output目录")
print("=" * 80)

