/******************************************************************************
* 文件名:     PC.v
* 描述:       程序计数器 (Program Counter)
*             存储当前指令地址，每个时钟周期根据 PC_sel 选择下一个 PC 值
*
* PC_sel 编码:
*   0 -> PC+4        : 顺序执行下一条指令
*   1 -> BTB_PC      : 分支预测命中，跳转到预测地址
*   2 -> EX_PC+4     : 分支预测错误，恢复到正确的顺序地址
*   3 -> EX_ALU_Result: 实际跳转/分支目标地址
******************************************************************************/

`include "SYSTEM_DEF.vh"

module PC(
    input clk,                              // 系统时钟
    input rst_n,                            // 异步复位 (低电平有效)
    input [1:0] PC_sel,                     // PC 来源选择信号
    input [`PC_WIDTH-1:0] EX_ALU_Result,    // 来自 EX 阶段的跳转目标地址
    input [`PC_WIDTH-1:0] PC_Plus_4,        // PC + 4 (顺序下一条)
    input [`PC_WIDTH-1:0] BTB_PC,           // BTB 预测的跳转目标地址
    input [`PC_WIDTH-1:0] EX_PC_Plus_4,     // EX 阶段的 PC+4 (预测错误恢复用)
    output reg [`PC_WIDTH-1:0] IF_PC        // 输出: 当前 PC 值
    );

    // 时序逻辑: 每个上升沿更新 PC
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) 
            IF_PC <= 0;                     // 复位时 PC = 0
        else begin 
            case(PC_sel) 
                2'd0: IF_PC <= PC_Plus_4;       // 顺序执行
                2'd1: IF_PC <= BTB_PC;          // 预测跳转
                2'd2: IF_PC <= EX_PC_Plus_4;    // 预测错误恢复 (实际不跳转)
                2'd3: IF_PC <= EX_ALU_Result;   // 实际跳转目标
                default:;
            endcase
        end
    end

endmodule
