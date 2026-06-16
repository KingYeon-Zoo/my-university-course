#!/usr/bin/env python3
"""
=============================================================================
文件名:     rv32i_transfer.py
描述:       RISC-V RV32I 汇编器 (指令转换器)
            将 RISC-V 汇编指令转换为机器码 (十六进制)

用法:       python rv32i_transfer.py <汇编文件>
示例:       python rv32i_transfer.py instr_r.dat

输入格式:   每行一条汇编指令
            ADD x1, x2, x3
            ADDI x1, x2, 100
            LW x1, 0(x2)
            // 开头的行为注释，会被保留

输出格式:   IM.dat 文件，每个字节一行 (大端序)
            // ADD x1, x2, x3
            00
            31
            80
            B3

支持的指令:
    R-Type:  ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
    M-Ext:   MUL, MULH, MULHSU, MULHU, DIV, DIVU, REM, REMU (乘除法扩展)
    I-Type:  ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
             LB, LH, LW, LBU, LHU, JALR
    S-Type:  SB, SH, SW
    B-Type:  BEQ, BNE, BLT, BGE, BLTU, BGEU
    U-Type:  LUI, AUIPC
    J-Type:  JAL
    CSR:     CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI
    System:  ECALL, EBREAK
=============================================================================
"""

import re

#=============================================================================
# 指令编码表
#=============================================================================
# 操作码 (Opcode) 映射
OPCODES = {
    # R-type: 寄存器-寄存器运算
    'ADD': 0x33, 'SUB': 0x33, 'SLL': 0x33, 'SLT': 0x33, 'SLTU': 0x33,
    'XOR': 0x33, 'SRL': 0x33, 'SRA': 0x33, 'OR': 0x33, 'AND': 0x33,
    
    # M 扩展: 乘除法指令 (也是 R-type，opcode 0x33)
    'MUL': 0x33, 'MULH': 0x33, 'MULHSU': 0x33, 'MULHU': 0x33,
    'DIV': 0x33, 'DIVU': 0x33, 'REM': 0x33, 'REMU': 0x33,
    
    # I-type: 立即数运算
    'ADDI': 0x13, 'SLTI': 0x13, 'SLTIU': 0x13, 'XORI': 0x13, 'ORI': 0x13, 'ANDI': 0x13,
    'SLLI': 0x13, 'SRLI': 0x13, 'SRAI': 0x13,
    
    # I-type: 加载指令
    'LB': 0x03, 'LH': 0x03, 'LW': 0x03, 'LBU': 0x03, 'LHU': 0x03,
    
    # I-type: 跳转/系统指令
    'JALR': 0x67, 'ECALL': 0x73, 'EBREAK': 0x73,
    
    # CSR 指令
    'CSRRW': 0x73, 'CSRRS': 0x73, 'CSRRC': 0x73,
    'CSRRWI': 0x73, 'CSRRSI': 0x73, 'CSRRCI': 0x73,
    
    # S-type: 存储指令
    'SB': 0x23, 'SH': 0x23, 'SW': 0x23,
    
    # B-type: 分支指令
    'BEQ': 0x63, 'BNE': 0x63, 'BLT': 0x63, 'BGE': 0x63, 'BLTU': 0x63, 'BGEU': 0x63,
    
    # U-type: 高位立即数
    'LUI': 0x37, 'AUIPC': 0x17,
    
    # J-type: 跳转指令
    'JAL': 0x6F
}

# funct3 字段映射 (决定具体操作)
FUNCT3 = {
    'ADD': 0, 'SUB': 0, 'ADDI': 0, 'SLL': 1, 'SLLI': 1, 'SLT': 2, 'SLTI': 2,
    'SLTU': 3, 'SLTIU': 3, 'XOR': 4, 'XORI': 4, 'SRL': 5, 'SRA': 5, 'SRLI': 5, 'SRAI': 5,
    'OR': 6, 'ORI': 6, 'AND': 7, 'ANDI': 7,
    # M 扩展: 乘除法指令的 funct3
    'MUL': 0, 'MULH': 1, 'MULHSU': 2, 'MULHU': 3,
    'DIV': 4, 'DIVU': 5, 'REM': 6, 'REMU': 7,
    'LB': 0, 'LH': 1, 'LW': 2, 'LBU': 4, 'LHU': 5,
    'SB': 0, 'SH': 1, 'SW': 2, 
    'BEQ': 0, 'BNE': 1, 'BLT': 4, 'BGE': 5, 'BLTU': 6, 'BGEU': 7,
    'JALR': 0, 'ECALL': 0, 'EBREAK': 0,
    # CSR 指令的 funct3
    'CSRRW': 1, 'CSRRS': 2, 'CSRRC': 3, 'CSRRWI': 5, 'CSRRSI': 6, 'CSRRCI': 7
}

