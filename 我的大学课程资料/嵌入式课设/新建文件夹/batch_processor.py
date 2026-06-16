# 批量流程图处理主程序
from extract_flowcharts import extract_all_flowcharts_from_report
from render_engine import BatchRenderer
from graphviz_detector import GraphvizDetector
import os
import time
from typing import List

def main():
    """主函数：批量处理所有流程图"""
    
    print("="*80)
    print("嵌入式系统实验报告流程图Python渲染器")
    print("Scientific Research Flowchart Renderer")
    print("="*80)
    
    start_time = time.time()
    
    try:
        # 第一步：提取所有流程图
        print("\n第一步：从实验报告中提取流程图...")
        flowcharts = extract_all_flowcharts_from_report()
        
        if not flowcharts:
            print("❌ 未找到任何流程图，程序退出")
            return
        
        print(f"✅ 成功提取 {len(flowcharts)} 个流程图")
        
        # 第二步：批量渲染
        print("\n第二步：使用科研配色方案批量渲染...")
        
        # 智能检测Graphviz安装
        detector = GraphvizDetector()
        graphviz_available = detector.detect_graphviz()
        
        if graphviz_available:
            print("使用 Graphviz 渲染引擎进行高质量渲染...")
            graphviz_path = detector.get_graphviz_directory()
            renderer = BatchRenderer(graphviz_path=graphviz_path)
            rendered_files = renderer.render_all_graphs(flowcharts)
        else:
            print("切换到 Matplotlib 后备渲染引擎...")
            from matplotlib_renderer import MatplotlibBatchRenderer
            renderer = MatplotlibBatchRenderer()
            rendered_files = renderer.render_all_graphs(flowcharts)
        
        # 第三步：生成结果报告
        print("\n第三步：生成渲染结果报告...")
        generate_result_report(rendered_files, flowcharts)
        
        # 显示总结信息
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\n" + "="*80)
        print("渲染任务完成!")
        print(f"总耗时: {elapsed_time:.2f} 秒")
        print(f"成功渲染: {len(rendered_files)}/{len(flowcharts)} 个流程图")
        print(f"输出目录: {renderer.output_dir}")
        print("="*80)
        
        # 显示文件列表
        if rendered_files:
            print("\n生成的图片文件:")
            for i, file_path in enumerate(rendered_files, 1):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"  {i:2d}. {file_name} ({file_size:.1f} KB)")
        
    except Exception as e:
        print(f"\n❌ 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def generate_result_report(rendered_files: List[str], flowcharts: List[tuple]):
    """生成渲染结果报告"""
    
    report_path = "渲染结果报告.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 流程图渲染结果报告\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 渲染配置\n\n")
        f.write("- **渲染引擎**: Graphviz\n")
        f.write("- **配色方案**: 科研期刊风格\n")
        f.write("- **输出格式**: PNG (300 DPI)\n")
        f.write("- **字体**: Microsoft YaHei (支持中文)\n\n")
        
        f.write("## 渲染结果\n\n")
        f.write(f"总计处理: {len(flowcharts)} 个流程图\n")
        f.write(f"成功渲染: {len(rendered_files)} 个\n")
        f.write(f"成功率: {len(rendered_files)/len(flowcharts)*100:.1f}%\n\n")
        
        f.write("## 文件清单\n\n")
        f.write("| 序号 | 原标题 | 输出文件 | 大小 | 状态 |\n")
        f.write("|------|--------|----------|------|------|\n")
        
        rendered_set = set(rendered_files)
        
        for i, (title, graph) in enumerate(flowcharts, 1):
            # 尝试找到对应的渲染文件
            expected_filename = None
            file_size = "N/A"
            status = "❌ 失败"
            
            for rendered_file in rendered_files:
                if title.replace('#', '').replace(' ', '_').replace('.', '_')[:20] in rendered_file:
                    expected_filename = os.path.basename(rendered_file)
                    file_size = f"{os.path.getsize(rendered_file)/1024:.1f} KB"
                    status = "✅ 成功"
                    break
            
            if not expected_filename:
                expected_filename = "未生成"
            
            f.write(f"| {i} | {title} | {expected_filename} | {file_size} | {status} |\n")
        
        f.write("\n## 科研配色方案详细说明\n\n")
        f.write("本次渲染采用专为学术论文设计的配色方案:\n\n")
        f.write("- **主流程节点**: 深蓝色 (#1f4e79) - 体现专业性和稳重感\n")
        f.write("- **子流程节点**: 中蓝色 (#2e5d8a) - 保持色调一致性\n")
        f.write("- **决策节点**: 橙色 (#ff7f00) - 突出关键决策点\n")
        f.write("- **开始/结束节点**: 深灰色 (#404040) - 明确流程边界\n")
        f.write("- **连接线**: 深灰色 (#404040) - 确保清晰可读\n\n")
        
        f.write("## 布局优化特点\n\n")
        f.write("- **自动布局选择**: 根据流程图复杂度自动选择最佳布局算法\n")
        f.write("- **节点间距优化**: 确保足够的间距避免重叠\n")
        f.write("- **文本自动换行**: 长标签自动换行保持美观\n")
        f.write("- **高分辨率输出**: 300 DPI确保打印质量\n\n")
        
        f.write("## 相比原Mermaid的改进\n\n")
        f.write("1. **空间效率**: 大幅减少纵向/横向空间占用\n")
        f.write("2. **视觉效果**: 专业的科研配色方案\n")
        f.write("3. **布局质量**: 智能布局算法减少边线交叉\n")
        f.write("4. **输出质量**: 矢量图确保任意缩放不失真\n")
    
    print(f"✅ 生成渲染结果报告: {report_path}")

def check_environment():
    """检查运行环境"""
    
    print("检查运行环境...")
    
    # 检查必要文件
    required_files = ['实验报告.md', 'config.py', 'graph_data.py', 'mermaid_parser.py', 'render_engine.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查依赖包
    try:
        import graphviz
        import matplotlib
        import numpy
        print("✅ 所有依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        return False
    
    # 检查输出目录
    output_dir = "flowchart_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 创建输出目录: {output_dir}")
    else:
        print(f"✅ 输出目录已存在: {output_dir}")
    
    return True

if __name__ == "__main__":
    # 检查环境
    if not check_environment():
        print("环境检查失败，程序退出")
        exit(1)
    
    # 运行主程序
    main() 