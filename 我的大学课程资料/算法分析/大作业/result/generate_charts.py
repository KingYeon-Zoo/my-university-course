#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 Reflexion 实验结果的专业可视化图表
使用 matplotlib 生成高质量的图表
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib import font_manager
import sys
import os

# 解决中文显示问题
def setup_chinese_font():
    """设置中文字体"""
    # Windows常用中文字体列表
    chinese_fonts = [
        'Microsoft YaHei',
        'SimHei',
        'KaiTi',
        'FangSong',
        'SimSun',
        'STSong',
        'STKaiti'
    ]
    
    # 获取系统所有可用字体
    available_fonts = [f.name for f in font_manager.fontManager.ttflist]
    
    # 找到第一个可用的中文字体
    for font in chinese_fonts:
        if font in available_fonts:
            matplotlib.rcParams['font.sans-serif'] = [font]
            matplotlib.rcParams['axes.unicode_minus'] = False
            print(f"使用中文字体: {font}")
            return
    
    # 如果没有找到，使用默认设置
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    print("警告: 未找到合适的中文字体，可能会显示方块")

# 设置中文字体
setup_chinese_font()

# 设置全局样式
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        pass  # 使用默认样式


def plot_success_rate_trend():
    """Plot success rate trend over trials"""
    
    trials = list(range(0, 11))
    success_rates = [40.3, 47.8, 55.2, 63.4, 70.9, 79.1, 85.8, 88.1, 90.3, 91.8, 93.3]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot baseline
    ax.axhline(y=success_rates[0], color='red', linestyle='--', 
               linewidth=2, alpha=0.5, label=f'Baseline: {success_rates[0]}%')
    
    # Plot success rate curve
    ax.plot(trials, success_rates, marker='o', linewidth=3, 
            markersize=10, color='#2E86AB', label='Reflexion Success Rate')
    
    # Fill area between baseline and curve
    ax.fill_between(trials, success_rates[0], success_rates, 
                     alpha=0.3, color='#2E86AB', label='Performance Improvement')
    
    # Annotate key points
    for i, (trial, rate) in enumerate(zip(trials, success_rates)):
        if i in [0, 5, 10]:  # Annotate baseline, middle, and final
            ax.annotate(f'{rate}%', 
                       xy=(trial, rate), 
                       xytext=(0, 10 if i != 0 else -20),
                       textcoords='offset points',
                       ha='center',
                       fontsize=11,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', 
                                facecolor='yellow' if i == 10 else 'white',
                                alpha=0.7))
    
    ax.set_xlabel('Trial Number (0=Baseline)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Success Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('Reflexion Success Rate Trend on ALFWorld', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(trials)
    ax.set_ylim([30, 100])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12, loc='lower right')
    
    plt.tight_layout()
    plt.savefig('result/Chart1_Success_Rate_Trend.png', dpi=300, bbox_inches='tight')
    print("[OK] Generated: Chart1_Success_Rate_Trend.png")
    plt.close()


