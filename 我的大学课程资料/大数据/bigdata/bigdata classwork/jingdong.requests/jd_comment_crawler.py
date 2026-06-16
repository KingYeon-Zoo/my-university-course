# 导入必要的库
import requests
import json
import time
import pandas as pd
import csv as csv_lib
import os
import jieba
 
 
# 函数：发起请求到京东并获取特定页面的数据
def start(page):
    # 构建京东商品评论页面的URL
    url = ('https://club.jd.com/comment/productPageComments.action?'
           '&productId=100142621642'  # 商品ID - 修改为用户指定的ID
           f'&score=0'  # 0表示所有评论，1表示好评，2表示中评，3表示差评，5表示追加评论
           '&sortType=5'  # 排序类型（通常使用5）
           f'&page={page}'  # 要获取的页面数
           '&pageSize=10'  # 每页评论数
           '&isShadowSku=0'
           '&fold=1')
 
    # 设置headers以模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36"
    }
 
    time.sleep(2)
    # 发送GET请求获取数据
    response = requests.get(url=url, headers=headers)
    # 将返回的JSON数据解析为字典
    data = json.loads(response.text)
    return data
 
 
# 解析函数：从返回的数据中提取所需信息
def parse(data):
    items = data['comments']
    for i in items:
        # 处理评论内容并进行分词
        raw_content = i['content'].replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        # 使用jieba进行分词，用空格连接分词结果
        segmented_content = ' '.join(jieba.cut(raw_content))
        yield (segmented_content,)  # 只返回分词后的内容
 
 
# CSV函数：将数据写入CSV文件，适配Hive框架
def csv(items, file_path='jd.csv'):
    # 定义CSV文件的分隔符和其他参数
    separator = '\t'
    csv_params = {
        'sep': separator,
        'encoding': 'utf-8',
        'quoting': csv_lib.QUOTE_MINIMAL,
        'escapechar': '\\',
        'na_rep': 'NULL'
    }
    
    # 如果文件不存在，创建文件并写入列名
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=['分词内容'])
    
    # 将数据转换为列表后再创建DataFrame
    items_list = list(items)
    if not items_list:
        print("没有数据可写入")
        return
        
    # 将数据写入CSV文件，适配Hive格式
    df = pd.DataFrame(items_list, columns=['分词内容'])
    df.to_csv(file_path, index=False, mode='a', header=False, **csv_params)
 
 
# 主函数：控制整个爬取过程
def main():
    # 如果有旧文件导致解析错误，可以选择删除
    if os.path.exists('jd.csv'):
        os.remove('jd.csv')
        print("已删除旧的CSV文件")
        
    total_pages = 1000 # 设置要爬取的总页数
 
    for j in range(total_pages):
        time.sleep(1.5)
        current_page = j + 1
        # 发起请求并获取数据
        data = start(current_page)
        # 解析数据
        parsed_data = parse(data)
        # 将数据写入CSV文件
        csv(parsed_data)
        print('第' + str(current_page) + '页抓取完毕')
 
 
# 如果作为独立脚本运行，则执行主函数
if __name__ == '__main__':
    main()