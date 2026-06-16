/******************************************************************************
* 文件名:     I_Mem.v
* 描述:       指令存储器 (Instruction Memory)
*             只读存储器，根据 PC 地址读取 32 位指令
*
* 存储格式:   按字节存储 (大端序)
*             地址 N   -> 指令[31:24]
*             地址 N+1 -> 指令[23:16]
*             地址 N+2 -> 指令[15:8]
*             地址 N+3 -> 指令[7:0]
*
* 初始化:     通过测试平台使用 $readmemh 从 IM.dat 文件加载
******************************************************************************/

`include "SYSTEM_DEF.vh"

module I_Mem (
    input [`INSTR_ADDR_WIDTH - 1:0] Instr_Addr,  // 指令地址 (来自 PC)
    output reg [`INSTR_WIDTH - 1:0] Instr        // 输出: 32 位指令
);
    
    // 指令存储器: 256 字节，每个单元 8 位
    reg [7:0] InstrMem [0:`INSTR_MEM_SIZE - 1]; 

    // 组合逻辑读取: 将 4 个连续字节拼接成 32 位指令 (大端序)
    always @(*) begin
        Instr = {InstrMem[Instr_Addr],      // [31:24] 最高字节
                 InstrMem[Instr_Addr+1],    // [23:16]
                 InstrMem[Instr_Addr+2],    // [15:8]
                 InstrMem[Instr_Addr+3]};   // [7:0]  最低字节
    end

endmodule
