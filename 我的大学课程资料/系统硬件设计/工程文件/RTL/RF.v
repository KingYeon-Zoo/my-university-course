/******************************************************************************
* 文件名:     RF.v
* 描述:       寄存器堆 (Register File)
*             包含 32 个 32 位通用寄存器 (x0-x31)
*             支持 2 个读端口和 1 个写端口
*
* 特点:
*   - x0 寄存器硬连线为 0，读取始终返回 0，写入被忽略
*   - 写操作在时钟下降沿执行 (避免读写冲突)
*   - 读操作是组合逻辑，无延迟
*   - 支持调试端口（用于FPGA上板验证时读取寄存器值）
*
* 修改记录:
*   2025-12-27: 添加调试读端口，支持上板验证
******************************************************************************/

`include "SYSTEM_DEF.vh"

module RF(
    input clk,                              // 系统时钟
    input rst_n,                            // 异步复位 (低电平有效)
    input Reg_w,                            // 写使能
    input [`ADDR_WIDTH - 1:0] Rs1_Addr,     // 读端口 1 地址 (5位)
    input [`ADDR_WIDTH - 1:0] Rs2_Addr,     // 读端口 2 地址 (5位)
    input [`ADDR_WIDTH - 1:0] Rd_Addr,      // 写端口地址 (5位)
    input [`DATA_WIDTH - 1:0] Rd_Data,      // 写入数据 (32位)
    output [`DATA_WIDTH - 1:0] Rs1_Data,    // 读端口 1 数据
    output [`DATA_WIDTH - 1:0] Rs2_Data,    // 读端口 2 数据
    
`ifdef FPGA_BOARD
    // 调试端口 (仅在FPGA上板模式下启用)
    input [`ADDR_WIDTH - 1:0] Debug_Addr1,  // 调试读端口 1 地址
    input [`ADDR_WIDTH - 1:0] Debug_Addr2,  // 调试读端口 2 地址
    output [`DATA_WIDTH - 1:0] Debug_Data1, // 调试读端口 1 数据
    output [`DATA_WIDTH - 1:0] Debug_Data2  // 调试读端口 2 数据
`endif
);

    // 32 个 32 位通用寄存器
    reg [`DATA_WIDTH - 1:0] GPR[0:`GPR_SIZE - 1];
    integer i;

    //=========================================================================
    // 写操作: 下降沿写入
    // 注意: 在下降沿写入可以实现同一周期内的写后读
    //=========================================================================
    always @(negedge clk or negedge rst_n) begin
        if(!rst_n) begin
            // 复位: 所有寄存器清零
            for (i = 0; i < `GPR_SIZE; i = i + 1) 
                GPR[i] <= 0;
        end
        else begin
            // 写使能有效且目标不是 x0 时执行写入
            if(Reg_w && Rd_Addr != 0) 
                GPR[Rd_Addr] <= Rd_Data; 
            else;
        end
    end

    //=========================================================================
    // 读操作: 组合逻辑
    // x0 寄存器永远返回 0
    //=========================================================================
    assign Rs1_Data = (Rs1_Addr == 0) ? 32'b0 : GPR[Rs1_Addr];
    assign Rs2_Data = (Rs2_Addr == 0) ? 32'b0 : GPR[Rs2_Addr];

`ifdef FPGA_BOARD
    //=========================================================================
    // 调试读端口 (仅在FPGA上板模式下有效)
    // 用于LED显示、数码管显示等外部观察
    //=========================================================================
    assign Debug_Data1 = (Debug_Addr1 == 0) ? 32'b0 : GPR[Debug_Addr1];
    assign Debug_Data2 = (Debug_Addr2 == 0) ? 32'b0 : GPR[Debug_Addr2];
`endif

endmodule
