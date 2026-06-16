# -*- coding: utf-8 -*-
"""
PDF按目录切分工具
根据PDF的二级目录（章、节）切分PDF文件

使用方法：
1. 首先安装依赖：pip install PyMuPDF
2. 运行脚本：python split_pdf_by_toc.py
3. 切分结果将保存在 "切分结果" 文件夹中
"""

import fitz  # PyMuPDF
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def sanitize_filename(name):
    """清理文件名，移除非法字符"""
    # 移除Windows文件名中的非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    name = re.sub(illegal_chars, '_', name)
    # 移除首尾空格和换行
    name = name.strip().replace('\n', ' ').replace('\r', '')
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    return name


def extract_toc(pdf_path):
    """提取PDF目录结构"""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    doc.close()
    return toc


def parse_toc_structure(toc):
    """
    解析目录结构，返回章节信息
    toc格式: [[level, title, page], ...]
    level=1 表示章，level=2 表示节
    """
    chapters = []  # 存储章信息
    current_chapter = None
    
    for item in toc:
        level, title, page = item
        
        if level == 1:
            # 这是一个章
            if current_chapter:
                chapters.append(current_chapter)
            current_chapter = {
                'title': title,
                'start_page': page,
                'end_page': None,
                'sections': []
            }
        elif level == 2 and current_chapter:
            # 这是一个节
            current_chapter['sections'].append({
                'title': title,
                'start_page': page,
                'end_page': None
            })
    
    # 添加最后一个章
    if current_chapter:
        chapters.append(current_chapter)
    
    return chapters


def calculate_end_pages(chapters, total_pages):
    """计算每个章节的结束页码"""
    # 收集所有起始页码
    all_starts = []
    for ch_idx, chapter in enumerate(chapters):
        all_starts.append(('chapter', ch_idx, None, chapter['start_page']))
        for sec_idx, section in enumerate(chapter['sections']):
            all_starts.append(('section', ch_idx, sec_idx, section['start_page']))
    
    # 按页码排序
    all_starts.sort(key=lambda x: x[3])
    
    # 计算结束页码
    for i, item in enumerate(all_starts):
        item_type, ch_idx, sec_idx, start_page = item
        
        # 下一个项目的起始页就是当前项目的结束页
        if i + 1 < len(all_starts):
            end_page = all_starts[i + 1][3]
        else:
            end_page = total_pages + 1
        
        if item_type == 'chapter':
            chapters[ch_idx]['end_page'] = end_page
        else:
            chapters[ch_idx]['sections'][sec_idx]['end_page'] = end_page
    
    # 修正章的结束页：应该包含所有小节
    for chapter in chapters:
        if chapter['sections']:
            # 章的结束页应该是最后一个小节的结束页
            max_end = max(sec['end_page'] for sec in chapter['sections'])
            chapter['end_page'] = max(chapter['end_page'], max_end)
    
    return chapters


def cn_to_num(cn_str):
    """将中文数字转换为阿拉伯数字"""
    cn_nums = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, 
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100, '千': 1000
    }
    
    if cn_str.isdigit():
        return int(cn_str)
    
    result = 0
    temp = 0
    
    for char in cn_str:
        if char in cn_nums:
            num = cn_nums[char]
            if num >= 10:
                if temp == 0:
                    temp = 1
                result += temp * num
                temp = 0
            else:
                temp = num
        else:
            break
    
    result += temp
    return result if result > 0 else None


def extract_chapter_number(title):
    """从标题中提取章节号"""
    # 匹配 "第n章" 或 "第n节" 格式
    match = re.search(r'第\s*([一二三四五六七八九十百千\d]+)\s*[章节]', title)
    if match:
        num_str = match.group(1)
        return cn_to_num(num_str)
    
    # 尝试匹配开头的数字，如 "1.1" 或 "1、"
    match = re.match(r'^(\d+)[\.\s、]', title)
    if match:
        return int(match.group(1))
    
    return None


def extract_section_number(title, chapter_num):
    """从标题中提取小节号"""
    # 匹配 "第n节" 格式
    match = re.search(r'第\s*([一二三四五六七八九十百千\d]+)\s*节', title)
    if match:
        num_str = match.group(1)
        return cn_to_num(num_str)
    
    # 尝试匹配 "n.m" 格式
    match = re.match(rf'^{chapter_num}\.(\d+)', title)
    if match:
        return int(match.group(1))
    
    # 尝试匹配开头的数字
    match = re.match(r'^(\d+)[\.\s、]', title)
    if match:
        return int(match.group(1))
    
    return None


def save_pdf_pages(src_pdf_path, output_path, start_page, end_page):
    """保存指定页码范围的PDF"""
    try:
        src_doc = fitz.open(src_pdf_path)
        new_doc = fitz.open()
        
        # 页码是1-based，fitz使用0-based
        start_idx = start_page - 1
        end_idx = end_page - 1  # end_page是下一个章节的起始页，所以不包含
        
        # 确保页码范围有效
        start_idx = max(0, start_idx)
        end_idx = min(len(src_doc), end_idx)
        
        if start_idx < end_idx:
            new_doc.insert_pdf(src_doc, from_page=start_idx, to_page=end_idx - 1)
            new_doc.save(output_path)
            new_doc.close()
            src_doc.close()
            return True
        
        new_doc.close()
        src_doc.close()
        return False
    except Exception as e:
        print(f"  保存PDF时出错: {e}")
        return False