# funct7 字段映射 (用于区分 ADD/SUB, SRL/SRA 等)
FUNCT7 = {
    'ADD': 0, 'SUB': 0x20, 'SLL': 0, 'SLT': 0, 'SLTU': 0, 'XOR': 0,
    'SRL': 0, 'SRA': 0x20, 'OR': 0, 'AND': 0, 'SLLI': 0, 'SRLI': 0, 'SRAI': 0x20,
    # M 扩展: 乘除法指令的 funct7 都是 0x01
    'MUL': 0x01, 'MULH': 0x01, 'MULHSU': 0x01, 'MULHU': 0x01,
    'DIV': 0x01, 'DIVU': 0x01, 'REM': 0x01, 'REMU': 0x01
}

#=============================================================================
# 辅助函数
#=============================================================================

def parse_csr(csr_name):
    """
    解析 CSR 名称，返回 CSR 地址
    支持常见 CSR 名称和十六进制地址
    """
    csr_map = {
        'mstatus': 0x300,    # 机器模式状态
        'mtvec': 0x305,      # 异常向量基址
        'mepc': 0x341,       # 异常返回地址
        'mcause': 0x342,     # 异常原因
        'rdcycle': 0xC00,    # 周期计数器 (低32位)
        'rdcycleh': 0xC80,   # 周期计数器 (高32位)
        'rdinstret': 0xC02,  # 指令计数器 (低32位)
        'rdinstreth': 0xC82  # 指令计数器 (高32位)
    }
    if csr_name in csr_map:
        return csr_map[csr_name]
    # 支持十六进制格式 (如 0x300)
    if csr_name.startswith('0x'):
        return int(csr_name, 16)
    return int(csr_name)

def parse_register(reg):
    """
    解析寄存器名称，返回寄存器编号 (0-31)
    格式: x0, x1, ..., x31
    """
    if reg.startswith('x'):
        return int(reg[1:])
    return 0

def parse_immediate(imm):
    """
    解析立即数，支持十进制和十六进制
    """
    if imm.startswith('0x'):
        return int(imm, 16)
    return int(imm)

def sign_extend(value, bits):
    """
    符号扩展
    """
    if value & (1 << (bits - 1)):
        value -= (1 << bits)
    return value

#=============================================================================
# 指令编码函数
#=============================================================================

