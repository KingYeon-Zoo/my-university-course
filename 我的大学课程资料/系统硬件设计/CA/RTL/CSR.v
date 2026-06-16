/******************************************************************************
* 文件名:     CSR.v
* 描述:       控制状态寄存器 (Control and Status Register)
*             实现 RISC-V 特权架构中的部分 CSR 寄存器
*
* 支持的 CSR:
*   mstatus (0x300) - 机器模式状态寄存器
*   mtvec   (0x305) - 机器模式异常向量基址
*   mepc    (0x341) - 机器模式异常 PC
*   mcause  (0x342) - 机器模式异常原因
*   rdcycle (0xC00) - 周期计数器 (只读，每周期自动递增)
*
* CSR 操作类型 (由 funct3[1:0] 决定):
*   01 - CSRRW: 写入新值，返回旧值
*   10 - CSRRS: 置位 (OR)，返回旧值
*   11 - CSRRC: 清位 (AND NOT)，返回旧值
******************************************************************************/

`include "SYSTEM_DEF.vh"

module CSR (
    input clk,                              // 系统时钟
    input rst_n,                            // 异步复位 (低电平有效)
    input CSR_en,                           // CSR 操作使能
    input [11:0] CSR_Addr,                  // CSR 地址 (12位)
    input [`DATA_WIDTH - 1:0] CSR_W_Data,   // 写入数据
    input [2:0] Funct3,                     // funct3 决定操作类型
    output reg [`DATA_WIDTH - 1:0] CSR_R_Data  // 读取数据
);

    //=========================================================================
    // CSR 地址定义
    //=========================================================================
    parameter CSR_MSTATUS = 12'h300;        // 机器模式状态
    parameter CSR_MTVEC   = 12'h305;        // 异常向量基址
    parameter CSR_MEPC    = 12'h341;        // 异常返回地址
    parameter CSR_MCAUSE  = 12'h342;        // 异常原因
    parameter CSR_RDCYCLE = 12'hc00;        // 周期计数器

    //=========================================================================
    // CSR 寄存器定义
    //=========================================================================
    reg [31:0] mstatus;                     // 机器模式状态
    reg [31:0] mtvec;                       // 异常向量基址
    reg [31:0] mepc;                        // 异常返回 PC
    reg [31:0] mcause;                      // 异常原因
    reg [31:0] rdcycle;                     // 周期计数器

    //=========================================================================
    // CSR 读取 (组合逻辑)
    //=========================================================================
    always @(*) begin
        case (CSR_Addr)
            CSR_MSTATUS: CSR_R_Data = mstatus;
            CSR_MTVEC:   CSR_R_Data = mtvec;
            CSR_MEPC:    CSR_R_Data = mepc;
            CSR_MCAUSE:  CSR_R_Data = mcause;
            CSR_RDCYCLE: CSR_R_Data = rdcycle;
            default:     CSR_R_Data = 32'h0;
        endcase
    end

    //=========================================================================
    // CSR 写入 (时序逻辑)
    // funct3[1:0] 决定写入方式:
    //   01 - CSRRW: csr = rs1
    //   10 - CSRRS: csr = csr | rs1
    //   11 - CSRRC: csr = csr & ~rs1
    //=========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // 复位: 所有 CSR 清零
            mstatus <= 32'h0;
            mtvec   <= 32'h0;
            mepc    <= 32'h0;
            mcause  <= 32'h0;
            rdcycle <= 32'h0;
        end
        else if (CSR_en) begin
            // CSR 操作使能时执行写入
            case (CSR_Addr)
                CSR_MSTATUS: begin
                    case (Funct3[1:0])
                        2'b01: mstatus <= CSR_W_Data;              // CSRRW: 直接写入
                        2'b10: mstatus <= mstatus | CSR_W_Data;    // CSRRS: 置位
                        2'b11: mstatus <= mstatus & ~CSR_W_Data;   // CSRRC: 清位
                    endcase
                end
                CSR_MTVEC: begin
                    case (Funct3[1:0])
                        2'b01: mtvec <= CSR_W_Data;
                        2'b10: mtvec <= mtvec | CSR_W_Data;
                        2'b11: mtvec <= mtvec & ~CSR_W_Data;
                    endcase
                end
                CSR_MEPC: begin
                    case (Funct3[1:0])
                        2'b01: mepc <= CSR_W_Data;
                        2'b10: mepc <= mepc | CSR_W_Data;
                        2'b11: mepc <= mepc & ~CSR_W_Data;
                    endcase
                end
                CSR_MCAUSE: begin
                    case (Funct3[1:0])
                        2'b01: mcause <= CSR_W_Data;
                        2'b10: mcause <= mcause | CSR_W_Data;
                        2'b11: mcause <= mcause & ~CSR_W_Data;
                    endcase
                end
                CSR_RDCYCLE: begin
                    rdcycle <= CSR_W_Data;  // rdcycle 可写 (非标准)
                end
                default: ;
            endcase
            rdcycle <= rdcycle + 1;         // 周期计数器递增
        end
        else begin
            rdcycle <= rdcycle + 1;         // 无 CSR 操作时也递增
        end
    end

endmodule
