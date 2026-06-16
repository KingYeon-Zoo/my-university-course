#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RISC-V CPU 性能分析工具
分析comprehensive_test.asm的执行性能，统计CPI、冒险次数等
"""

import re
from collections import defaultdict


class PerformanceAnalyzer:
    def __init__(self):
        self.instructions = []
        self.total_cycles = 0
        self.total_instructions = 0
        
        # 统计数据
        self.stats = {
            'load_use_hazards': 0,      # Load-Use冒险次数
            'branch_count': 0,           # 分支指令总数
            'branch_taken': 0,           # 实际跳转次数
            'branch_pred_fail': 0,       # 预测失败次数（估算）
            'jump_count': 0,             # 跳转指令次数
            'nop_bubbles': 0,            # 插入的气泡数
            'forwarding_count': 0,       # 数据前递次数（估算）
        }
        
        # 指令分类
        self.instr_types = {
            'R-type': 0,
            'I-type': 0,
            'Load': 0,
            'Store': 0,
            'Branch': 0,
            'Jump': 0,
            'LUI/AUIPC': 0,
            'CSR': 0
        }
    
    def parse_asm_file(self, filename):
        """解析汇编文件"""
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('//'):
                continue
            
            # 提取指令部分（去掉注释）
            if '//' in line:
                instr = line.split('//')[0].strip()
            else:
                instr = line
            
            if instr:
                self.instructions.append(instr)
                self.classify_instruction(instr)
        
        self.total_instructions = len(self.instructions)
        print(f"[INFO] 解析完成，共 {self.total_instructions} 条指令")
    
    def classify_instruction(self, instr):
        """分类指令"""
        instr_upper = instr.upper()
        
        if any(op in instr_upper for op in ['ADD ', 'SUB ', 'AND ', 'OR ', 'XOR ', 
                                              'SLL ', 'SRL ', 'SRA ', 'SLT ', 'SLTU',
                                              'MUL ', 'DIV ', 'REM ']):
            if any(op in instr_upper for op in ['ADDI', 'ANDI', 'ORI', 'XORI',
                                                  'SLLI', 'SRLI', 'SRAI', 'SLTI']):
                self.instr_types['I-type'] += 1
            else:
                self.instr_types['R-type'] += 1
        
        elif any(op in instr_upper for op in ['LW ', 'LH ', 'LB ', 'LHU', 'LBU']):
            self.instr_types['Load'] += 1
            self.stats['load_use_hazards'] += 1  # 假设每个Load后都可能有冒险
        
        elif any(op in instr_upper for op in ['SW ', 'SH ', 'SB ']):
            self.instr_types['Store'] += 1
        
        elif any(op in instr_upper for op in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']):
            self.instr_types['Branch'] += 1
            self.stats['branch_count'] += 1
        
        elif any(op in instr_upper for op in ['JAL', 'JALR']):
            self.instr_types['Jump'] += 1
            self.stats['jump_count'] += 1
        
        elif any(op in instr_upper for op in ['LUI', 'AUIPC']):
            self.instr_types['LUI/AUIPC'] += 1
        
        elif any(op in instr_upper for op in ['CSR']):
            self.instr_types['CSR'] += 1
    
    def estimate_performance(self):
        """估算性能指标"""
        # 基础周期: 指令数 + 流水线填充5周期
        base_cycles = self.total_instructions + 5
        
        # Load-Use冒险: 保守估计50%的Load指令会导致冒险，每次停顿1周期
        load_hazard_cycles = int(self.instr_types['Load'] * 0.5)
        
        # 分支预测: 
        # - 循环首次: 预测失败，损失2周期
        # - 循环内部: 90%预测正确，10%失败
        # - 循环末尾: 退出时预测失败，损失2周期
        # 保守估计: 20%的分支预测失败，每次损失2周期
        branch_cycles = int(self.stats['branch_count'] * 0.2 * 2)
        
        # Jump指令: 每次损失2周期（冲刷流水线）
        jump_cycles = self.stats['jump_count'] * 2
        
        # 总周期数
        self.total_cycles = base_cycles + load_hazard_cycles + branch_cycles + jump_cycles
        
        self.stats['load_use_hazards'] = load_hazard_cycles
        self.stats['branch_pred_fail'] = int(self.stats['branch_count'] * 0.2)
        self.stats['nop_bubbles'] = load_hazard_cycles + branch_cycles + jump_cycles
        
        # 计算CPI
        cpi = self.total_cycles / self.total_instructions if self.total_instructions > 0 else 0
        
        return cpi
    
    def generate_report(self):
        """生成性能分析报告"""
        cpi = self.estimate_performance()
        
        report = []
        report.append("=" * 80)
        report.append(" RISC-V CPU 性能分析报告")
        report.append("=" * 80)
        report.append("")
        
        report.append("【指令统计】")
        report.append(f"  总指令数: {self.total_instructions} 条")
        report.append("")
        for itype, count in sorted(self.instr_types.items()):
            if count > 0:
                percentage = (count / self.total_instructions) * 100
                report.append(f"  {itype:12s}: {count:3d} 条  ({percentage:5.1f}%)")
        report.append("")
        
        report.append("【性能指标】")
        report.append(f"  总周期数: {self.total_cycles} 周期")
        report.append(f"  CPI (每指令周期数): {cpi:.2f}")
        report.append(f"  IPC (每周期指令数): {1/cpi:.2f}")
        report.append("")
        
        report.append("【周期详细分析】")
        base = self.total_instructions + 5
        report.append(f"  基础周期: {base}")
        report.append(f"    - 指令执行: {self.total_instructions} 周期")
        report.append(f"    - 流水线填充: 5 周期")
        report.append(f"  额外周期: {self.total_cycles - base}")
        report.append(f"    - Load-Use冒险停顿: {self.stats['load_use_hazards']} 周期")
        report.append(f"    - 分支预测失败: {self.stats['branch_pred_fail']} 次 × 2周期 = {self.stats['branch_pred_fail']*2} 周期")
        report.append(f"    - Jump指令冲刷: {self.stats['jump_count']} 次 × 2周期 = {self.stats['jump_count']*2} 周期")
        report.append("")
        
        report.append("【冒险与优化】")
        report.append(f"  分支指令数: {self.stats['branch_count']} 条")
        report.append(f"  估算预测准确率: 80%")
        report.append(f"  估算预测失败: {self.stats['branch_pred_fail']} 次")
        report.append(f"  Load指令数: {self.instr_types['Load']} 条")
        report.append(f"  估算Load-Use冒险: {self.stats['load_use_hazards']} 次")
        report.append(f"  跳转指令数: {self.stats['jump_count']} 条")
        report.append("")
        
        report.append("【性能对比】")
        ideal_cpi = 1.0
        no_forward_cpi = cpi + 0.3  # 假设无前递会增加30%周期
        no_prediction_cpi = cpi + 0.4  # 假设无分支预测会增加40%周期
        
        report.append(f"  理想CPI (无冒险): {ideal_cpi:.2f}")
        report.append(f"  实际CPI (有优化): {cpi:.2f}")
        report.append(f"  无数据前递CPI (估算): {no_forward_cpi:.2f}")
        report.append(f"  无分支预测CPI (估算): {no_prediction_cpi:.2f}")
        report.append("")
        
        improvement_forward = ((no_forward_cpi - cpi) / no_forward_cpi) * 100
        improvement_branch = ((no_prediction_cpi - cpi) / no_prediction_cpi) * 100
        
        report.append(f"  数据前递优化效果: {improvement_forward:.1f}%")
        report.append(f"  分支预测优化效果: {improvement_branch:.1f}%")
        report.append("")
        
        report.append("=" * 80)
        report.append(" 分析完成")
        report.append("=" * 80)
        
        return '\n'.join(report)
    
    def generate_visualization(self):
        """生成可视化数据"""
        viz = []
        viz.append("\n" + "=" * 80)
        viz.append(" 性能可视化")
        viz.append("=" * 80)
        viz.append("")
        
        # 指令类型分布柱状图
        viz.append("【指令类型分布】")
        max_count = max(self.instr_types.values()) if self.instr_types.values() else 1
        for itype, count in sorted(self.instr_types.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                bar_len = int((count / max_count) * 50)
                bar = '█' * bar_len
                viz.append(f"  {itype:12s} [{count:3d}] {bar}")
        viz.append("")
        
        # CPI对比图
        cpi = self.total_cycles / self.total_instructions
        ideal = 1.0
        
        viz.append("【CPI对比】")
        viz.append(f"  理想CPI   [1.00] {'█' * 50}")
        actual_bar = int((cpi / 2.0) * 50)  # 假设最大CPI为2.0
        viz.append(f"  实际CPI   [{cpi:.2f}] {'█' * actual_bar}")
        viz.append("")
        
        # 周期分布饼图(文本版)
        viz.append("【周期分布】")
        base = self.total_instructions
        load_use = self.stats['load_use_hazards']
        branch = self.stats['branch_pred_fail'] * 2
        jump = self.stats['jump_count'] * 2
        fill = 5
        
        total = base + load_use + branch + jump + fill
        
        viz.append(f"  指令执行      : {base:3d} 周期 ({base/total*100:5.1f}%)")
        viz.append(f"  Load-Use停顿  : {load_use:3d} 周期 ({load_use/total*100:5.1f}%)")
        viz.append(f"  分支预测失败  : {branch:3d} 周期 ({branch/total*100:5.1f}%)")
        viz.append(f"  跳转冲刷      : {jump:3d} 周期 ({jump/total*100:5.1f}%)")
        viz.append(f"  流水线填充    : {fill:3d} 周期 ({fill/total*100:5.1f}%)")
        viz.append(f"  ────────────────────────────────")
        viz.append(f"  总计          : {total:3d} 周期")
        viz.append("")
        
        viz.append("=" * 80)
        
        return '\n'.join(viz)


def main():
    """主函数"""
    import os
    
    # 默认测试文件
    test_file = os.path.join(os.path.dirname(__file__), 'testbench', 'comprehensive_test.asm')
    
    if not os.path.exists(test_file):
        print(f"[ERROR] 测试文件不存在: {test_file}")
        return
    
    print(f"开始分析: {test_file}")
    print("")
    
    # 创建分析器
    analyzer = PerformanceAnalyzer()
    
    # 解析文件
    analyzer.parse_asm_file(test_file)
    
    # 生成报告
    report = analyzer.generate_report()
    print(report)
    
    # 生成可视化
    viz = analyzer.generate_visualization()
    print(viz)
    
    # 保存到文件
    output_file = os.path.join(os.path.dirname(__file__), 'performance_report.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
        f.write('\n')
        f.write(viz)
    
    print(f"\n[OK] 性能报告已保存到: {output_file}")


if __name__ == '__main__':
    main()

