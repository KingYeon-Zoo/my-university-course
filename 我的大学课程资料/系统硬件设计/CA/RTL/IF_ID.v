/******************************************************************************
* 文件名:     IF_ID.v
* 描述:       IF/ID 流水线寄存器
*             在 IF (取指) 和 ID (译码) 阶段之间传递数据
*
* 功能:
*   1. 正常传递: IF_ID_w=1, IF_ID_Flush=0 -> 传递 PC 和指令
*   2. 流水线停顿: IF_ID_w=0 -> 保持当前值不变 (用于 Load-Use 冒险)
*   3. 流水线冲刷: IF_ID_Flush=1 -> 插入 NOP 指令 (用于分支/跳转)
******************************************************************************/

`include "SYSTEM_DEF.vh"

module IF_ID(
    input clk,                                  // 系统时钟
    input rst_n,                                // 异步复位 (低电平有效)
    input IF_ID_w,                              // 写使能 (0=停顿)
    input IF_ID_Flush,                          // 冲刷信号 (1=插入气泡)
    input [`PC_WIDTH - 1:0] IF_PC,              // IF 阶段的 PC
    input [`INSTR_WIDTH - 1:0] IF_Instr,        // IF 阶段取到的指令
    input IF_Predict_Taken,                     // IF 阶段的分支预测结果
    output reg [`PC_WIDTH - 1:0] ID_PC,         // 传递到 ID 阶段的 PC
    output reg [`INSTR_WIDTH - 1:0] ID_Instr,   // 传递到 ID 阶段的指令
    output reg ID_Predict_Taken                 // 传递到 ID 阶段的预测结果
);

    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            // 复位: 清零所有寄存器
            ID_PC <= 0;
            ID_Instr <= `NOP;                   // 复位为 NOP 指令
            ID_Predict_Taken <= 0;
        end
        else begin
            if (IF_ID_w) begin
                // 写使能有效
                ID_PC <= (IF_ID_Flush)? 0 : IF_PC;          // 冲刷时 PC 清零
                ID_Instr <= (IF_ID_Flush)? `NOP : IF_Instr; // 冲刷时插入 NOP
                ID_Predict_Taken <= IF_Predict_Taken;
            end
            else begin
                // 停顿: 保持当前值不变
                ID_PC <= ID_PC;
                ID_Instr <= ID_Instr;
                ID_Predict_Taken <= ID_Predict_Taken;
            end
        end
    end

endmodule
