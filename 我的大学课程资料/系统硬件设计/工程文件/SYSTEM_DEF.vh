/******************************************************************************
* 文件名:     SYSTEM_DEF.vh
* 项目:       五级流水线 RISC-V CPU 设计
* 描述:       系统全局宏定义文件，包含所有模块共用的常量、参数和宏定义
*
* 修改记录:
*   2025-12-27: 添加仿真/上板模式切换宏
******************************************************************************/

`ifndef SYSTEM_DEF_VH
`define SYSTEM_DEF_VH

//=============================================================================
// 工作模式选择 (请根据需要注释/取消注释以下宏定义)
//=============================================================================
// 定义 FPGA_BOARD 宏时，编译上板验证版本（包含LED、数码管等硬件接口）
// 注释掉 FPGA_BOARD 宏时，编译仿真版本（仅包含CPU核心，用于testbench仿真）
//
// 使用方法:
//   1. 仿真模式: 将下面的 `define FPGA_BOARD 注释掉
//   2. 上板模式: 取消注释 `define FPGA_BOARD
//=============================================================================

// *** 仿真模式 (默认) ***
// 如需上板验证，请取消下面一行的注释:
// `define FPGA_BOARD

// *** 上板验证模式 ***
// 如需仿真验证，请注释下面一行:
// `define FPGA_BOARD

//=============================================================================
// 指令存储器 (Instruction Memory) 参数
//=============================================================================
`define INSTR_MEM_SIZE 512          // 指令存储器大小: 512 字节
`define INSTR_WIDTH 32              // 指令宽度: 32 位 (RV32I)
`define INSTR_ADDR_WIDTH 32         // 指令地址宽度: 32 位

//=============================================================================
// 数据存储器 (Data Memory) 参数
//=============================================================================
`define DATA_MEM_SIZE 64            // 数据存储器大小: 64 字节
`define DATA_MEM_WIDTH 32           // 数据宽度: 32 位
`define DATA_MEM_ADDR_WIDTH 32      // 数据地址宽度: 32 位

//=============================================================================
// CPU 核心参数
//=============================================================================
`define PC_WIDTH 32                 // 程序计数器宽度: 32 位
`define DATA_WIDTH 32               // 数据总线宽度: 32 位
`define ADDR_WIDTH 5                // 寄存器地址宽度: 5 位 (可寻址 32 个寄存器)

//=============================================================================
// 寄存器堆 (Register File) 参数
//=============================================================================
`define GPR_SIZE 32                 // 通用寄存器数量: 32 个 (x0-x31)

//=============================================================================
// 立即数类型定义 (用于 ImmGen 模块)
// 根据 RISC-V 指令格式分为 5 种类型
//=============================================================================
`define I_TYPE_IMM 0                // I 型立即数: 用于 ADDI, LW, JALR 等
`define S_TYPE_IMM 1                // S 型立即数: 用于 SW, SH, SB 等存储指令
`define B_TYPE_IMM 2                // B 型立即数: 用于 BEQ, BNE 等分支指令
`define U_TYPE_IMM 3                // U 型立即数: 用于 LUI, AUIPC
`define J_TYPE_IMM 4                // J 型立即数: 用于 JAL 跳转指令

//=============================================================================
// 操作码 (Opcode) 定义 - 指令[6:0]
// 根据 RISC-V RV32I 指令集规范
//=============================================================================
`define OPCODE_WIDTH 7              // 操作码宽度: 7 位

// R 型指令: 寄存器-寄存器运算 (ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, SLT, SLTU)
`define R_TYPE 7'b0110011

// I 型指令 - 立即数算术运算 (ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI)
`define I_TYPE_ALU 7'b0010011

// I 型指令 - 加载 (LB, LH, LW, LBU, LHU)
`define I_TYPE_LOAD 7'b0000011

// I 型指令 - 间接跳转 (JALR)
`define I_TYPE_JALR 7'b1100111

// I 型指令 - CSR 操作 (CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI)
`define I_TYPE_CSR 7'b1110011

// S 型指令 - 存储 (SB, SH, SW)
`define S_TYPE 7'b0100011

// B 型指令 - 条件分支 (BEQ, BNE, BLT, BGE, BLTU, BGEU)
`define B_TYPE 7'b1100011

// U 型指令 - 加载高位立即数 (LUI)
`define U_TYPE_LUI 7'b0110111

// U 型指令 - PC 加高位立即数 (AUIPC)
`define U_TYPE_AUIPC 7'b0010111

// J 型指令 - 直接跳转 (JAL)
`define J_TYPE_JAL 7'b1101111

