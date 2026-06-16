#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存性能分析数据可视化工具
基于实验报告中的数据生成多维度性能图表
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib import rcParams

# 配置中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
rcParams['figure.dpi'] = 120

# ==================== 数据定义 ====================

# 3.1 基准配置性能测试数据
baseline_data = {
    'programs': ['mcf', 'vortex', 'bzip2'],
    'accesses': [88761256, 34491160, 26272583],
    'misses': [38294168, 893209, 8942720],
    'miss_rate': [0.4314, 0.0259, 0.3404]
}

# 3.2 块大小影响实验数据
block_size_data = {
    'mcf': {
        'block_sizes': [64, 128, 256, 512],
        'accesses': [88761256, 88761256, 88761256, 88761256],
        'misses': [22599744, 14794549, 8841978, 6813640],
        'miss_rate': [0.2546, 0.1667, 0.0996, 0.0768]
    },
    'vortex': {
        'block_sizes': [64, 128, 256, 512],
        'accesses': [34491160, 34491160, 34491160, 34491160],
        'misses': [528875, 350525, 303986, 384982],
        'miss_rate': [0.0153, 0.0102, 0.0088, 0.0112]
    },
    'bzip2': {
        'block_sizes': [64, 128, 256, 512],
        'accesses': [26272583, 26272583, 26272583, 26272583],
        'misses': [6251150, 5987022, 6064279, 5952276],
        'miss_rate': [0.2379, 0.2278, 0.2308, 0.2265]
    }
}

# 3.3 缓存容量扫描实验数据
capacity_data = {
    'mcf': {
        'capacities': [64, 128, 256, 512, 1024],
        'accesses': [88761256] * 5,
        'misses': [58125546, 47513014, 38294168, 22599744, 15444558],
        'miss_rate': [0.6548, 0.5353, 0.4314, 0.2546, 0.1740]
    },
    'vortex': {
        'capacities': [64, 128, 256, 512, 1024],
        'accesses': [34491160] * 5,
        'misses': [8488977, 2736993, 893209, 528875, 423992],
        'miss_rate': [0.2462, 0.0794, 0.0259, 0.0153, 0.0123]
    },
    'bzip2': {
        'capacities': [64, 128, 256, 512, 1024],
        'accesses': [26272583] * 5,
        'misses': [12911805, 11286235, 8942720, 6251150, 3981831],
        'miss_rate': [0.4915, 0.4296, 0.3404, 0.2379, 0.1516]
    }
}

# 3.4 相联度变化实验数据
associativity_data = {
    'mcf': {
        'ways': [2, 4, 8, 16, 64],
        'accesses': [88761256] * 5,
        'misses': [22904664, 22536018, 22599744, 22731928, 22805833],
        'miss_rate': [0.2581, 0.2539, 0.2546, 0.2561, 0.2569]
    },
    'vortex': {
        'ways': [2, 4, 8, 16, 64],
        'accesses': [34491160] * 5,
        'misses': [978465, 584880, 528875, 517610, 503134],
        'miss_rate': [0.0284, 0.0170, 0.0153, 0.0150, 0.0146]
    },
    'bzip2': {
        'ways': [2, 4, 8, 16, 64],
        'accesses': [26272583] * 5,
        'misses': [6658769, 6425946, 6251150, 6189011, 6153684],
        'miss_rate': [0.2534, 0.2445, 0.2379, 0.2355, 0.2342]
    }
}

# 3.6 Victim Cache 性能数据
victim_cache_data = {
    'programs': ['mcf', 'vortex', 'bzip2'],
    'standard_miss_rate': [0.2112, 0.0161, 0.0151],
    'vc_miss_rate': [0.2479, 0.0204, 0.0220],
    'vc_hit_count': [358642, 2118425, 742136],
    'l1d_original_miss': [68504342, 8145688, 15851500],
    'vc_hit_rate': [0.52, 26.00, 4.68]
}


# ==================== 可视化函数 ====================

