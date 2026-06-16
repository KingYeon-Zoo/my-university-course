/******************************************************************************
* 文件名:     EX_MEM.v
* 描述:       EX/MEM 流水线寄存器
*             在 EX (执行) 和 MEM (访存) 阶段之间传递数据和控制信号
*
* 传递内容:
*   - 控制信号: Mem_r, Mem_w, Reg_w, WB_sel, Mem_W_Strb, Funct3
*   - 数据: ALU_Result, Mem_W_Data, Rd_Addr, PC+4, Imm
******************************************************************************/

`include "SYSTEM_DEF.vh"

module EX_MEM(
    input clk,                              // 系统时钟
    input rst_n,                            // 异步复位 (低电平有效)
    
    //=========================================================================
    // 控制信号输入 (来自 EX 阶段)
    //=========================================================================
    input EX_Mem_r,                         // 内存读使能
    input EX_Mem_w,                         // 内存写使能
    input EX_Reg_w,                         // 寄存器写使能
    input [1:0] EX_WB_sel,                  // 写回数据选择
    
    //=========================================================================
    // 数据输入 (来自 EX 阶段)
    //=========================================================================
    input [`DATA_WIDTH - 1:0] EX_Imm,       // 立即数 (用于 LUI)
    input [`DATA_WIDTH - 1:0] EX_PC_Plus_4, // PC + 4 (用于 JAL/JALR)
    input [`DATA_WIDTH - 1:0] EX_ALU_Result,// ALU 运算结果
    input [`DATA_WIDTH - 1:0] EX_Mem_W_Data,// 内存写入数据 (来自 Rs2)
    input [`ADDR_WIDTH - 1:0] EX_Rd_Addr,   // 目标寄存器地址
    input [3:0] EX_Mem_W_Strb,              // 内存写字节选通
    input [2:0] EX_Funct3,                  // funct3 (用于 LDU)

    //=========================================================================
    // 控制信号输出 (传递到 MEM 阶段)
    //=========================================================================
    output reg MEM_Mem_r,
    output reg MEM_Mem_w,
    output reg MEM_Reg_w,
    output reg [1:0] MEM_WB_sel,
    
    //=========================================================================
    // 数据输出 (传递到 MEM 阶段)
    //=========================================================================
    output reg [`DATA_WIDTH - 1:0] MEM_Imm,
    output reg [`DATA_WIDTH - 1:0] MEM_PC_Plus_4,
    output reg [`DATA_WIDTH - 1:0] MEM_ALU_Result,
    output reg [`DATA_WIDTH - 1:0] MEM_Mem_W_Data,
    output reg [`ADDR_WIDTH - 1:0] MEM_Rd_Addr,
    output reg [3:0] MEM_Mem_W_Strb,
    output reg [2:0] MEM_Funct3
);

    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            //=================================================================
            // 复位: 所有信号清零
            //=================================================================
            MEM_Mem_r <= 0;
            MEM_Mem_w <= 0;
            MEM_Reg_w <= 0;
            MEM_WB_sel <= 0;
            MEM_Imm <= 0;
            MEM_PC_Plus_4 <= 0;
            MEM_ALU_Result <= 0;
            MEM_Mem_W_Data <= 0;
            MEM_Rd_Addr <= 0;
            MEM_Mem_W_Strb <= 0;
            MEM_Funct3 <= 0;
        end
        else begin
            //=================================================================
            // 正常传递: 所有信号传递到下一阶段
            //=================================================================
            // 控制信号
            MEM_Mem_r <= EX_Mem_r;
            MEM_Mem_w <= EX_Mem_w;
            MEM_Reg_w <= EX_Reg_w;
            MEM_WB_sel <= EX_WB_sel;
            MEM_Mem_W_Strb <= EX_Mem_W_Strb;
            MEM_Funct3 <= EX_Funct3;

            // 数据
            MEM_Imm <= EX_Imm;
            MEM_PC_Plus_4 <= EX_PC_Plus_4;
            MEM_ALU_Result <= EX_ALU_Result;
            MEM_Mem_W_Data <= EX_Mem_W_Data;
            MEM_Rd_Addr <= EX_Rd_Addr;
        end
    end

endmodule
