/******************************************************************************
* 文件名:     D_Mem.v
* 描述:       数据存储器 (Data Memory)
*             支持字节 (Byte)、半字 (Halfword)、字 (Word) 的读写
*
* 存储格式:   按字节存储 (小端序)
*             地址 N   -> 数据[7:0]   (最低字节)
*             地址 N+1 -> 数据[15:8]
*             地址 N+2 -> 数据[23:16]
*             地址 N+3 -> 数据[31:24] (最高字节)
*
* 写操作:     由 Mem_W_Strb (字节选通) 控制写入哪些字节
*             4'b0001 -> 写 1 字节 (SB)
*             4'b0011 -> 写 2 字节 (SH)
*             4'b1111 -> 写 4 字节 (SW)
*
* 读操作:     始终读取 4 字节，由 LDU 进行符号/零扩展
******************************************************************************/

`include "SYSTEM_DEF.vh"

module D_Mem(
    input clk,                              // 系统时钟
    input Mem_r,                            // 读使能
    input Mem_w,                            // 写使能
    input [`DATA_MEM_ADDR_WIDTH-1:0] Mem_Addr,  // 内存地址
    input [`DATA_MEM_WIDTH-1:0] Mem_W_Data,     // 写入数据
    input [3:0] Mem_W_Strb,                 // 写字节选通
    output [`DATA_MEM_WIDTH-1:0] Mem_R_Data     // 读取数据
);

    // 数据存储器: 32 字节，每个单元 8 位
    reg [7:0] DataMem [0:`DATA_MEM_SIZE - 1];
    integer i;
    
    //=========================================================================
    // 写操作: 上升沿写入，根据 Mem_W_Strb 选择写入的字节
    //=========================================================================
    always @(posedge clk) begin
        if(Mem_w) begin
            // 根据字节选通信号写入对应字节
            if(Mem_W_Strb[0]) DataMem[Mem_Addr]   <= Mem_W_Data[7:0];    // 字节 0
            if(Mem_W_Strb[1]) DataMem[Mem_Addr+1] <= Mem_W_Data[15:8];   // 字节 1
            if(Mem_W_Strb[2]) DataMem[Mem_Addr+2] <= Mem_W_Data[23:16];  // 字节 2
            if(Mem_W_Strb[3]) DataMem[Mem_Addr+3] <= Mem_W_Data[31:24];  // 字节 3
        end
        else;
    end

    //=========================================================================
    // 读操作: 组合逻辑，读取 4 个连续字节 (小端序)
    //=========================================================================
    assign Mem_R_Data = (Mem_r)? {DataMem[Mem_Addr+3],   // [31:24] 最高字节
                                  DataMem[Mem_Addr+2],   // [23:16]
                                  DataMem[Mem_Addr+1],   // [15:8]
                                  DataMem[Mem_Addr]}     // [7:0]   最低字节
                                : 0;

endmodule