//=============================================================================
// ALU 操作码 (ALU_op) 定义 - Control 单元输出
// 用于告诉 ALU_Control 当前是什么类型的操作
//=============================================================================
`define ALU_OP_ADD 2'b00            // 加法操作 (Load/Store 地址计算)
`define ALU_OP_BRANCH 2'b01         // 分支操作 (需要比较)
`define ALU_OP_R_TYPE 2'b10         // R 型指令 (根据 funct3/funct7 决定)
`define ALU_OP_I_TYPE 2'b11         // I 型立即数指令 (根据 funct3 决定)

//=============================================================================
// ALU 控制信号 (ALU_Ctrl_op) 定义 - ALU_Control 输出
// 直接控制 ALU 执行具体运算
//=============================================================================
`define ALU_CTRL_ADD  5'b00000      // 加法: Src1 + Src2
`define ALU_CTRL_SUB  5'b00001      // 减法: Src1 - Src2
`define ALU_CTRL_SLL  5'b00010      // 逻辑左移: Src1 << Src2[4:0]
`define ALU_CTRL_SLT  5'b00011      // 有符号小于比较: (Src1 < Src2) ? 1 : 0
`define ALU_CTRL_SLTU 5'b00100      // 无符号小于比较: (Src1 < Src2) ? 1 : 0
`define ALU_CTRL_XOR  5'b00101      // 异或: Src1 ^ Src2
`define ALU_CTRL_SRL  5'b00110      // 逻辑右移: Src1 >> Src2[4:0]
`define ALU_CTRL_SRA  5'b00111      // 算术右移: Src1 >>> Src2[4:0] (保留符号位)
`define ALU_CTRL_OR   5'b01000      // 或: Src1 | Src2
`define ALU_CTRL_AND  5'b01001      // 与: Src1 & Src2
`define ALU_CTRL_GEU  5'b01010      // 无符号大于等于: (Src1 >= Src2) ? 1 : 0
`define ALU_CTRL_GE   5'b01011      // 有符号大于等于: (Src1 >= Src2) ? 1 : 0

// M 扩展 - 乘除法指令
`define ALU_CTRL_MUL    5'b01100    // 乘法: (Src1 * Src2)[31:0] (有符号低32位)
`define ALU_CTRL_MULH   5'b01101    // 乘法高位: (Src1 * Src2)[63:32] (有符号×有符号)
`define ALU_CTRL_MULHSU 5'b01110    // 乘法高位: (Src1 * Src2)[63:32] (有符号×无符号)
`define ALU_CTRL_MULHU  5'b01111    // 乘法高位: (Src1 * Src2)[63:32] (无符号×无符号)
`define ALU_CTRL_DIV    5'b10000    // 除法: Src1 / Src2 (有符号)
`define ALU_CTRL_DIVU   5'b10001    // 除法: Src1 / Src2 (无符号)
`define ALU_CTRL_REM    5'b10010    // 取余: Src1 % Src2 (有符号)
`define ALU_CTRL_REMU   5'b10011    // 取余: Src1 % Src2 (无符号)

//=============================================================================
// 特殊指令定义
//=============================================================================
`define NOP 0                       // 空操作指令 (用于流水线冲刷)

//=============================================================================
// 分支预测参数
//=============================================================================
`define BHT_PC_WIDTH 6              // BHT 索引宽度: 6 位 (使用 PC[5:0])
`define BTB_PC_WIDTH 6              // BTB 索引宽度: 6 位 (使用 PC[5:0])
`define BHT_SIZE 64                 // 分支历史表大小: 64 项
`define BTB_SIZE 64                 // 分支目标缓冲大小: 64 项

//=============================================================================
// Cache 参数 (预留，当前未使用)
//=============================================================================
`define CACHE_SIZE 8192                                     // Cache 总大小: 8KB
`define WAY 2                                               // 组相联度: 2 路
`define BLOCK_BYTE_SIZE 32                                  // 块大小: 32 字节
`define BLOCK_WORD_SIZE (`BLOCK_BYTE_SIZE / 4)              // 块大小: 8 字 (32/4)
`define SET_NUM (`CACHE_SIZE / (`BLOCK_BYTE_SIZE * `WAY))   // 组数: 128 组
`define OFFSET_WIDTH ($clog2(`BLOCK_BYTE_SIZE))             // 块内偏移宽度: 5 位
`define WORD_OFFSET_WIDTH ($clog2(`BLOCK_WORD_SIZE))        // 字偏移宽度: 3 位
`define INDEX_WIDTH ($clog2(`SET_NUM))                      // 索引宽度: 7 位
`define TAG_WIDTH (`INSTR_ADDR_WIDTH - `OFFSET_WIDTH - `INDEX_WIDTH)  // 标签宽度

`endif
