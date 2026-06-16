#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将CSV文件从制表符分隔格式转换为Hive默认的'\001'分隔符格式
"""

import os
import sys

def convert_delimiter(input_file, output_file):
    """
    将输入文件从制表符分隔转换为'\001'分隔
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                # 替换制表符为'\001'
                converted_line = line.strip().replace('\t', '\001')
                outfile.write(converted_line + '\n')
    
    print(f"转换完成：{input_file} → {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python convert_delimiter.py <输入文件> <输出文件>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    convert_delimiter(input_file, output_file) 