import pandas as pd
import re

# 读取原始CSV文件（处理可能的格式问题）
try:
    # 尝试不同编码方式和分隔符
    df = pd.read_csv('node1_.csv', sep=None, engine='python', encoding='utf-8')
except:
    df = pd.read_csv('node1_.csv', sep=None, engine='python', encoding='gbk')

# 检查列名并重命名（根据实际文件结构调整）
df.columns = ['word', 'frequency'][:len(df.columns)]

# 定义过滤条件：排除纯数字和标点符号
def is_valid_word(word):
    if pd.isna(word):
        return False
    str_word = str(word).strip()
    if re.fullmatch(r'\d+', str_word):
        return False
    if re.fullmatch(r'[\W_]+', str_word):
        return False
    return True

# 应用过滤条件
filtered = df[df['word'].apply(is_valid_word)]

# 取前100个高频词
top_100 = filtered.sort_values(by='frequency', ascending=False).head(100)

# 保存结果
top_100.to_csv('top_100_words.csv', index=False, encoding='utf-8-sig')