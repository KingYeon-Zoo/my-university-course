/******************************************************************************
* 文件名:     ID_EX.v
* 描述:       ID/EX 流水线寄存器
*             在 ID (译码) 和 EX (执行) 阶段之间传递数据和控制信号
*
* 功能:
*   1. 正常传递: 将 ID 阶段的数据和控制信号传递到 EX 阶段
*   2. 流水线冲刷: ID_EX_Flush=1 时，控制信号清零 (插入气泡)
*      注意: 数据信号不清零，因为被清零的控制信号会使其无效
******************************************************************************/

`include "SYSTEM_DEF.vh"

module ID_EX(
    input clk,                              // 系统时钟
    input rst_n,                            // 异步复位 (低电平有效)
    input ID_EX_Flush,                      // 冲刷信号 (来自冒险检测或分支)
    
    //=========================================================================
    // 控制信号输入 (来自 Control 单元)
    //=========================================================================
    input [1:0] ID_ALU_op,                  // ALU 操作类型
    input ID_ALU_src1,                      // ALU 源1选择
    input ID_ALU_src2,                      // ALU 源2选择
    input ID_Branch,                        // 分支指令标志
    input ID_Jump,                          // 跳转指令标志
    input ID_Mem_r,                         // 内存读使能
    input ID_Mem_w,                         // 内存写使能
    input ID_Reg_w,                         // 寄存器写使能
    input [1:0] ID_WB_sel,                  // 写回数据选择

    //=========================================================================
    // 数据输入
    //=========================================================================
    input [`DATA_WIDTH - 1:0] ID_PC,        // PC 值
    input [`DATA_WIDTH - 1:0] ID_Rs1_Data,  // Rs1 寄存器数据
    input [`DATA_WIDTH - 1:0] ID_Rs2_Data,  // Rs2 寄存器数据
    input [`DATA_WIDTH - 1:0] ID_Imm,       // 立即数
    input [`ADDR_WIDTH - 1:0] ID_Rs1_Addr,  // Rs1 地址 (用于前递)
    input [`ADDR_WIDTH - 1:0] ID_Rs2_Addr,  // Rs2 地址 (用于前递)
    input [`ADDR_WIDTH - 1:0] ID_Rd_Addr,   // Rd 目标寄存器地址
    input [6:0] ID_Funct7,                  // funct7 字段
    input [2:0] ID_Funct3,                  // funct3 字段
    input ID_CSR_en,                        // CSR 操作使能
    input ID_Predict_Taken,                 // 分支预测结果

    //=========================================================================
    // 控制信号输出 (传递到 EX 阶段)
    //=========================================================================
    output reg [1:0] EX_ALU_op,
    output reg EX_ALU_src1,
    output reg EX_ALU_src2,
    output reg EX_Branch,
    output reg EX_Jump,
    output reg EX_Mem_r,
    output reg EX_Mem_w,
    output reg EX_Reg_w,
    output reg [1:0] EX_WB_sel,

    //=========================================================================
    // 数据输出 (传递到 EX 阶段)
    //=========================================================================
    output reg [`DATA_WIDTH - 1:0] EX_PC,
    output reg [`DATA_WIDTH - 1:0] EX_Rs1_Data,
    output reg [`DATA_WIDTH - 1:0] EX_Rs2_Data,
    output reg [`DATA_WIDTH - 1:0] EX_Imm,
    output reg [`ADDR_WIDTH - 1:0] EX_Rs1_Addr,
    output reg [`ADDR_WIDTH - 1:0] EX_Rs2_Addr,
    output reg [`ADDR_WIDTH - 1:0] EX_Rd_Addr,
    output reg [6:0] EX_Funct7,
    output reg [2:0] EX_Funct3,
    output reg EX_CSR_en,
    output reg EX_Predict_Taken
);

    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            //=================================================================
            // 复位: 所有信号清零
            //=================================================================
            EX_ALU_op <= 0;
            EX_ALU_src1 <= 0;
            EX_ALU_src2 <= 0;
            EX_Branch <= 0;
            EX_Jump <= 0;
            EX_Mem_r <= 0;
            EX_Mem_w <= 0;
            EX_Reg_w <= 0;
            EX_WB_sel <= 0;
            EX_PC <= 0;
            EX_Rs1_Data <= 0;
            EX_Rs2_Data <= 0;
            EX_Imm <= 0;
            EX_Rs1_Addr <= 0;
            EX_Rs2_Addr <= 0;
            EX_Rd_Addr <= 0;
            EX_Funct7 <= 0;
            EX_Funct3 <= 0;
            EX_CSR_en <= 0;
            EX_Predict_Taken <= 0;
        end
        else begin
            //=================================================================
            // 控制信号: 冲刷时清零，否则正常传递
            // 清零控制信号相当于插入 NOP (不写寄存器，不访问内存)
            //=================================================================
            EX_ALU_op <= (ID_EX_Flush)? 0 : ID_ALU_op;
            EX_ALU_src1 <= (ID_EX_Flush)? 0 : ID_ALU_src1;
            EX_ALU_src2 <= (ID_EX_Flush)? 0 : ID_ALU_src2;
            EX_Branch <= (ID_EX_Flush)? 0 : ID_Branch;
            EX_Jump <= (ID_EX_Flush)? 0 : ID_Jump;
            EX_Mem_r <= (ID_EX_Flush)? 0 : ID_Mem_r;
            EX_Mem_w <= (ID_EX_Flush)? 0 : ID_Mem_w;
            EX_Reg_w <= (ID_EX_Flush)? 0 : ID_Reg_w;
            EX_WB_sel <= (ID_EX_Flush)? 0 : ID_WB_sel;
            EX_CSR_en <= (ID_EX_Flush)? 0 : ID_CSR_en;

            //=================================================================
            // 数据信号: 始终传递 (控制信号清零后数据无效)
            //=================================================================
            EX_PC <= ID_PC;
            EX_Rs1_Data <= ID_Rs1_Data;
            EX_Rs2_Data <= ID_Rs2_Data;
            EX_Imm <= ID_Imm;
            EX_Rs1_Addr <= ID_Rs1_Addr;
            EX_Rs2_Addr <= ID_Rs2_Addr;
            EX_Rd_Addr <= ID_Rd_Addr;
            EX_Funct7 <= ID_Funct7;
            EX_Funct3 <= ID_Funct3;
            EX_Predict_Taken <= ID_Predict_Taken;
        end
    end
endmodule
