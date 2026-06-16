import csv
import jieba
import re

def process_csv():
    # 输入和输出文件路径
    input_file = 'jd_hive.csv'
    output_file = 'jd_new_hive.csv'
    
    # 读取CSV文件并处理
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        # 创建CSV读取器和写入器
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # 读取标题行
        try:
            header = next(reader)
            # 写入相同的标题行
            writer.writerow(header)
        except StopIteration:
            print("文件为空或格式不正确")
            return
        
        # 处理每一行数据
        for row in reader:
            if not row:  # 跳过空行
                continue
            
            # 假设CSV格式为: id, 时间, 内容
            # 如果格式不正确，需要调整下面的逻辑
            try:
                # 检查行的格式，因为看到的数据似乎没有明确的分隔符
                if len(row) == 1 and len(row[0]) > 0:
                    # 使用正则表达式分割数据
                    # 假设格式是: id时间内容
                    data = row[0]
                    # 尝试提取id（假设id是纯数字）
                    id_match = re.match(r'(\d+)(.*)', data)
                    if id_match:
                        comment_id = id_match.group(1)
                        rest_data = id_match.group(2)
                        
                        # 尝试提取时间（假设格式为YYYY-MM-DD HH:MM:SS）
                        time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(.*)', rest_data)
                        if time_match:
                            time = time_match.group(1)
                            content = time_match.group(2)
                            
                            # 对内容进行分词
                            seg_list = jieba.cut(content, cut_all=False)
                            segmented_content = ' '.join(seg_list)
                            
                            # 写入新行
                            writer.writerow([comment_id, time, segmented_content])
                        else:
                            print(f"无法解析时间: {rest_data}")
                    else:
                        print(f"无法解析ID: {data}")
                else:
                    # 如果CSV格式正确，直接处理
                    comment_id = row[0]
                    time = row[1] if len(row) > 1 else ""
                    content = row[2] if len(row) > 2 else ""
                    
                    # 对内容进行分词
                    seg_list = jieba.cut(content, cut_all=False)
                    segmented_content = ' '.join(seg_list)
                    
                    # 写入新行
                    writer.writerow([comment_id, time, segmented_content])
            except Exception as e:
                print(f"处理行时出错: {e}")
                print(f"问题行: {row}")
    
    print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    process_csv() 