def split_pdf_by_toc(pdf_path, output_dir=None):
    """主函数：按目录切分PDF"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"错误：文件不存在 - {pdf_path}")
        return
    
    if output_dir is None:
        output_dir = pdf_path.parent / "切分结果"
    else:
        output_dir = Path(output_dir)
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"PDF目录切分工具")
    print(f"{'='*60}")
    print(f"源文件: {pdf_path}")
    print(f"输出目录: {output_dir}")
    
    # 提取目录
    print("\n正在读取PDF目录...")
    toc = extract_toc(pdf_path)
    if not toc:
        print("错误：未找到PDF目录！请确保PDF文件包含书签/目录。")
        return
    
    print(f"找到 {len(toc)} 个目录条目")
    
    # 显示目录预览
    print("\n目录结构预览（前30项）：")
    print("-" * 50)
    for item in toc[:30]:
        level, title, page = item
        indent = "  " * (level - 1)
        print(f"{indent}[L{level}] {title} (p.{page})")
    if len(toc) > 30:
        print(f"  ... 还有 {len(toc) - 30} 个条目")
    print("-" * 50)
    
    # 获取PDF总页数
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    print(f"\nPDF总页数: {total_pages}")
    
    # 解析目录结构
    chapters = parse_toc_structure(toc)
    print(f"识别到 {len(chapters)} 个章节")
    
    if not chapters:
        print("错误：未能解析出章节结构！")
        print("请检查PDF目录是否为二级结构（章-节）。")
        return
    
    # 计算结束页码
    chapters = calculate_end_pages(chapters, total_pages)
    
    # 显示章节信息
    print("\n章节详情：")
    print("=" * 60)
    for i, chapter in enumerate(chapters):
        ch_num = extract_chapter_number(chapter['title']) or (i + 1)
        print(f"\n【第{ch_num}章】{chapter['title']}")
        print(f"  页码: {chapter['start_page']} - {chapter['end_page'] - 1}")
        print(f"  小节数: {len(chapter['sections'])}")
        if chapter['sections']:
            for j, section in enumerate(chapter['sections']):
                sec_num = extract_section_number(section['title'], ch_num) or (j + 1)
                print(f"    {ch_num}.{sec_num} {section['title']} (p.{section['start_page']}-{section['end_page']-1})")
    
    # 开始切分
    print("\n" + "=" * 60)
    print("开始切分PDF...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, chapter in enumerate(chapters):
        ch_num = extract_chapter_number(chapter['title']) or (i + 1)
        
        # 创建章文件夹
        chapter_folder_name = f"第{ch_num}章"
        chapter_folder = output_dir / chapter_folder_name
        chapter_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n处理 {chapter_folder_name}: {chapter['title'][:30]}...")
        
        # 保存整章PDF
        chapter_title_clean = sanitize_filename(chapter['title'])
        # 移除各种前缀格式，避免重复
        chapter_title_short = chapter_title_clean
        # 移除 "第X章" 格式
        chapter_title_short = re.sub(r'^第[一二三四五六七八九十百千\d]+章\s*', '', chapter_title_short)
        # 移除 "X.Y" 或 "X.Y.Z" 数字前缀格式
        chapter_title_short = re.sub(r'^\d+(\.\d+)*\s*', '', chapter_title_short)
        # 移除 "X、" 或 "X " 数字前缀格式
        chapter_title_short = re.sub(r'^\d+[、\s]\s*', '', chapter_title_short)
        if not chapter_title_short:
            chapter_title_short = chapter_title_clean
        chapter_pdf_name = f"{ch_num}.【整章】{chapter_title_short}.pdf"
        chapter_pdf_path = chapter_folder / chapter_pdf_name
        
        success = save_pdf_pages(
            str(pdf_path),
            str(chapter_pdf_path),
            chapter['start_page'],
            chapter['end_page']
        )
        
        if success:
            print(f"  ✓ 整章: {chapter_pdf_name}")
            success_count += 1
        else:
            print(f"  ✗ 整章保存失败: {chapter_pdf_name}")
            fail_count += 1
        
        # 保存各小节PDF
        for j, section in enumerate(chapter['sections']):
            sec_num = extract_section_number(section['title'], ch_num) or (j + 1)
            section_title_clean = sanitize_filename(section['title'])
            # 移除各种前缀格式
            section_title_short = section_title_clean
            # 移除 "第X节" 格式
            section_title_short = re.sub(r'^第[一二三四五六七八九十百千\d]+节\s*', '', section_title_short)
            # 移除 "X.Y" 或 "X.Y.Z" 数字前缀格式
            section_title_short = re.sub(r'^\d+(\.\d+)*\s*', '', section_title_short)
            # 移除 "X、" 或 "X " 数字前缀格式
            section_title_short = re.sub(r'^\d+[、\s]\s*', '', section_title_short)
            if not section_title_short:
                section_title_short = section_title_clean
            
            section_pdf_name = f"{ch_num}.{sec_num}.{section_title_short}.pdf"
            section_pdf_path = chapter_folder / section_pdf_name
            
            success = save_pdf_pages(
                str(pdf_path),
                str(section_pdf_path),
                section['start_page'],
                section['end_page']
            )
            
            if success:
                print(f"  ✓ 小节: {section_pdf_name}")
                success_count += 1
            else:
                print(f"  ✗ 小节保存失败: {section_pdf_name}")
                fail_count += 1
    
    # 完成总结
    print("\n" + "=" * 60)
    print("切分完成！")
    print("=" * 60)
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")
    print(f"输出目录: {output_dir}")
    print("\n请查看输出目录获取切分后的PDF文件。")


if __name__ == "__main__":
    # PDF文件路径
    pdf_path = r"D:\Users\Desktop\大模型基础\大模型基础 完整版.pdf"
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误：文件不存在 - {pdf_path}")
        print("请确保PDF文件路径正确。")
        input("按回车键退出...")
        sys.exit(1)
    
    try:
        # 执行切分
        split_pdf_by_toc(pdf_path)
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 等待用户确认
    print("\n")
    input("按回车键退出...")
