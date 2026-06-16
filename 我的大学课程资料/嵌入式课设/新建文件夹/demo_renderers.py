# 渲染方法演示脚本
from extract_flowcharts import extract_all_flowcharts_from_report
from alternative_renderers import AlternativeRenderer
import time

def demo_svg_rendering():
    """演示 SVG 渲染"""
    print("🎨 SVG 渲染演示")
    print("="*50)
    
    # 提取流程图
    flowcharts = extract_all_flowcharts_from_report()
    
    # 只渲染前3个作为演示
    demo_charts = flowcharts[:3]
    
    # SVG 渲染
    svg_renderer = AlternativeRenderer('svg', 'svg_output')
    start_time = time.time()
    svg_files = svg_renderer.render_all_graphs(demo_charts)
    svg_time = time.time() - start_time
    
    print(f"\n✅ SVG 渲染完成")
    print(f"耗时: {svg_time:.2f} 秒")
    print(f"生成 {len(svg_files)} 个 SVG 文件")
    
    return svg_files

def demo_matplotlib_rendering():
    """演示 Matplotlib 渲染"""
    print("\n🎨 Matplotlib 渲染演示")
    print("="*50)
    
    # 提取流程图
    flowcharts = extract_all_flowcharts_from_report()
    
    # 只渲染前3个作为演示
    demo_charts = flowcharts[:3]
    
    # Matplotlib 渲染
    mpl_renderer = AlternativeRenderer('matplotlib', 'matplotlib_output')
    start_time = time.time()
    mpl_files = mpl_renderer.render_all_graphs(demo_charts)
    mpl_time = time.time() - start_time
    
    print(f"\n✅ Matplotlib 渲染完成")
    print(f"耗时: {mpl_time:.2f} 秒")
    print(f"生成 {len(mpl_files)} 个 PNG 文件")
    
    return mpl_files

if __name__ == "__main__":
    print("🚀 多种渲染方法演示")
    print("="*80)
    
    # 演示 SVG 渲染
    svg_files = demo_svg_rendering()
    
    # 演示 Matplotlib 渲染
    mpl_files = demo_matplotlib_rendering()
    
    print("\n📊 演示总结")
    print("="*50)
    print(f"SVG 文件: {len(svg_files)} 个 (位于 svg_output/ 目录)")
    print(f"PNG 文件: {len(mpl_files)} 个 (位于 matplotlib_output/ 目录)")
    print("\n现在您可以比较不同渲染方法的效果！") 