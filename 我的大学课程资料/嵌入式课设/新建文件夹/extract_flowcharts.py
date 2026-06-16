# 从实验报告中提取所有Mermaid流程图
from mermaid_parser import extract_mermaid_from_markdown, MermaidParser
from graph_data import Graph
from typing import List, Tuple
import os

def extract_all_flowcharts_from_report() -> List[Tuple[str, Graph]]:
    """从实验报告中提取所有流程图并转换为Graph对象"""
    
    # 读取实验报告文件
    report_file = "实验报告.md"
    if not os.path.exists(report_file):
        raise FileNotFoundError(f"找不到实验报告文件：{report_file}")
    
    with open(report_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # 提取所有Mermaid代码块
    mermaid_blocks = extract_mermaid_from_markdown(markdown_content)
    print(f"从实验报告中找到 {len(mermaid_blocks)} 个流程图")
    
    # 创建解析器
    parser = MermaidParser()
    graphs = []
    
    # 解析每个Mermaid代码块
    for i, (title, mermaid_code) in enumerate(mermaid_blocks):
        try:
            print(f"\n正在解析流程图 {i+1}: {title}")
            print(f"Mermaid代码长度: {len(mermaid_code)} 字符")
            
            # 解析为Graph对象
            graph = parser.parse_mermaid_text(mermaid_code, title)
            graphs.append((title, graph))
            
            print(f"解析成功：{len(graph.nodes)} 个节点，{len(graph.edges)} 条边")
            
        except Exception as e:
            print(f"解析流程图 {i+1} 时出错：{e}")
            continue
    
    return graphs

def print_flowchart_summary(graphs: List[Tuple[str, Graph]]):
    """打印流程图摘要信息"""
    print("\n" + "="*60)
    print("流程图提取结果摘要")
    print("="*60)
    
    for i, (title, graph) in enumerate(graphs, 1):
        print(f"\n{i}. {title}")
        print(f"   类型: {graph.graph_type.value}")
        print(f"   节点数: {len(graph.nodes)}")
        print(f"   边数: {len(graph.edges)}")
        
        # 显示节点类型统计
        from collections import Counter
        node_types = Counter(node.node_type.value for node in graph.nodes)
        print(f"   节点类型分布: {dict(node_types)}")

if __name__ == "__main__":
    try:
        # 提取所有流程图
        flowcharts = extract_all_flowcharts_from_report()
        
        # 打印摘要
        print_flowchart_summary(flowcharts)
        
        # 保存提取结果供后续使用
        print(f"\n成功提取 {len(flowcharts)} 个流程图，准备进行渲染...")
        
    except Exception as e:
        print(f"提取流程图时发生错误：{e}")
        import traceback
        traceback.print_exc() 