def plot_baseline_comparison():
    """绘制基准配置性能对比图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    programs = baseline_data['programs']
    x = np.arange(len(programs))
    width = 0.6
    
    # 子图1: L2缺失率对比
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    bars = ax1.bar(x, [r * 100 for r in baseline_data['miss_rate']], 
                   width, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    ax1.set_xlabel('基准程序', fontsize=12, fontweight='bold')
    ax1.set_ylabel('L2 缺失率 (%)', fontsize=12, fontweight='bold')
    ax1.set_title('3.1 基准配置性能测试 - L2缓存缺失率对比\n(256KB/8-way/64B)', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(programs, fontsize=11)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 在柱状图上添加数值标签
    for i, (bar, val) in enumerate(zip(bars, baseline_data['miss_rate'])):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val*100:.2f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 子图2: L2访问次数与缺失次数对比
    x_pos = np.arange(len(programs))
    width = 0.35
    
    accesses_M = [a / 1e6 for a in baseline_data['accesses']]
    misses_M = [m / 1e6 for m in baseline_data['misses']]
    
    bars1 = ax2.bar(x_pos - width/2, accesses_M, width, 
                    label='L2总访问', color='#3498db', alpha=0.8, edgecolor='black')
    bars2 = ax2.bar(x_pos + width/2, misses_M, width, 
                    label='L2缺失', color='#e74c3c', alpha=0.8, edgecolor='black')
    
    ax2.set_xlabel('基准程序', fontsize=12, fontweight='bold')
    ax2.set_ylabel('访问/缺失次数 (百万次)', fontsize=12, fontweight='bold')
    ax2.set_title('L2缓存访问与缺失次数对比', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(programs, fontsize=11)
    ax2.legend(fontsize=10, loc='upper left')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}M',
                    ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('图1_基准配置性能对比.png', bbox_inches='tight')
    print("[OK] 已生成: 图1_基准配置性能对比.png")


def plot_block_size_impact():
    """绘制块大小影响分析图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 子图1: 缺失率随块大小变化
    for prog in ['mcf', 'vortex', 'bzip2']:
        data = block_size_data[prog]
        ax1.plot(data['block_sizes'], [r * 100 for r in data['miss_rate']], 
                marker='o', linewidth=2.5, markersize=8, label=prog, alpha=0.8)
    
    ax1.set_xlabel('块大小 (Bytes)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('L2 缺失率 (%)', fontsize=12, fontweight='bold')
    ax1.set_title('3.2 块大小对缓存性能的影响\n(固定: 512KB/8-way/LRU)', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.set_xscale('log', base=2)
    ax1.set_xticks([64, 128, 256, 512])
    ax1.set_xticklabels(['64', '128', '256', '512'])
    ax1.legend(fontsize=11, loc='best')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # 子图2: 缺失次数随块大小变化
    x = np.arange(4)
    width = 0.25
    
    for i, prog in enumerate(['mcf', 'vortex', 'bzip2']):
        data = block_size_data[prog]
        misses_M = [m / 1e6 for m in data['misses']]
        ax2.bar(x + i * width, misses_M, width, label=prog, alpha=0.8, edgecolor='black')
    
    ax2.set_xlabel('块大小 (Bytes)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L2 缺失次数 (百万次)', fontsize=12, fontweight='bold')
    ax2.set_title('块大小对缺失次数的影响', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xticks(x + width)
    ax2.set_xticklabels(['64', '128', '256', '512'])
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('图2_块大小影响分析.png', bbox_inches='tight')
    print("[OK] 已生成: 图2_块大小影响分析.png")


def plot_capacity_impact():
    """绘制缓存容量影响分析图"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = {'mcf': '#e74c3c', 'vortex': '#3498db', 'bzip2': '#2ecc71'}
    
    # 子图1: 缺失率随容量变化
    for prog in ['mcf', 'vortex', 'bzip2']:
        data = capacity_data[prog]
        ax1.plot(data['capacities'], [r * 100 for r in data['miss_rate']], 
                marker='o', linewidth=2.5, markersize=8, label=prog, 
                color=colors[prog], alpha=0.8)
    
    ax1.set_xlabel('缓存容量 (KB)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('L2 缺失率 (%)', fontsize=12, fontweight='bold')
    ax1.set_title('3.3 缓存容量对缺失率的影响\n(固定: 8-way/64B/LRU)', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.set_xscale('log', base=2)
    ax1.set_xticks([64, 128, 256, 512, 1024])
    ax1.set_xticklabels(['64', '128', '256', '512', '1024'])
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # 子图2: 缺失次数随容量变化
    for prog in ['mcf', 'vortex', 'bzip2']:
        data = capacity_data[prog]
        misses_M = [m / 1e6 for m in data['misses']]
        ax2.plot(data['capacities'], misses_M, 
                marker='s', linewidth=2.5, markersize=8, label=prog, 
                color=colors[prog], alpha=0.8)
    
    ax2.set_xlabel('缓存容量 (KB)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('L2 缺失次数 (百万次)', fontsize=12, fontweight='bold')
    ax2.set_title('缓存容量对缺失次数的影响', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xscale('log', base=2)
    ax2.set_xticks([64, 128, 256, 512, 1024])
    ax2.set_xticklabels(['64', '128', '256', '512', '1024'])
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # 子图3: 各程序容量敏感度对比（降幅百分比）
    programs = ['mcf', 'vortex', 'bzip2']
    capacity_reduction = []
    
    for prog in programs:
        data = capacity_data[prog]
        reduction = ((data['miss_rate'][0] - data['miss_rate'][-1]) / 
                    data['miss_rate'][0] * 100)
        capacity_reduction.append(reduction)
    
    bars = ax3.bar(programs, capacity_reduction, color=[colors[p] for p in programs], 
                   alpha=0.8, edgecolor='black', linewidth=1.2, width=0.6)
    ax3.set_ylabel('缺失率降幅 (%)', fontsize=12, fontweight='bold')
    ax3.set_title('容量从64KB扩展至1024KB的性能提升', 
                  fontsize=13, fontweight='bold', pad=15)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, val in zip(bars, capacity_reduction):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 子图4: 不同容量下的缺失率分布（热力图）
    x_pos = np.arange(5)
    width = 0.25
    
    for i, prog in enumerate(['mcf', 'vortex', 'bzip2']):
        data = capacity_data[prog]
        ax4.bar(x_pos + i * width, [r * 100 for r in data['miss_rate']], 
               width, label=prog, color=colors[prog], alpha=0.8, edgecolor='black')
    
    ax4.set_xlabel('缓存容量 (KB)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('L2 缺失率 (%)', fontsize=12, fontweight='bold')
    ax4.set_title('不同容量下的缺失率分布对比', fontsize=13, fontweight='bold', pad=15)
    ax4.set_xticks(x_pos + width)
    ax4.set_xticklabels(['64', '128', '256', '512', '1024'])
    ax4.legend(fontsize=10)
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('图3_缓存容量影响分析.png', bbox_inches='tight')
    print("[OK] 已生成: 图3_缓存容量影响分析.png")


def plot_associativity_impact():
    """绘制相联度影响分析图"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = {'mcf': '#e74c3c', 'vortex': '#3498db', 'bzip2': '#2ecc71'}
    
    # 子图1: 缺失率随相联度变化
    for prog in ['mcf', 'vortex', 'bzip2']:
        data = associativity_data[prog]
        ax1.plot(data['ways'], [r * 100 for r in data['miss_rate']], 
                marker='o', linewidth=2.5, markersize=8, label=prog, 
                color=colors[prog], alpha=0.8)
    
    ax1.set_xlabel('相联度 (路)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('L2 缺失率 (%)', fontsize=12, fontweight='bold')
    ax1.set_title('3.4 相联度对缓存性能的影响\n(固定: 512KB/64B/LRU)', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.set_xscale('log', base=2)
    ax1.set_xticks([2, 4, 8, 16, 64])
    ax1.set_xticklabels(['2', '4', '8', '16', '64'])
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # 子图2: 性能改善幅度对比
    programs = ['mcf', 'vortex', 'bzip2']
    improvements = []
    
    for prog in programs:
        data = associativity_data[prog]
        improvement = ((data['miss_rate'][0] - data['miss_rate'][-1]) / 
                      data['miss_rate'][0] * 100)
        improvements.append(improvement)
    
    bars = ax2.bar(programs, improvements, color=[colors[p] for p in programs], 
                   alpha=0.8, edgecolor='black', linewidth=1.2, width=0.6)
    ax2.set_ylabel('缺失率改善幅度 (%)', fontsize=12, fontweight='bold')
    ax2.set_title('相联度从2-way提升至64-way的性能改善', 
                  fontsize=13, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, val in zip(bars, improvements):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 子图3: vortex 详细分析（最敏感）
    data = associativity_data['vortex']
    ax3.plot(data['ways'], [r * 100 for r in data['miss_rate']], 
            marker='o', linewidth=3, markersize=10, color='#3498db', 
            alpha=0.8, label='vortex')
    ax3.fill_between(data['ways'], [r * 100 for r in data['miss_rate']], 
                     alpha=0.2, color='#3498db')
    
    ax3.set_xlabel('相联度 (路)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('L2 缺失率 (%)', fontsize=12, fontweight='bold')
    ax3.set_title('vortex程序相联度敏感性分析\n(冲突缺失显著)', 
                  fontsize=13, fontweight='bold', pad=15)
    ax3.set_xscale('log', base=2)
    ax3.set_xticks([2, 4, 8, 16, 64])
    ax3.set_xticklabels(['2-way', '4-way', '8-way', '16-way', '64-way'])
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for x, y in zip(data['ways'], data['miss_rate']):
        ax3.annotate(f'{y*100:.2f}%', (x, y*100), 
                    textcoords="offset points", xytext=(0,8), 
                    ha='center', fontsize=9, fontweight='bold')
    
    # 子图4: 缺失次数对比
    x_pos = np.arange(5)
    width = 0.25
    
    for i, prog in enumerate(['mcf', 'vortex', 'bzip2']):
        data = associativity_data[prog]
        misses_M = [m / 1e6 for m in data['misses']]
        ax4.bar(x_pos + i * width, misses_M, width, label=prog, 
               color=colors[prog], alpha=0.8, edgecolor='black')
    
    ax4.set_xlabel('相联度 (路)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('L2 缺失次数 (百万次)', fontsize=12, fontweight='bold')
    ax4.set_title('不同相联度下的缺失次数对比', fontsize=13, fontweight='bold', pad=15)
    ax4.set_xticks(x_pos + width)
    ax4.set_xticklabels(['2', '4', '8', '16', '64'])
    ax4.legend(fontsize=10)
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('图4_相联度影响分析.png', bbox_inches='tight')
    print("[OK] 已生成: 图4_相联度影响分析.png")


def plot_victim_cache_analysis():
    """绘制 Victim Cache 性能分析图"""
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    
    programs = victim_cache_data['programs']
    x = np.arange(len(programs))
    width = 0.35
    
    # 子图1: VC 命中率对比
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    bars = ax1.bar(x, victim_cache_data['vc_hit_rate'], 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=1.2, width=0.6)
    
    ax1.set_ylabel('VC 命中率 (%)', fontsize=12, fontweight='bold')
    ax1.set_title('3.6 Victim Cache 命中率对比\n(4块全相联配置)', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(programs, fontsize=11)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, val in zip(bars, victim_cache_data['vc_hit_rate']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{val:.2f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 子图2: 有效缺失率变化对比
    standard_rates = [r * 100 for r in victim_cache_data['standard_miss_rate']]
    vc_rates = [r * 100 for r in victim_cache_data['vc_miss_rate']]
    
    bars1 = ax2.bar(x - width/2, standard_rates, width, 
                    label='无VC', color='#95a5a6', alpha=0.8, edgecolor='black')
    bars2 = ax2.bar(x + width/2, vc_rates, width, 
                    label='启用VC(4块)', color='#e67e22', alpha=0.8, edgecolor='black')
    
    ax2.set_ylabel('有效L1D缺失率 (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Victim Cache 对有效缺失率的影响', 
                  fontsize=13, fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(programs, fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}%',
                    ha='center', va='bottom', fontsize=9)
    
    # 子图3: VC 命中次数与L1D原始缺失对比
    x_pos = np.arange(len(programs))
    width_main = 0.6
    
    # 主柱：L1D原始缺失
    original_misses_M = [m / 1e6 for m in victim_cache_data['l1d_original_miss']]
    bars_original = ax3.bar(x_pos, original_misses_M, width_main, 
                           label='L1D原始缺失', color='#95a5a6', 
                           alpha=0.6, edgecolor='black', linewidth=1.2)
    
    # 叠加柱：VC命中部分
    vc_hits_M = [h / 1e6 for h in victim_cache_data['vc_hit_count']]
    bars_vc = ax3.bar(x_pos, vc_hits_M, width_main, 
                     label='VC命中(挽回部分)', color='#27ae60', 
                     alpha=0.9, edgecolor='black', linewidth=1.2)
    
    ax3.set_xlabel('基准程序', fontsize=12, fontweight='bold')
    ax3.set_ylabel('次数 (百万次)', fontsize=12, fontweight='bold')
    ax3.set_title('Victim Cache 命中次数与L1D原始缺失对比', 
                  fontsize=13, fontweight='bold', pad=15)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(programs, fontsize=11)
    ax3.legend(fontsize=11, loc='upper left')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for i, (orig, vc) in enumerate(zip(original_misses_M, vc_hits_M)):
        # 原始缺失标签
        ax3.text(i, orig + 1, f'{orig:.1f}M',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
        # VC命中标签
        ax3.text(i, vc / 2, f'{vc:.1f}M\n({victim_cache_data["vc_hit_rate"][i]:.1f}%)',
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    plt.savefig('图5_Victim_Cache性能分析.png', bbox_inches='tight')
    print("[OK] 已生成: 图5_Victim_Cache性能分析.png")


def plot_comprehensive_comparison():
    """绘制综合性能对比雷达图"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12), 
                                                  subplot_kw=dict(projection='polar'))
    
    # 准备雷达图数据
    categories = ['容量敏感度', '相联度敏感度', '块大小敏感度', '基准失效率', 'VC收益']
    
    # 归一化数据 (0-100分制)
    def normalize_score(value, max_val):
        return (value / max_val) * 100 if max_val > 0 else 0
    
    # mcf 数据
    mcf_capacity_sens = ((0.6548 - 0.1740) / 0.6548) * 100  # 73.4
    mcf_assoc_sens = ((0.2581 - 0.2569) / 0.2581) * 100  # 0.5
    mcf_block_sens = ((0.2546 - 0.0768) / 0.2546) * 100  # 69.8
    mcf_baseline = (1 - 0.4314) * 100  # 失效率越低越好，转为得分
    mcf_vc = 0.52 * 5  # VC命中率较低，放大显示
    
    mcf_scores = [mcf_capacity_sens, mcf_assoc_sens, mcf_block_sens, mcf_baseline, mcf_vc]
    
    # vortex 数据
    vortex_capacity_sens = ((0.2462 - 0.0123) / 0.2462) * 100  # 95.0
    vortex_assoc_sens = ((0.0284 - 0.0146) / 0.0284) * 100  # 48.6
    vortex_block_sens = ((0.0153 - 0.0088) / 0.0153) * 100  # 42.5
    vortex_baseline = (1 - 0.0259) * 100
    vortex_vc = 26.00 * 2  # VC命中率高
    
    vortex_scores = [vortex_capacity_sens, vortex_assoc_sens, vortex_block_sens, 
                    vortex_baseline, vortex_vc]
    
    # bzip2 数据
    bzip2_capacity_sens = ((0.4915 - 0.1516) / 0.4915) * 100  # 69.2
    bzip2_assoc_sens = ((0.2534 - 0.2342) / 0.2534) * 100  # 7.6
    bzip2_block_sens = ((0.2379 - 0.2265) / 0.2379) * 100  # 4.8
    bzip2_baseline = (1 - 0.3404) * 100
    bzip2_vc = 4.68 * 10
    
    bzip2_scores = [bzip2_capacity_sens, bzip2_assoc_sens, bzip2_block_sens, 
                   bzip2_baseline, bzip2_vc]
    
    # 绘制雷达图
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合图形
    
    def plot_radar(ax, scores, title, color):
        scores_plot = scores + scores[:1]
        ax.plot(angles, scores_plot, 'o-', linewidth=2.5, color=color, label=title, markersize=8)
        ax.fill(angles, scores_plot, alpha=0.25, color=color)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_title(f'{title} 性能特征分析', fontsize=12, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
    
    plot_radar(ax1, mcf_scores, 'mcf', '#e74c3c')
    plot_radar(ax2, vortex_scores, 'vortex', '#3498db')
    plot_radar(ax3, bzip2_scores, 'bzip2', '#2ecc71')
    
    # 第四个子图：三者对比
    ax4.plot(angles, mcf_scores + mcf_scores[:1], 'o-', linewidth=2, 
            color='#e74c3c', label='mcf', markersize=6)
    ax4.plot(angles, vortex_scores + vortex_scores[:1], 's-', linewidth=2, 
            color='#3498db', label='vortex', markersize=6)
    ax4.plot(angles, bzip2_scores + bzip2_scores[:1], '^-', linewidth=2, 
            color='#2ecc71', label='bzip2', markersize=6)
    
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories, fontsize=10)
    ax4.set_ylim(0, 100)
    ax4.set_title('三个基准程序综合性能对比', fontsize=13, fontweight='bold', pad=20)
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper right', fontsize=10)
    
    plt.savefig('图6_综合性能雷达图.png', bbox_inches='tight')
    print("[OK] 已生成: 图6_综合性能雷达图.png")


def generate_summary_report():
    """生成数据分析摘要报告"""
    report = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                     缓存性能实验数据可视化分析报告                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

【1】基准配置性能测试 (L2: 256KB/8-way/64B)
    ├─ mcf     : 失效率 43.14% (高内存需求，容量缺失为主)
    ├─ vortex  : 失效率  2.59% (优异的局部性)
    └─ bzip2   : 失效率 34.04% (中等容量压力)

【2】缓存容量影响分析 (64KB → 1024KB)
    ├─ mcf     : 失效率降低 73.4% (容量敏感度极高)
    ├─ vortex  : 失效率降低 95.0% (小工作集，容量充足时性能优异)
    └─ bzip2   : 失效率降低 69.2% (中等容量敏感度)
    
    设计启示：mcf 和 bzip2 受益于大容量缓存

【3】相联度影响分析 (2-way → 64-way)
    ├─ mcf     : 性能改善  0.5% (冲突缺失占比极低)
    ├─ vortex  : 性能改善 48.6% (冲突缺失显著，提升相联度收益大)
    └─ bzip2   : 性能改善  7.6% (轻度冲突缺失)
    
    设计启示：vortex 类负载适合高相联度设计

【4】块大小影响分析 (64B → 512B)
    ├─ mcf     : 失效率降低 69.8% (良好的空间局部性)
    ├─ vortex  : 最佳块大小 256B (512B引入缓存污染)
    └─ bzip2   : 改善幅度  4.8% (块大小不敏感)
    
    设计启示：块大小需根据程序访存模式优化

【5】Victim Cache 性能分析 (4块全相联)
    ├─ mcf     : VC命中率  0.52%, 有效失效率上升 17.4%
    ├─ vortex  : VC命中率 26.00%, 有效失效率上升 26.7%
    └─ bzip2   : VC命中率  4.68%, 有效失效率上升 45.7%
    
    关键发现：虽然 vortex 的 VC 命中率达 26%，但由于 VC 机制引入的
             额外开销，反而导致整体有效失效率上升

【综合结论】
    - 容量扩展对所有基准程序都有显著性能提升
    - 相联度提升主要改善冲突缺失（vortex 受益最大）
    - 块大小优化需匹配程序的空间局部性特征
    - Victim Cache 在本实验配置下未能带来性能收益
    
═══════════════════════════════════════════════════════════════════════════
"""
    print(report)
    
    with open('数据分析报告摘要.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("[OK] 已生成: 数据分析报告摘要.txt")


# ==================== 主程序 ====================

def main():
    """主函数：执行所有可视化任务"""
    print("\n" + "="*70)
    print(" 缓存性能实验数据可视化分析工具 ".center(70, "="))
    print("="*70 + "\n")
    
    print("开始生成可视化图表...\n")
    
    try:
        plot_baseline_comparison()
        plot_block_size_impact()
        plot_capacity_impact()
        plot_associativity_impact()
        plot_victim_cache_analysis()
        plot_comprehensive_comparison()
        generate_summary_report()
        
        print("\n" + "="*70)
        print(" 所有可视化图表生成完成！ ".center(70, "="))
        print("="*70)
        print("\n生成的文件列表：")
        print("  [图表] 图1_基准配置性能对比.png")
        print("  [图表] 图2_块大小影响分析.png")
        print("  [图表] 图3_缓存容量影响分析.png")
        print("  [图表] 图4_相联度影响分析.png")
        print("  [图表] 图5_Victim_Cache性能分析.png")
        print("  [图表] 图6_综合性能雷达图.png")
        print("  [报告] 数据分析报告摘要.txt\n")
        
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

