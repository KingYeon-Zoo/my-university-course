"""
实验二：中文分词与命名实体识别 - 实验拓展
Author: NLP Course
Date: 2025-10-30
Description: 
    1. 基于深度学习的分词（BiLSTM-CRF）
    2. 领域适应性研究
    3. 分词歧义研究
    4. 命名实体识别优化
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import time
import warnings
import jieba
import jieba.posseg as pseg

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
print("实验二：中文分词与命名实体识别 - 实验拓展")
print("=" * 80)

# 创建输出目录（使用绝对路径）
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# ============================================================================
# 拓展1: 基于深度学习的中文分词（BiLSTM-CRF）
# ============================================================================
print("\n" + "=" * 80)
print("[拓展1] 基于深度学习的中文分词（BiLSTM-CRF）")
print("=" * 80)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    
    class BiLSTM_CRF(nn.Module):
        """
        BiLSTM-CRF模型用于中文分词
        
        架构：
        Input -> Embedding -> BiLSTM -> Linear -> CRF -> Output
        """
        
        def __init__(self, vocab_size, tag_to_ix, embedding_dim=100, hidden_dim=128):
            super(BiLSTM_CRF, self).__init__()
            self.embedding_dim = embedding_dim
            self.hidden_dim = hidden_dim
            self.vocab_size = vocab_size
            self.tag_to_ix = tag_to_ix
            self.tagset_size = len(tag_to_ix)
            
            # 词嵌入层
            self.word_embeds = nn.Embedding(vocab_size, embedding_dim)
            
            # BiLSTM层
            self.lstm = nn.LSTM(embedding_dim, hidden_dim // 2,
                              num_layers=1, bidirectional=True, batch_first=True)
            
            # 全连接层：LSTM输出到标签空间
            self.hidden2tag = nn.Linear(hidden_dim, self.tagset_size)
            
            # CRF转移矩阵
            self.transitions = nn.Parameter(
                torch.randn(self.tagset_size, self.tagset_size))
            
            # 约束：不能转移到START，不能从END转移
            self.transitions.data[tag_to_ix['<START>'], :] = -10000
            self.transitions.data[:, tag_to_ix['<END>']] = -10000
        
        def _get_lstm_features(self, sentence):
            """获取BiLSTM的特征输出"""
            embeds = self.word_embeds(sentence)
            lstm_out, _ = self.lstm(embeds)
            lstm_feats = self.hidden2tag(lstm_out)
            return lstm_feats
        
        def _forward_alg(self, feats):
            """前向算法计算配分函数"""
            init_alphas = torch.full((1, self.tagset_size), -10000.)
            init_alphas[0][self.tag_to_ix['<START>']] = 0.
            forward_var = init_alphas
            
            for feat in feats:
                alphas_t = []
                for next_tag in range(self.tagset_size):
                    emit_score = feat[next_tag].view(1, -1).expand(1, self.tagset_size)
                    trans_score = self.transitions[next_tag].view(1, -1)
                    next_tag_var = forward_var + trans_score + emit_score
                    alphas_t.append(self._log_sum_exp(next_tag_var).view(1))
                forward_var = torch.cat(alphas_t).view(1, -1)
            
            terminal_var = forward_var + self.transitions[self.tag_to_ix['<END>']]
            alpha = self._log_sum_exp(terminal_var)
            return alpha
        
        def _log_sum_exp(self, vec):
            """数值稳定的log-sum-exp"""
            max_score = vec[0, vec.argmax(dim=1)]
            max_score_broadcast = max_score.view(1, -1).expand(1, vec.size()[1])
            return max_score + torch.log(torch.sum(torch.exp(vec - max_score_broadcast)))
        
        def _score_sentence(self, feats, tags):
            """计算给定标签序列的得分"""
            score = torch.zeros(1)
            tags = torch.cat([torch.tensor([self.tag_to_ix['<START>']], dtype=torch.long), tags])
            for i, feat in enumerate(feats):
                score = score + self.transitions[tags[i + 1], tags[i]] + feat[tags[i + 1]]
            score = score + self.transitions[self.tag_to_ix['<END>'], tags[-1]]
            return score
        
        def _viterbi_decode(self, feats):
            """Viterbi解码找到最优路径"""
            backpointers = []
            
            init_vvars = torch.full((1, self.tagset_size), -10000.)
            init_vvars[0][self.tag_to_ix['<START>']] = 0
            forward_var = init_vvars
            
            for feat in feats:
                bptrs_t = []
                viterbivars_t = []
                
                for next_tag in range(self.tagset_size):
                    next_tag_var = forward_var + self.transitions[next_tag]
                    best_tag_id = next_tag_var.argmax(dim=1)
                    bptrs_t.append(best_tag_id)
                    viterbivars_t.append(next_tag_var[0][best_tag_id].view(1))
                
                forward_var = (torch.cat(viterbivars_t) + feat).view(1, -1)
                backpointers.append(bptrs_t)
            
            terminal_var = forward_var + self.transitions[self.tag_to_ix['<END>']]
            best_tag_id = terminal_var.argmax(dim=1)
            path_score = terminal_var[0][best_tag_id]
            
            best_path = [best_tag_id.item()]
            for bptrs_t in reversed(backpointers):
                best_tag_id = bptrs_t[best_tag_id]
                best_path.append(best_tag_id.item())
            
            start = best_path.pop()
            assert start == self.tag_to_ix['<START>']
            best_path.reverse()
            return path_score, best_path
        
        def neg_log_likelihood(self, sentence, tags):
            """计算负对数似然损失"""
            feats = self._get_lstm_features(sentence)
            forward_score = self._forward_alg(feats[0])
            gold_score = self._score_sentence(feats[0], tags)
            return forward_score - gold_score
        
        def forward(self, sentence):
            """前向传播，返回最优标签序列"""
            lstm_feats = self._get_lstm_features(sentence)
            score, tag_seq = self._viterbi_decode(lstm_feats[0])
            return score, tag_seq
    
    print("\n[1.1] 准备训练数据")
    
    # 准备训练数据
    training_data = [
        ("自然语言处理", ['B', 'M', 'M', 'E']),
        ("计算机科学", ['B', 'M', 'E']),
        ("机器学习", ['B', 'M', 'E']),
        ("深度学习", ['B', 'M', 'E']),
        ("神经网络", ['B', 'M', 'E']),
        ("自然语言处理是计算机科学的一个重要分支", 
         ['B', 'M', 'M', 'E', 'S', 'B', 'M', 'M', 'E', 'S', 'B', 'E', 'B', 'E', 'B', 'E']),
    ]
    
    # 构建字符和标签词典
    char_to_ix = {}
    for sent, tags in training_data:
        for char in sent:
            if char not in char_to_ix:
                char_to_ix[char] = len(char_to_ix)
    
    tag_to_ix = {'B': 0, 'M': 1, 'E': 2, 'S': 3, '<START>': 4, '<END>': 5}
    ix_to_tag = {v: k for k, v in tag_to_ix.items()}
    
    print(f"字符词典大小: {len(char_to_ix)}")
    print(f"标签集合: {list(tag_to_ix.keys())}")
    
    def prepare_sequence(seq, to_ix):
        """将序列转换为索引"""
        idxs = [to_ix.get(w, 0) for w in seq]
        return torch.tensor(idxs, dtype=torch.long)
    
    print("\n[1.2] 初始化并训练BiLSTM-CRF模型")
    
    # 初始化模型
    EMBEDDING_DIM = 50
    HIDDEN_DIM = 64
    
    model = BiLSTM_CRF(len(char_to_ix), tag_to_ix, EMBEDDING_DIM, HIDDEN_DIM)
    optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay=1e-4)
    
    # 训练模型
    print("开始训练...")
    model.train()
    for epoch in range(100):
        epoch_loss = 0
        for sentence, tags in training_data:
            model.zero_grad()
            
            sentence_in = prepare_sequence(sentence, char_to_ix).unsqueeze(0)
            targets = torch.tensor([tag_to_ix[t] for t in tags], dtype=torch.long)
            
            loss = model.neg_log_likelihood(sentence_in, targets)
            epoch_loss += loss.item()
            
            loss.backward()
            optimizer.step()
        
        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch+1}/100, Loss: {epoch_loss:.4f}")
    
    print("✓ 训练完成")
    
    print("\n[1.3] 测试BiLSTM-CRF分词")
    
    def bilstm_crf_segment(text, model, char_to_ix, ix_to_tag):
        """使用BiLSTM-CRF进行分词"""
        model.eval()
        with torch.no_grad():
            inputs = prepare_sequence(text, char_to_ix).unsqueeze(0)
            score, tag_seq = model(inputs)
        
        # 根据标签序列分词
        words = []
        word = ""
        for i, tag_idx in enumerate(tag_seq):
            tag = ix_to_tag[tag_idx]
            if tag == 'B':
                if word:
                    words.append(word)
                word = text[i]
            elif tag == 'M':
                word += text[i]
            elif tag == 'E':
                word += text[i]
                if word:
                    words.append(word)
                word = ""
            else:  # tag == 'S'
                if word:
                    words.append(word)
                    word = ""
                words.append(text[i])
        
        if word:
            words.append(word)
        
        return words
    
    test_text = "自然语言处理是计算机科学的一个重要分支"
    bilstm_result = bilstm_crf_segment(test_text, model, char_to_ix, ix_to_tag)
    print(f"BiLSTM-CRF分词结果: {' / '.join(bilstm_result)}")
    
    # 保存模型
    model_path = os.path.join(OUTPUT_DIR, 'bilstm_crf_model.pth')
    torch.save(model.state_dict(), model_path)
    print(f"✓ 模型已保存到 {model_path}")
    
except ImportError as e:
    print(f"⚠ PyTorch未安装，跳过BiLSTM-CRF实验: {e}")
except Exception as e:
    print(f"⚠ BiLSTM-CRF实验出错: {e}")

# ============================================================================
# 拓展2: 领域适应性研究
# ============================================================================
print("\n" + "=" * 80)
print("[拓展2] 领域适应性研究")
print("=" * 80)

print("\n[2.1] 定义不同领域的测试文本")

# 定义不同领域的测试文本
domain_texts = {
    "通用": [
        "今天天气很好，我们去公园散步吧",
        "这是一个测试句子，用于评估分词效果"
    ],
    "科技": [
        "深度学习是人工智能领域的重要技术",
        "自然语言处理技术在智能客服中广泛应用",
        "神经网络模型在图像识别任务中表现出色"
    ],
    "医疗": [
        "患者出现发热、咳嗽等症状",
        "建议进行血常规和胸部CT检查",
        "诊断为上呼吸道感染，需要抗感染治疗"
    ],
    "法律": [
        "根据合同法第五十二条规定",
        "被告应承担违约责任并赔偿损失",
        "原告请求判令被告支付货款及利息"
    ],
    "金融": [
        "股票市场今日大幅波动，沪指下跌",
        "央行宣布降低存款准备金率",
        "该公司发布年度财务报告，净利润增长"
    ]
}

print(f"测试领域数量: {len(domain_texts)}")
for domain, texts in domain_texts.items():
    print(f"  {domain}: {len(texts)}条文本")

print("\n[2.2] 测试不同分词方法的领域适应性")

def evaluate_domain_adaptation(domain_texts):
    """评估不同分词方法在各领域的适应性"""
    results = []
    
    for domain, texts in domain_texts.items():
        print(f"\n处理领域: {domain}")
        
        for text in texts:
            # jieba分词
            jieba_words = list(jieba.cut(text))
            
            # 统计信息
            avg_word_len = np.mean([len(w) for w in jieba_words])
            single_char_ratio = sum(1 for w in jieba_words if len(w) == 1) / len(jieba_words)
            
            results.append({
                'domain': domain,
                'text': text,
                'word_count': len(jieba_words),
                'avg_word_len': avg_word_len,
                'single_char_ratio': single_char_ratio
            })
    
    return pd.DataFrame(results)

df_domain = evaluate_domain_adaptation(domain_texts)

print("\n[2.3] 领域适应性统计分析")
domain_stats = df_domain.groupby('domain').agg({
    'word_count': ['mean', 'std'],
    'avg_word_len': ['mean', 'std'],
    'single_char_ratio': ['mean', 'std']
}).round(3)

print("\n各领域分词统计:")
print(domain_stats)

# 保存结果
csv_path = os.path.join(OUTPUT_DIR, 'domain_adaptation_results.csv')
df_domain.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n✓ 领域适应性结果已保存到 {csv_path}")

print("\n[2.4] 领域适应性可视化")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

domains = df_domain.groupby('domain')['avg_word_len'].mean().index
avg_lengths = df_domain.groupby('domain')['avg_word_len'].mean().values
single_ratios = df_domain.groupby('domain')['single_char_ratio'].mean().values
word_counts = df_domain.groupby('domain')['word_count'].mean().values

# Average Word Length
ax1 = axes[0]
bars = ax1.bar(domains, avg_lengths, color='steelblue', alpha=0.8)
ax1.set_title('Average Word Length by Domain', fontsize=12, fontweight='bold')
ax1.set_xlabel('Domain', fontsize=10)
ax1.set_ylabel('Avg Word Length', fontsize=10)
ax1.grid(axis='y', linestyle='--', alpha=0.7)
for bar, val in zip(bars, avg_lengths):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}', ha='center', va='bottom', fontsize=9)

# Single Character Ratio
ax2 = axes[1]
bars = ax2.bar(domains, single_ratios, color='coral', alpha=0.8)
ax2.set_title('Single Character Ratio by Domain', fontsize=12, fontweight='bold')
ax2.set_xlabel('Domain', fontsize=10)
ax2.set_ylabel('Single Char Ratio', fontsize=10)
ax2.grid(axis='y', linestyle='--', alpha=0.7)
for bar, val in zip(bars, single_ratios):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}', ha='center', va='bottom', fontsize=9)

# Average Word Count
ax3 = axes[2]
bars = ax3.bar(domains, word_counts, color='lightgreen', alpha=0.8)
ax3.set_title('Average Word Count by Domain', fontsize=12, fontweight='bold')
ax3.set_xlabel('Domain', fontsize=10)
ax3.set_ylabel('Avg Word Count', fontsize=10)
ax3.grid(axis='y', linestyle='--', alpha=0.7)
for bar, val in zip(bars, word_counts):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
fig_path = os.path.join(FIGURES_DIR, 'domain_adaptation.png')
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"✓ 可视化图表已保存到 {fig_path}")
plt.show()

# ============================================================================
# 拓展3: 分词歧义研究
# ============================================================================
print("\n" + "=" * 80)
print("[拓展3] 分词歧义研究")
print("=" * 80)

print("\n[3.1] 收集分词歧义案例")

# 分词歧义案例
ambiguous_cases = [
    {
        'text': '乒乓球拍卖完了',
        'options': [
            ['乒乓球', '拍卖', '完了'],  # 解释1
            ['乒乓球拍', '卖', '完了']     # 解释2
        ],
        'explanation': '交叉歧义：乒乓球 + 拍卖 vs 乒乓球拍 + 卖'
    },
    {
        'text': '中国人民解放军',
        'options': [
            ['中国', '人民', '解放军'],
            ['中国人民', '解放军'],
            ['中国', '人民解放军']
        ],
        'explanation': '组合歧义：不同的组合方式'
    },
    {
        'text': '结婚的和尚未结婚的',
        'options': [
            ['结婚', '的', '和', '尚未', '结婚', '的'],
            ['结婚', '的', '和尚', '未', '结婚', '的']
        ],
        'explanation': '交叉歧义：和 + 尚未 vs 和尚 + 未'
    },
    {
        'text': '这个门把手坏了',
        'options': [
            ['这个', '门', '把手', '坏了'],
            ['这个', '门把手', '坏了']
        ],
        'explanation': '组合歧义：门 + 把手 vs 门把手'
    },
    {
        'text': '美国会通过对台售武法案',
        'options': [
            ['美国', '会', '通过', '对台', '售武', '法案'],
            ['美', '国会', '通过', '对台', '售武', '法案']
        ],
        'explanation': '交叉歧义：美国 + 会 vs 美 + 国会'
    }
]

print(f"收集到 {len(ambiguous_cases)} 个歧义案例\n")

print("\n[3.2] 分析不同分词方法对歧义的处理")

def analyze_ambiguity(cases):
    """分析分词歧义"""
    results = []
    
    for case in cases:
        text = case['text']
        print(f"\n文本: {text}")
        print(f"说明: {case['explanation']}")
        print(f"可能的分词:")
        for i, option in enumerate(case['options'], 1):
            print(f"  选项{i}: {' / '.join(option)}")
        
        # 使用不同方法分词
        jieba_result = list(jieba.cut(text))
        print(f"jieba: {' / '.join(jieba_result)}")
        
        # 检查是否匹配任何一个选项
        matched = False
        for option in case['options']:
            if jieba_result == option:
                matched = True
                break
        
        results.append({
            'text': text,
            'jieba_result': ' / '.join(jieba_result),
            'matched_option': matched,
            'explanation': case['explanation']
        })
    
    return results

ambiguity_results = analyze_ambiguity(ambiguous_cases)

print("\n[3.3] 歧义处理策略")
print("\n常见的分词歧义类型及处理策略:")
print("1. 交叉歧义：使用上下文信息和词频统计")
print("2. 组合歧义：优先选择较长的词")
print("3. 真歧义：需要语义分析才能确定")
print("\n建议的改进方法:")
print("- 引入词性标注信息")
print("- 使用语言模型进行消歧")
print("- 结合领域知识和上下文")

# ============================================================================
# 拓展4: 命名实体识别优化
# ============================================================================
print("\n" + "=" * 80)
print("[拓展4] 命名实体识别优化")
print("=" * 80)

print("\n[4.1] 基于规则的命名实体识别增强")

class EnhancedNER:
    """增强的命名实体识别器"""
    
    def __init__(self):
        # 人名常用字
        self.person_surnames = set('赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜')
        self.person_names = set('明华强伟芳娜秀英敏静丽刚勇艳涛平')
        
        # 地名标志词
        self.location_indicators = set('省市区县镇乡村路街道大学中学小学')
        
        # 机构标志词
        self.org_indicators = set('公司集团有限责任股份大学学院部委局')
        
        # 时间表达式
        self.time_pattern = re.compile(r'\d{4}年|\d{1,2}月|\d{1,2}日')
        
        # 数字表达式
        self.number_pattern = re.compile(r'\d+\.?\d*[万亿千百十]?[元米克斤]?')
    
    def recognize(self, text):
        """识别文本中的命名实体"""
        entities = {
            'PER': [],  # 人名
            'LOC': [],  # 地名
            'ORG': [],  # 机构名
            'TIME': [], # 时间
            'NUM': []   # 数字
        }
        
        # 先用jieba分词和词性标注
        words_pos = pseg.cut(text)
        
        for word, pos in words_pos:
            # 人名识别
            if pos.startswith('nr'):
                entities['PER'].append(word)
            elif len(word) == 2 and word[0] in self.person_surnames and word[1] in self.person_names:
                entities['PER'].append(word)
            
            # 地名识别
            elif pos.startswith('ns'):
                entities['LOC'].append(word)
            elif any(ind in word for ind in self.location_indicators):
                entities['LOC'].append(word)
            
            # 机构名识别
            elif pos.startswith('nt'):
                entities['ORG'].append(word)
            elif any(ind in word for ind in self.org_indicators):
                entities['ORG'].append(word)
        
        # 时间表达式识别
        time_matches = self.time_pattern.findall(text)
        entities['TIME'].extend(time_matches)
        
        # 数字表达式识别
        num_matches = self.number_pattern.findall(text)
        entities['NUM'].extend(num_matches)
        
        return entities

ner = EnhancedNER()

print("\n[4.2] 测试增强的NER系统")

test_ner_texts = [
    "李明在北京大学计算机科学系学习自然语言处理",
    "2023年10月1日，腾讯公司发布了新产品",
    "王芳和张伟在上海市浦东新区创立了科技公司",
    "中国人民银行决定降低存款准备金率0.5个百分点"
]

for text in test_ner_texts:
    print(f"\n文本: {text}")
    entities = ner.recognize(text)
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"  {entity_type}: {entity_list}")

print("\n[4.3] NER性能统计")

def evaluate_ner_performance(texts):
    """评估NER性能"""
    stats = defaultdict(int)
    
    for text in texts:
        entities = ner.recognize(text)
        for entity_type, entity_list in entities.items():
            stats[entity_type] += len(entity_list)
    
    return dict(stats)

ner_stats = evaluate_ner_performance(test_ner_texts)
print("\n实体识别统计:")
for entity_type, count in ner_stats.items():
    print(f"  {entity_type}: {count}个")

# 可视化
if ner_stats:
    fig, ax = plt.subplots(figsize=(10, 6))
    entity_types = list(ner_stats.keys())
    counts = list(ner_stats.values())
    
    bars = ax.bar(entity_types, counts, color='steelblue', alpha=0.8)
    ax.set_title('Named Entity Recognition Statistics', fontsize=14, fontweight='bold')
    ax.set_xlabel('Entity Type', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, 'ner_statistics.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ NER统计图表已保存到 {fig_path}")
    plt.show()

# ============================================================================
# 拓展5: CRF优化命名实体识别
# ============================================================================
print("\n" + "=" * 80)
print("[拓展5] 使用CRF优化命名实体识别")
print("=" * 80)

try:
    import sklearn_crfsuite
    from sklearn_crfsuite import metrics
    
    print("\n[5.1] 准备NER训练数据")
    
    # BIO标注格式的训练数据
    # B-PER: 人名开始, I-PER: 人名内部
    # B-LOC: 地名开始, I-LOC: 地名内部
    # B-ORG: 机构开始, I-ORG: 机构内部
    # O: 非实体
    
    ner_training_data = [
        ([("李", "B-PER"), ("明", "I-PER"), ("在", "O"), ("北", "B-LOC"), 
          ("京", "I-LOC"), ("大", "I-LOC"), ("学", "I-LOC")]),
        ([("王", "B-PER"), ("芳", "I-PER"), ("来", "O"), ("自", "O"), 
          ("上", "B-LOC"), ("海", "I-LOC"), ("市", "I-LOC")]),
        ([("腾", "B-ORG"), ("讯", "I-ORG"), ("公", "I-ORG"), ("司", "I-ORG"), 
          ("发", "O"), ("布", "O"), ("新", "O"), ("产", "O"), ("品", "O")]),
    ]
    
    def sent2features_ner(sent):
        """提取NER特征"""
        return [word2features_ner(sent, i) for i in range(len(sent))]
    
    def sent2labels_ner(sent):
        """提取NER标签"""
        return [label for token, label in sent]
    
    def word2features_ner(sent, i):
        """提取单个词的NER特征"""
        word = sent[i][0]
        
        features = {
            'bias': 1.0,
            'word': word,
            'word.isdigit()': word.isdigit(),
        }
        
        if i > 0:
            word_prev = sent[i-1][0]
            features.update({
                '-1:word': word_prev,
                '-1:word.isdigit()': word_prev.isdigit(),
            })
        else:
            features['BOS'] = True
        
        if i < len(sent) - 1:
            word_next = sent[i+1][0]
            features.update({
                '+1:word': word_next,
                '+1:word.isdigit()': word_next.isdigit(),
            })
        else:
            features['EOS'] = True
        
        return features
    
    X_ner = [sent2features_ner(s) for s in ner_training_data]
    y_ner = [sent2labels_ner(s) for s in ner_training_data]
    
    print(f"训练样本数: {len(X_ner)}")
    
    print("\n[5.2] 训练CRF-NER模型")
    
    crf_ner = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True,
        verbose=False
    )
    
    crf_ner.fit(X_ner, y_ner)
    print("✓ CRF-NER模型训练完成")
    
    print("\n[5.3] 测试CRF-NER模型")
    
    test_sent = [("张", ), ("三", ), ("在", ), ("清", ), ("华", ), ("大", ), ("学", )]
    test_features = sent2features_ner([(w[0], "O") for w in test_sent])
    predicted_labels = crf_ner.predict([test_features])[0]
    
    print("测试句子: " + "".join([w[0] for w in test_sent]))
    print("预测标签:", predicted_labels)
    
except ImportError:
    print("⚠ sklearn-crfsuite未安装，跳过CRF-NER实验")

# ============================================================================
# 实验总结
# ============================================================================
print("\n" + "=" * 80)
print("[实验拓展总结]")
print("=" * 80)

print("\n1. BiLSTM-CRF深度学习分词:")
print("   - 能够自动学习特征，不需要手工设计")
print("   - 在标注数据充足时效果优于传统方法")
print("   - 训练时间较长，但预测速度可接受")

print("\n2. 领域适应性研究:")
print("   - 不同领域的分词特征存在显著差异")
print("   - 专业领域需要定制词典和规则")
print("   - 通用分词工具在专业领域可能需要调优")

print("\n3. 分词歧义研究:")
print("   - 交叉歧义和组合歧义是主要类型")
print("   - 上下文信息对消歧至关重要")
print("   - 语言模型可以有效辅助歧义消解")

print("\n4. 命名实体识别优化:")
print("   - 规则方法简单高效但覆盖有限")
print("   - CRF方法能够学习序列标注模式")
print("   - 深度学习方法（如BERT-NER）是当前最优方案")

print("\n" + "=" * 80)
print("实验拓展完成！所有结果已保存到output目录")
print("=" * 80)

