/******************************************************************************
* 文件名:     MEM_WB.v
* 描述:       MEM/WB 流水线寄存器
*             在 MEM (访存) 和 WB (写回) 阶段之间传递数据和控制信号
*
* 传递内容:
*   - 控制信号: Reg_w (寄存器写使能), WB_sel (写回选择)
*   - 数据: ALU_Result, Mem_R_Data, PC+4, Imm, Rd_Addr
******************************************************************************/

`include "SYSTEM_DEF.vh"

module MEM_WB(
    input clk,                              // 系统时钟
    input rst_n,                            // 异步复位 (低电平有效)
    
    //=========================================================================
    // 控制信号输入 (来自 MEM 阶段)
    //=========================================================================
    input MEM_Reg_w,                        // 寄存器写使能
    input [1:0] MEM_WB_sel,                 // 写回数据选择

    //=========================================================================
    // 数据输入 (来自 MEM 阶段)
    //=========================================================================
    input [`DATA_WIDTH - 1:0] MEM_Imm,       // 立即数 (用于 LUI)
    input [`DATA_WIDTH - 1:0] MEM_PC_Plus_4, // PC + 4 (用于 JAL/JALR)
    input [`DATA_WIDTH - 1:0] MEM_Mem_R_Data,// 内存读取数据 (用于 Load)
    input [`DATA_WIDTH - 1:0] MEM_ALU_Result,// ALU 结果
    input [`ADDR_WIDTH - 1:0] MEM_Rd_Addr,   // 目标寄存器地址

    //=========================================================================
    // 控制信号输出 (传递到 WB 阶段)
    //=========================================================================
    output reg WB_Reg_w,                    // 寄存器写使能
    output reg [1:0] WB_WB_sel,             // 写回数据选择

    //=========================================================================
    // 数据输出 (传递到 WB 阶段)
    //=========================================================================
    output reg [`DATA_WIDTH - 1:0] WB_Imm,
    output reg [`DATA_WIDTH - 1:0] WB_PC_Plus_4,
    output reg [`DATA_WIDTH - 1:0] WB_Mem_R_Data,
    output reg [`DATA_WIDTH - 1:0] WB_ALU_Result,
    output reg [`ADDR_WIDTH - 1:0] WB_Rd_Addr
);

    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            //=================================================================
            // 复位: 所有信号清零
            //=================================================================
            WB_Reg_w <= 0;
            WB_WB_sel <= 0;
            WB_Imm <= 0;
            WB_PC_Plus_4 <= 0;
            WB_Mem_R_Data <= 0;
            WB_ALU_Result <= 0;
            WB_Rd_Addr <= 0;
        end
        else begin
            //=================================================================
            // 正常传递: 所有信号传递到下一阶段
            //=================================================================
            // 控制信号
            WB_Reg_w <= MEM_Reg_w;
            WB_WB_sel <= MEM_WB_sel;

            // 数据
            WB_Imm <= MEM_Imm;
            WB_PC_Plus_4 <= MEM_PC_Plus_4;
            WB_Mem_R_Data <= MEM_Mem_R_Data;
            WB_ALU_Result <= MEM_ALU_Result;
            WB_Rd_Addr <= MEM_Rd_Addr;
        end
    end

endmodule