def encode_instruction(parts):
    """
    编码单条指令为 32 位机器码
    
    Args:
        parts: 指令各部分的列表，如 ['ADD', 'x1,', 'x2,', 'x3']
    
    Returns:
        32 位机器码 (整数)
    """
    opcode_name = parts[0]
    opcode = OPCODES[opcode_name]
    
    #=========================================================================
    # R-type 指令: op rd, rs1, rs2
    # 格式: funct7[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    # 包括基础指令和 M 扩展的乘除法指令
    #=========================================================================
    if opcode_name in ['ADD', 'SUB', 'SLL', 'SLT', 'SLTU', 'XOR', 'SRL', 'SRA', 'OR', 'AND',
                       'MUL', 'MULH', 'MULHSU', 'MULHU', 'DIV', 'DIVU', 'REM', 'REMU']:
        rd = parse_register(parts[1].rstrip(','))
        rs1 = parse_register(parts[2].rstrip(','))
        rs2 = parse_register(parts[3])
        funct3 = FUNCT3[opcode_name]
        funct7 = FUNCT7[opcode_name]
        return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # I-type 立即数运算: op rd, rs1, imm
    # 格式: imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['ADDI', 'SLTI', 'SLTIU', 'XORI', 'ORI', 'ANDI']:
        rd = parse_register(parts[1].rstrip(','))
        rs1 = parse_register(parts[2].rstrip(','))
        imm = parse_immediate(parts[3]) & 0xFFF  # 12 位立即数
        funct3 = FUNCT3[opcode_name]
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # I-type 移位指令: op rd, rs1, shamt
    # 格式: funct7[31:25] | shamt[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['SLLI', 'SRLI', 'SRAI']:
        rd = parse_register(parts[1].rstrip(','))
        rs1 = parse_register(parts[2].rstrip(','))
        shamt = parse_immediate(parts[3]) & 0x1F  # 5 位移位量
        funct3 = FUNCT3[opcode_name]
        funct7 = FUNCT7[opcode_name]
        imm = (funct7 << 5) | shamt
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # I-type 加载指令: op rd, offset(rs1)
    # 格式: imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['LB', 'LH', 'LW', 'LBU', 'LHU']:
        rd = parse_register(parts[1].rstrip(','))
        match = re.match(r'(-?\d+)\(x(\d+)\)', parts[2])
        imm = parse_immediate(match.group(1)) & 0xFFF
        rs1 = int(match.group(2))
        funct3 = FUNCT3[opcode_name]
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # S-type 存储指令: op rs2, offset(rs1)
    # 格式: imm[11:5][31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[4:0][11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['SB', 'SH', 'SW']:
        rs2 = parse_register(parts[1].rstrip(','))
        match = re.match(r'(-?\d+)\(x(\d+)\)', parts[2])
        imm = parse_immediate(match.group(1)) & 0xFFF
        rs1 = int(match.group(2))
        funct3 = FUNCT3[opcode_name]
        imm_11_5 = (imm >> 5) & 0x7F
        imm_4_0 = imm & 0x1F
        return (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode
    
    #=========================================================================
    # B-type 分支指令: op rs1, rs2, offset
    # 格式: imm[12|10:5][31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[4:1|11][11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
        rs1 = parse_register(parts[1].rstrip(','))
        rs2 = parse_register(parts[2].rstrip(','))
        imm = parse_immediate(parts[3]) & 0x1FFE  # 13 位，最低位为 0
        funct3 = FUNCT3[opcode_name]
        imm_12 = (imm >> 12) & 1
        imm_11 = (imm >> 11) & 1  
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0xF
        return (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode
    
    #=========================================================================
    # U-type 指令: op rd, imm
    # 格式: imm[31:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['LUI', 'AUIPC']:
        rd = parse_register(parts[1].rstrip(','))
        imm = parse_immediate(parts[2]) & 0xFFFFF  # 20 位立即数
        return (imm << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # J-type 跳转指令: jal rd, offset
    # 格式: imm[20|10:1|11|19:12][31:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name == 'JAL':
        rd = parse_register(parts[1].rstrip(','))
        imm = parse_immediate(parts[2]) & 0x1FFFFE  # 21 位，最低位为 0
        imm_20 = (imm >> 20) & 1
        imm_19_12 = (imm >> 12) & 0xFF
        imm_11 = (imm >> 11) & 1
        imm_10_1 = (imm >> 1) & 0x3FF
        return (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # I-type JALR 指令: jalr rd, rs1, offset
    # 格式: imm[31:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name == 'JALR':
        rd = parse_register(parts[1].rstrip(','))
        rs1 = parse_register(parts[2].rstrip(','))
        imm = parse_immediate(parts[3]) & 0xFFF
        funct3 = FUNCT3[opcode_name]
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # CSR 指令: csrxx rd, csr, rs1/uimm
    # 格式: csr[31:20] | rs1/uimm[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
    #=========================================================================
    elif opcode_name in ['CSRRW', 'CSRRS', 'CSRRC', 'CSRRWI', 'CSRRSI', 'CSRRCI']:
        rd = parse_register(parts[1].rstrip(','))
        csr_addr = parse_csr(parts[2].rstrip(','))
        funct3 = FUNCT3[opcode_name]
        
        # 判断是立即数版本还是寄存器版本
        if opcode_name.endswith('I'):  # 立即数版本
            uimm = parse_immediate(parts[3]) & 0x1F  # 5 位立即数
            return (csr_addr << 20) | (uimm << 15) | (funct3 << 12) | (rd << 7) | opcode
        else:  # 寄存器版本
            rs1 = parse_register(parts[3])
            return (csr_addr << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    #=========================================================================
    # 系统指令
    #=========================================================================
    elif opcode_name == 'ECALL':
        return 0x73
    elif opcode_name == 'EBREAK':
        return 0x100073
    
    return 0

#=============================================================================
# 主转换函数
#=============================================================================

def convert_instructions(input_file, output_file):
    """
    转换指令文件
    
    Args:
        input_file: 输入汇编文件路径
        output_file: 输出机器码文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('//'):
                continue
            
            parts = line.split()
            if not parts:
                continue
            
            try:
                machine_code = encode_instruction(parts)
                
                # 转换为大端序字节
                bytes_data = machine_code.to_bytes(4, 'big')
                
                # 写入原始汇编作为注释
                f_out.write(f"// {line}\n")
                
                # 写入十六进制字节 (每个字节一行，大写)
                for byte in bytes_data:
                    f_out.write(f"{byte:02X}\n")
                
            except Exception as e:
                print(f"Error processing line: {line}")
                print(f"Error: {e}")

#=============================================================================
# 程序入口
#=============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python rv32i_transfer.py <汇编文件>")
        print("示例: python rv32i_transfer.py instr_r.dat")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = "IM.dat"
    
    try:
        convert_instructions(input_file, output_file)
        print(f"转换完成！")
        print(f"输入文件：{input_file}")
        print(f"输出文件：{output_file}")
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except Exception as e:
        print(f"转换过程中发生错误：{e}")
