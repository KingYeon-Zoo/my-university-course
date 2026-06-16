/******************************************************************************
* 文件名:     PC_Adderr.v
* 描述:       PC 加法器
*             计算 PC + 4，得到顺序执行的下一条指令地址
*             当流水线停顿时 (IF_ID_w=0)，保持当前 PC 不变
*
* 注意:       RISC-V 是字节寻址，每条指令占 4 字节，所以 +4
******************************************************************************/

`include "SYSTEM_DEF.vh"

module PC_Adder(
    input IF_ID_w,                          // IF/ID 写使能 (0=停顿, 1=正常)
    input [`PC_WIDTH - 1:0] PC_In,          // 当前 PC 值
    output reg [`PC_WIDTH - 1:0] PC_Out     // 输出: PC + 4 或保持不变
);

    // 组合逻辑
    always @(*) begin
        if (IF_ID_w) 
            PC_Out = PC_In + 4;             // 正常执行: PC + 4
        else 
            PC_Out = PC_In;                 // 停顿: 保持 PC 不变
    end

endmodule
