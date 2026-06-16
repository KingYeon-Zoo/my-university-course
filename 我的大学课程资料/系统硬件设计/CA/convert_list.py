#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown无序列表转有序列表脚本
将报告中的所有无序列表（- 开头）转换为有序列表（1. 2. 3. ...）
"""

import re
import sys
import os


def convert_unordered_to_ordered(content):
    """
    将Markdown中的无序列表转换为有序列表
    
    参数:
        content: Markdown文件内容
        
    返回:
        转换后的内容
    """
    lines = content.split('\n')
    result = []
    in_code_block = False
    list_stack = []  # 用于跟踪不同缩进级别的列表编号
    prev_indent = -1
    
    for line in lines:
        # 检测代码块，避免转换代码块中的内容
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            # 退出代码块时重置列表状态
            if not in_code_block:
                list_stack = []
                prev_indent = -1
            continue
        
        # 在代码块中，直接添加行
        if in_code_block:
            result.append(line)
            continue
        
        # 检测无序列表项：以 "- " 开头（注意有空格）
        # 同时考虑缩进的情况（包括0个或多个空格的缩进）
        match = re.match(r'^(\s*)- (.+)$', line)
        
        if match:
            indent = match.group(1)  # 缩进空格
            content_text = match.group(2)  # 列表项内容
            current_indent = len(indent)
            
            # 处理缩进变化，维护嵌套列表的编号
            if current_indent > prev_indent:
                # 进入更深层次的列表
                list_stack.append(1)
            elif current_indent < prev_indent:
                # 返回上层列表
                # 计算返回了几层
                indent_diff = prev_indent - current_indent
                # 简单处理：假设每次缩进是2或4个空格
                levels_back = indent_diff // 2 if indent_diff >= 2 else 1
                for _ in range(min(levels_back, len(list_stack) - 1)):
                    list_stack.pop()
                if list_stack:
                    list_stack[-1] += 1
                else:
                    list_stack.append(1)
            else:
                # 同一层次的列表项
                if list_stack:
                    list_stack[-1] += 1
                else:
                    list_stack.append(1)
            
            # 获取当前编号
            current_number = list_stack[-1] if list_stack else 1
            
            # 转换为有序列表项
            ordered_line = f"{indent}{current_number}. {content_text}"
            result.append(ordered_line)
            
            prev_indent = current_indent
        else:
            # 非列表项，重置列表状态
            if line.strip() and not line.strip().startswith('#'):
                # 如果是非空行且不是标题，重置列表
                list_stack = []
                prev_indent = -1
            result.append(line)
    
    return '\n'.join(result)


def backup_file(filepath):
    """
    备份原文件
    
    参数:
        filepath: 要备份的文件路径
    """
    backup_path = filepath + '.backup'
    counter = 1
    while os.path.exists(backup_path):
        backup_path = f"{filepath}.backup{counter}"
        counter += 1
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] 已创建备份文件: {backup_path}")
    return backup_path


def main():
    """主函数"""
    # 设置控制台编码为UTF-8（Windows兼容性）
    if sys.platform == 'win32':
        try:
            import codecs
            if sys.stdout.encoding != 'utf-8':
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass  # 如果失败，继续使用默认编码
    
    # 默认处理当前目录下的实验报告.md
    default_file = os.path.join(os.path.dirname(__file__), '实验报告.md')
    
    # 如果命令行提供了文件路径，使用命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = default_file
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"[ERROR] 文件不存在: {input_file}")
        sys.exit(1)
    
    print(f"开始处理文件: {input_file}")
    
    # 备份原文件
    backup_path = backup_file(input_file)
    
    # 读取文件内容
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] 读取文件失败: {e}")
        sys.exit(1)
    
    # 转换无序列表为有序列表
    print("正在转换无序列表为有序列表...")
    converted_content = convert_unordered_to_ordered(content)
    
    # 统计转换数量
    original_count = content.count('\n- ')
    converted_count = converted_content.count('. ')
    
    # 写入转换后的内容
    try:
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        print(f"[OK] 转换完成!")
        print(f"  检测到约 {original_count} 个无序列表项")
        print(f"  已转换为有序列表")
        print(f"  输出文件: {input_file}")
    except Exception as e:
        print(f"[ERROR] 写入文件失败: {e}")
        # 恢复备份
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        print("[INFO] 已从备份恢复原文件")
        sys.exit(1)


if __name__ == '__main__':
    main()

