#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级图表生成系统主程序
=====================

用于替换实验报告中简单mermaid图表的Python图表生成系统。
支持生成专业级别的2D彩色图表、弧线连接和复杂视觉效果。

作者: AI Assistant
日期: 2024
版本: 1.0
"""

import os
import sys
import argparse
import time
from typing import List, Optional

# 导入所有图表生成器
try:
    from diagram_manager import DiagramManager
    from system_architecture_generator import SystemArchitectureGenerator
    from flowchart_generator import FlowchartGenerator
    from state_machine_generator import StateMachineGenerator
    from hardware_diagram_generator import HardwareDiagramGenerator
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有必要的Python文件都在当前目录中")
    sys.exit(1)


def print_banner():
    """打印程序横幅"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                    高级图表生成系统 v1.0                        ║
║                                                                ║
║  用于生成专业级别的嵌入式系统图表，替换简单的mermaid图表          ║
║  支持: 彩色设计 | 弧线连接 | 渐变色彩 | 高分辨率输出             ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_progress(step: int, total: int, description: str):
    """打印进度信息"""
    percentage = (step / total) * 100
    bar_length = 30
    filled_length = int(bar_length * step / total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    print(f"\r[{bar}] {percentage:.1f}% - {description}", end='', flush=True)
    if step == total:
        print()  # 完成时换行


def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    required_packages = [
        'matplotlib', 'numpy', 'networkx', 
        'plotly', 'PIL', 'graphviz'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖项检查通过")
    return True


def generate_individual_diagram(diagram_type: str, output_dir: str = "generated_diagrams"):
    """生成单个类型的图表"""
    print(f"\n📊 生成{diagram_type}图表...")
    
    try:
        if diagram_type == "系统架构":
            generator = SystemArchitectureGenerator()
            generator.generate_architecture_diagram(output_dir)
            generator.generate_module_interaction_diagram(output_dir)
            print("✅ 系统架构图生成完成")
            
        elif diagram_type == "流程图":
            generator = FlowchartGenerator()
            generator.generate_main_system_flowchart(output_dir)
            generator.generate_key_detection_flowchart(output_dir)
            print("✅ 流程图生成完成")
            
        elif diagram_type == "状态机":
            generator = StateMachineGenerator()
            generator.generate_led_state_machine(output_dir)
            print("✅ 状态机图生成完成")
            
        elif diagram_type == "硬件交互":
            generator = HardwareDiagramGenerator()
            generator.generate_gpio_hardware_diagram(output_dir)
            print("✅ 硬件交互图生成完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成{diagram_type}图表失败: {str(e)}")
        return False


def generate_all_diagrams(output_dir: str = "generated_diagrams"):
    """生成所有图表"""
    print(f"\n🚀 开始生成所有图表到目录: {output_dir}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义所有图表类型
    diagram_types = [
        "系统架构",
        "流程图", 
        "状态机",
        "硬件交互"
    ]
    
    success_count = 0
    total_count = len(diagram_types)
    
    start_time = time.time()
    
    for i, diagram_type in enumerate(diagram_types, 1):
        print_progress(i-1, total_count, f"准备生成{diagram_type}图表")
        time.sleep(0.5)  # 短暂延迟以显示进度
        
        if generate_individual_diagram(diagram_type, output_dir):
            success_count += 1
        
        print_progress(i, total_count, f"已完成{diagram_type}图表")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 使用DiagramManager生成索引文件
    try:
        manager = DiagramManager()
        manager._generate_index_file(output_dir)
        print(f"\n📋 已生成图表索引文件: {output_dir}/README.md")
    except Exception as e:
        print(f"⚠️  生成索引文件失败: {str(e)}")
    
    # 输出最终结果
    print(f"\n{'='*60}")
    print(f"📊 图表生成完成!")
    print(f"✅ 成功: {success_count}/{total_count} 个图表")
    print(f"⏱️  用时: {duration:.2f} 秒")
    print(f"📁 输出目录: {os.path.abspath(output_dir)}")
    
    if success_count == total_count:
        print("🎉 所有图表生成成功!")
    else:
        print(f"⚠️  {total_count - success_count} 个图表生成失败")
    
    print(f"{'='*60}")


def list_available_diagrams():
    """列出可用的图表类型"""
    print("\n📋 可用的图表类型:")
    diagrams = [
        ("系统架构", "彩色分层架构图和模块交互图"),
        ("流程图", "主系统流程图和按键检测流程图"),
        ("状态机", "LED控制状态机图"),
        ("硬件交互", "GPIO硬件原理图")
    ]
    
    for name, description in diagrams:
        print(f"  • {name:<10} - {description}")


def main():
    """主函数"""
    print_banner()
    
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description="高级图表生成系统 - 替换简单mermaid图表的专业解决方案",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 生成所有图表
  python main.py --type 系统架构     # 只生成系统架构图
  python main.py --output my_diagrams # 指定输出目录
  python main.py --list             # 列出可用图表类型
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['系统架构', '流程图', '状态机', '硬件交互'],
        help='指定要生成的图表类型'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='generated_diagrams',
        help='指定输出目录 (默认: generated_diagrams)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有可用的图表类型'
    )
    
    parser.add_argument(
        '--no-check',
        action='store_true',
        help='跳过依赖项检查'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 处理列表请求
    if args.list:
        list_available_diagrams()
        return
    
    # 检查依赖项
    if not args.no_check:
        if not check_dependencies():
            sys.exit(1)
    
    try:
        # 根据参数执行相应操作
        if args.type:
            # 生成指定类型的图表
            success = generate_individual_diagram(args.type, args.output)
            if success:
                print(f"\n🎉 {args.type}图表生成成功!")
                print(f"📁 保存位置: {os.path.abspath(args.output)}")
            else:
                print(f"\n❌ {args.type}图表生成失败!")
                sys.exit(1)
        else:
            # 生成所有图表
            generate_all_diagrams(args.output)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 