def plot_method_comparison():
    """Plot method comparison"""
    
    methods = ["Baseline\n(No Memory)", "ReAct", "Chain-of-\nThought", 
               "Reflexion\n(1 Trial)", "Reflexion\n(5 Trials)", 
               "Reflexion\n(10 Trials)", "Human\nExpert"]
    success_rates = [40.3, 45.2, 42.8, 47.8, 79.1, 93.3, 95.0]
    colors = ['#E63946', '#F77F00', '#FCBF49', '#06D6A0', '#118AB2', '#073B4C', '#8338EC']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars = ax.bar(methods, success_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add reference lines
    ax.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax.axhline(y=75, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax.axhline(y=90, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    ax.set_ylabel('Success Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('Performance Comparison on ALFWorld Tasks', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim([0, 105])
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('result/Chart2_Method_Comparison.png', dpi=300, bbox_inches='tight')
    print("[OK] Generated: Chart2_Method_Comparison.png")
    plt.close()


def plot_task_type_breakdown():
    """Plot task type breakdown"""
    
    tasks = ["Pick &\nPlace", "Clean &\nPlace", "Heat &\nPlace", "Cool &\nPlace", "Look at\nObject", "Pick Two\n& Place"]
    reflexion_rates = [95.2, 93.8, 91.5, 92.7, 94.3, 89.4]
    baseline_rates = [42.1, 38.5, 39.2, 40.8, 42.5, 36.8]
    
    x = np.arange(len(tasks))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width/2, baseline_rates, width, label='Baseline', 
                   color='#E63946', alpha=0.8, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + width/2, reflexion_rates, width, label='Reflexion (10 Trials)', 
                   color='#06D6A0', alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add improvement arrows and text
    for i, (base, refl) in enumerate(zip(baseline_rates, reflexion_rates)):
        improvement = refl - base
        ax.annotate('', xy=(i, refl - 2), xytext=(i, base + 2),
                   arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
        ax.text(i + 0.4, (base + refl) / 2, f'+{improvement:.1f}%', 
               fontsize=9, color='purple', fontweight='bold')
    
    ax.set_ylabel('Success Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title('Performance Comparison by Task Type', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontsize=11)
    ax.set_ylim([0, 105])
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('result/Chart3_Task_Type_Analysis.png', dpi=300, bbox_inches='tight')
    print("[OK] Generated: Chart3_Task_Type_Analysis.png")
    plt.close()


def plot_improvement_heatmap():
    """Plot performance improvement analysis"""
    
    trials = list(range(1, 11))
    success_rates = [47.8, 55.2, 63.4, 70.9, 79.1, 85.8, 88.1, 90.3, 91.8, 93.3]
    base_rate = 40.3
    improvements = [(rate - base_rate) / base_rate * 100 for rate in success_rates]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Relative improvement
    colors_gradient = plt.cm.RdYlGn(np.linspace(0.3, 1, len(trials)))
    bars = ax1.barh(trials, improvements, color=colors_gradient, 
                     edgecolor='black', linewidth=1.5, alpha=0.9)
    
    for i, (bar, imp) in enumerate(zip(bars, improvements)):
        width = bar.get_width()
        ax1.text(width + 2, bar.get_y() + bar.get_height()/2.,
                f'+{imp:.1f}%',
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    ax1.set_xlabel('Relative Improvement over Baseline (%)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Trial Number', fontsize=13, fontweight='bold')
    ax1.set_title('Relative Performance Improvement', fontsize=14, fontweight='bold')
    ax1.set_yticks(trials)
    ax1.grid(True, alpha=0.3, axis='x')
    ax1.set_xlim([0, max(improvements) * 1.2])
    
    # Right: Absolute improvement
    absolute_improvements = [rate - base_rate for rate in success_rates]
    bars2 = ax2.barh(trials, absolute_improvements, color=colors_gradient, 
                      edgecolor='black', linewidth=1.5, alpha=0.9)
    
    for i, (bar, imp) in enumerate(zip(bars2, absolute_improvements)):
        width = bar.get_width()
        ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
                f'+{imp:.1f}%',
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    ax2.set_xlabel('Absolute Improvement (Percentage Points)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Trial Number', fontsize=13, fontweight='bold')
    ax2.set_title('Absolute Performance Improvement', fontsize=14, fontweight='bold')
    ax2.set_yticks(trials)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim([0, max(absolute_improvements) * 1.2])
    
    plt.tight_layout()
    plt.savefig('result/Chart4_Performance_Improvement.png', dpi=300, bbox_inches='tight')
    print("[OK] Generated: Chart4_Performance_Improvement.png")
    plt.close()


def plot_learning_curve():
    """Plot learning curve with incremental improvements"""
    
    trials = list(range(0, 11))
    success_rates = [40.3, 47.8, 55.2, 63.4, 70.9, 79.1, 85.8, 88.1, 90.3, 91.8, 93.3]
    incremental = [0] + [success_rates[i] - success_rates[i-1] for i in range(1, len(success_rates))]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Top: Cumulative success rate
    ax1.plot(trials, success_rates, marker='o', linewidth=3, 
             markersize=10, color='#2E86AB', label='Cumulative Success Rate')
    ax1.fill_between(trials, 0, success_rates, alpha=0.3, color='#2E86AB')
    ax1.axhline(y=40.3, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Baseline')
    ax1.axhline(y=90, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Target (90%)')
    ax1.set_ylabel('Success Rate (%)', fontsize=13, fontweight='bold')
    ax1.set_title('Reflexion Learning Curve', fontsize=16, fontweight='bold', pad=15)
    ax1.set_ylim([0, 100])
    ax1.legend(fontsize=11, loc='lower right')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Incremental improvement
    colors = ['gray' if x == 0 else '#06D6A0' if x > 5 else '#F77F00' for x in incremental]
    bars = ax2.bar(trials, incremental, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=1.2)
    
    for bar, inc in zip(bars, incremental):
        if inc > 0:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'+{inc:.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax2.set_xlabel('Trial Number (0=Baseline)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Incremental Improvement (%)', fontsize=13, fontweight='bold')
    ax2.set_title('Per-Trial Incremental Improvement', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xticks(trials)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(y=0, color='black', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig('result/Chart5_Learning_Curve.png', dpi=300, bbox_inches='tight')
    print("[OK] Generated: Chart5_Learning_Curve.png")
    plt.close()


def plot_comprehensive_dashboard():
    """Plot comprehensive dashboard"""
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Data preparation
    trials = list(range(0, 11))
    success_rates = [40.3, 47.8, 55.2, 63.4, 70.9, 79.1, 85.8, 88.1, 90.3, 91.8, 93.3]
    
    # 1. Main trend plot (occupies top-left large area)
    ax1 = fig.add_subplot(gs[0:2, 0:2])
    ax1.plot(trials, success_rates, marker='o', linewidth=4, 
             markersize=12, color='#2E86AB', label='Reflexion')
    ax1.axhline(y=success_rates[0], color='red', linestyle='--', 
                linewidth=2, alpha=0.6, label=f'Baseline: {success_rates[0]}%')
    ax1.fill_between(trials, success_rates[0], success_rates, alpha=0.3, color='#2E86AB')
    ax1.set_xlabel('Trial Number', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Main Learning Curve', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([30, 100])
    
    # 2. Method comparison (top-right)
    ax2 = fig.add_subplot(gs[0, 2])
    methods_short = ["Baseline", "ReAct", "CoT", "R-1", "R-5", "R-10"]
    rates_short = [40.3, 45.2, 42.8, 47.8, 79.1, 93.3]
    colors = ['#E63946', '#F77F00', '#FCBF49', '#06D6A0', '#118AB2', '#073B4C']
    ax2.barh(methods_short, rates_short, color=colors, alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Success Rate (%)', fontsize=10, fontweight='bold')
    ax2.set_title('Method Comparison', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 3. Incremental improvement (middle-right)
    ax3 = fig.add_subplot(gs[1, 2])
    incremental = [success_rates[i] - success_rates[i-1] for i in range(1, len(success_rates))]
    ax3.bar(range(1, 11), incremental, color='#06D6A0', alpha=0.8, edgecolor='black')
    ax3.set_xlabel('Trial', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Increment (%)', fontsize=10, fontweight='bold')
    ax3.set_title('Per-Trial Improvement', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Key metrics display (bottom)
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
    
    metrics = [
        ("Baseline Success", f"{success_rates[0]:.1f}%", '#E63946'),
        ("Final Success", f"{success_rates[-1]:.1f}%", '#06D6A0'),
        ("Absolute Gain", f"+{success_rates[-1] - success_rates[0]:.1f}%", '#118AB2'),
        ("Relative Gain", f"+{((success_rates[-1] - success_rates[0]) / success_rates[0] * 100):.1f}%", '#8338EC'),
        ("Average Success", f"{np.mean(success_rates[1:]):.1f}%", '#F77F00'),
        ("Max Single Gain", f"+{max(incremental):.1f}%", '#06D6A0'),
    ]
    
    y_pos = 0.8
    for i, (label, value, color) in enumerate(metrics):
        x_pos = (i % 3) / 3 + 0.1
        y = y_pos if i < 3 else 0.3
        
        # Draw metric boxes
        bbox = dict(boxstyle='round,pad=0.8', facecolor=color, alpha=0.3, edgecolor=color, linewidth=2)
        ax4.text(x_pos, y, f"{label}\n{value}", 
                fontsize=14, fontweight='bold', ha='center', va='center',
                bbox=bbox, transform=ax4.transAxes)
    
    fig.suptitle('Reflexion Experiment Results - Comprehensive Dashboard', fontsize=18, fontweight='bold', y=0.98)
    
    plt.savefig('result/Chart6_Comprehensive_Dashboard.png', dpi=300, bbox_inches='tight')
    print("[OK] Generated: Chart6_Comprehensive_Dashboard.png")
    plt.close()


def main():
    """Main function"""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "Reflexion Experiment Visualization")
    print("=" * 80 + "\n")
    
    print("Generating professional charts...\n")
    
    try:
        # Generate all charts
        plot_success_rate_trend()
        plot_method_comparison()
        plot_task_type_breakdown()
        plot_improvement_heatmap()
        plot_learning_curve()
        plot_comprehensive_dashboard()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] All charts generated successfully!")
        print("=" * 80)
        print("\nGenerated chart files:")
        print("  1. Chart1_Success_Rate_Trend.png      - Success rate trend over trials")
        print("  2. Chart2_Method_Comparison.png        - Performance comparison of methods")
        print("  3. Chart3_Task_Type_Analysis.png       - Detailed analysis by task type")
        print("  4. Chart4_Performance_Improvement.png  - Relative & absolute improvements")
        print("  5. Chart5_Learning_Curve.png           - Learning curve with increments")
        print("  6. Chart6_Comprehensive_Dashboard.png  - Comprehensive metrics dashboard")
        print("\nAll charts saved in the 'result' folder, ready for your report!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error generating charts: {e}")
        print("Please ensure matplotlib is installed: pip install matplotlib")


if __name__ == "__main__":
    main()

