# 多种渲染方法选择器
from extract_flowcharts import extract_all_flowcharts_from_report
from alternative_renderers import AlternativeRenderer
from graphviz_detector import GraphvizDetector
import time
import os

def show_menu():
    """显示渲染方法选择菜单"""
    print("\n" + "="*80)
    print("🎨 流程图渲染方法选择器")
    print("="*80)
    print("可用的渲染方法:")
    print("1. Graphviz 渲染 (推荐) - 专业级矢量图渲染")
    print("2. Matplotlib 渲染 - Python 原生渲染，兼容性好")
    print("3. NetworkX 渲染 - 网络图风格，适合复杂关系")
    print("4. SVG 渲染 - 轻量级矢量图，体积小")
    print("5. Plotly 交互式渲染 - 可交互的 HTML 图表")
    print("6. 对比渲染 - 使用多种方法渲染同一组图表")
    print("0. 退出")
    print("="*80)

def get_user_choice():
    """获取用户选择"""
    while True:
        try:
            choice = int(input("\n请选择渲染方法 (0-6): "))
            if 0 <= choice <= 6:
                return choice
            else:
                print("❌ 请输入有效的选项 (0-6)")
        except ValueError:
            print("❌ 请输入数字")

def render_with_method(method: str, flowcharts: list):
    """使用指定方法渲染"""
    
    print(f"\n开始使用 {method.upper()} 方法渲染...")
    start_time = time.time()
    
    try:
        if method == "graphviz":
            # 使用 Graphviz 渲染
            detector = GraphvizDetector()
            if detector.detect_graphviz():
                from render_engine import BatchRenderer
                graphviz_path = detector.get_graphviz_directory()
                renderer = BatchRenderer(graphviz_path=graphviz_path)
            else:
                print("❌ 未检测到 Graphviz，切换到 Matplotlib")
                renderer = AlternativeRenderer("matplotlib")
        else:
            # 使用替代渲染器
            renderer = AlternativeRenderer(method)
        
        # 渲染所有图表
        rendered_files = renderer.render_all_graphs(flowcharts)
        
        # 统计结果
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n✅ 渲染完成!")
        print(f"耗时: {elapsed_time:.2f} 秒")
        print(f"成功: {len(rendered_files)}/{len(flowcharts)} 个")
        
        # 显示生成的文件
        if rendered_files:
            print(f"\n生成的文件 ({method.upper()}):")
            for i, file_path in enumerate(rendered_files, 1):
                file_name = os.path.basename(file_path)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path) / 1024
                    print(f"  {i:2d}. {file_name} ({file_size:.1f} KB)")
                else:
                    print(f"  {i:2d}. {file_name} (文件不存在)")
        
        return rendered_files
        
    except Exception as e:
        print(f"❌ 渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def compare_render_methods(flowcharts: list):
    """对比多种渲染方法"""
    
    methods = [
        ("graphviz", "Graphviz"),
        ("matplotlib", "Matplotlib"),
        ("networkx", "NetworkX"),
        ("svg", "SVG")
    ]
    
    print(f"\n🔍 对比渲染模式 - 将使用 {len(methods)} 种方法渲染所有流程图")
    print("="*80)
    
    all_results = {}
    
    for method_key, method_name in methods:
        print(f"\n正在使用 {method_name} 渲染...")
        
        # 为每种方法创建单独的输出目录
        output_dir = f"flowchart_output_{method_key}"
        
        try:
            if method_key == "graphviz":
                detector = GraphvizDetector()
                if detector.detect_graphviz():
                    from render_engine import BatchRenderer
                    graphviz_path = detector.get_graphviz_directory()
                    renderer = BatchRenderer(output_dir, graphviz_path)
                else:
                    print(f"  ⚠️ Graphviz 不可用，跳过")
                    continue
            else:
                renderer = AlternativeRenderer(method_key, output_dir)
            
            start_time = time.time()
            rendered_files = renderer.render_all_graphs(flowcharts)
            end_time = time.time()
            
            all_results[method_name] = {
                'files': rendered_files,
                'time': end_time - start_time,
                'success_rate': len(rendered_files) / len(flowcharts) * 100
            }
            
            print(f"  ✅ {method_name}: {len(rendered_files)}/{len(flowcharts)} 个成功, 耗时 {end_time - start_time:.2f}s")
            
        except Exception as e:
            print(f"  ❌ {method_name} 失败: {e}")
            all_results[method_name] = {
                'files': [],
                'time': 0,
                'success_rate': 0
            }
    
    # 生成对比报告
    print(f"\n📊 渲染方法对比报告")
    print("="*80)
    print(f"{'方法':<15} {'成功率':<10} {'耗时(秒)':<10} {'文件数':<10}")
    print("-"*50)
    
    for method_name, result in all_results.items():
        print(f"{method_name:<15} {result['success_rate']:>7.1f}% {result['time']:>8.2f}s {len(result['files']):>8d}")
    
    print("="*80)
    
    return all_results

def main():
    """主函数"""
    
    print("正在提取流程图...")
    flowcharts = extract_all_flowcharts_from_report()
    
    if not flowcharts:
        print("❌ 未找到任何流程图")
        return
    
    print(f"✅ 成功提取 {len(flowcharts)} 个流程图")
    
    while True:
        show_menu()
        choice = get_user_choice()
        
        if choice == 0:
            print("👋 再见!")
            break
        elif choice == 1:
            render_with_method("graphviz", flowcharts)
        elif choice == 2:
            render_with_method("matplotlib", flowcharts)
        elif choice == 3:
            render_with_method("networkx", flowcharts)
        elif choice == 4:
            render_with_method("svg", flowcharts)
        elif choice == 5:
            render_with_method("plotly", flowcharts)
        elif choice == 6:
            compare_render_methods(flowcharts)
        
        input("\n按 Enter 键继续...")

if __name__ == "__main__":
    main() 