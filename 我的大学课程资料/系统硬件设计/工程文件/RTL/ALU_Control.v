/******************************************************************************
* 文件名:     ALU_Control.v
* 描述:       ALU 控制单元
*             根据 ALU_op (来自 Control) 和 funct3/funct7 生成 ALU 控制信号
*             同时生成内存写字节选通信号 (用于 SB/SH/SW)
*
* ALU_op 编码 (来自主控制单元):
*   00 - ADD    : 直接执行加法 (Load/Store 地址计算)
*   01 - BRANCH : 分支比较操作
*   10 - R_TYPE : R 型指令，根据 funct7 + funct3 决定
*   11 - I_TYPE : I 型立即数指令，根据 funct3 决定
******************************************************************************/

`include "SYSTEM_DEF.vh"

module ALU_Control(
    input [1:0] ALU_op,                     // ALU 操作类型 (来自 Control)
    input [2:0] Funct3,                     // funct3 字段 (指令[14:12])
    input [6:0] Funct7,                     // funct7 字段 (指令[31:25])
    output reg [3:0] Mem_W_Strb,            // 内存写字节选通 (用于 Store)
    output reg [4:0] ALU_Ctrl_op            // 输出: ALU 控制信号 (扩展到5位)
);

    always @(*) begin
        case(ALU_op)
        
        //=====================================================================
        // ALU_OP_ADD: 直接加法
        // 用于: Load/Store 地址计算, LUI, AUIPC, JAL, JALR
        // 同时根据 funct3 生成 Store 的字节选通信号
        //=====================================================================
        `ALU_OP_ADD : begin
            ALU_Ctrl_op = `ALU_CTRL_ADD;
            // 根据 funct3 设置 Store 指令的写字节选通
            case(Funct3)
                3'b000: Mem_W_Strb = 4'b0001;   // SB: 写 1 字节
                3'b001: Mem_W_Strb = 4'b0011;   // SH: 写 2 字节 (半字)
                3'b010: Mem_W_Strb = 4'b1111;   // SW: 写 4 字节 (全字)
                default: Mem_W_Strb = 4'b0000;  // 非 Store 指令
            endcase
        end
        
        //=====================================================================
        // ALU_OP_BRANCH: 分支比较
        // funct3 决定比较类型
        //=====================================================================
        `ALU_OP_BRANCH : begin
            Mem_W_Strb = 4'b0000;
            case(Funct3)
                3'b000: ALU_Ctrl_op = `ALU_CTRL_SUB;   // BEQ:  相等 (用减法，看零标志)
                3'b001: ALU_Ctrl_op = `ALU_CTRL_SUB;   // BNE:  不等 (用减法，看零标志)
                3'b100: ALU_Ctrl_op = `ALU_CTRL_SLT;   // BLT:  有符号小于
                3'b101: ALU_Ctrl_op = `ALU_CTRL_GE;    // BGE:  有符号大于等于
                3'b110: ALU_Ctrl_op = `ALU_CTRL_SLTU;  // BLTU: 无符号小于
                3'b111: ALU_Ctrl_op = `ALU_CTRL_GEU;   // BGEU: 无符号大于等于
                default: ALU_Ctrl_op = `ALU_CTRL_SUB;
            endcase
        end
        
        //=====================================================================
        // ALU_OP_R_TYPE: R 型指令
        // 由 funct7 + funct3 共同决定操作
        // funct7 = 0000001 表示 M 扩展 (乘除法指令)
        //=====================================================================
        `ALU_OP_R_TYPE : begin
            Mem_W_Strb = 4'b0000;
            case({Funct7, Funct3})
                // 标准 RV32I 指令
                {7'b0000000, 3'b000}: ALU_Ctrl_op = `ALU_CTRL_ADD;   // ADD
                {7'b0100000, 3'b000}: ALU_Ctrl_op = `ALU_CTRL_SUB;   // SUB
                {7'b0000000, 3'b001}: ALU_Ctrl_op = `ALU_CTRL_SLL;   // SLL
                {7'b0000000, 3'b010}: ALU_Ctrl_op = `ALU_CTRL_SLT;   // SLT
                {7'b0000000, 3'b011}: ALU_Ctrl_op = `ALU_CTRL_SLTU;  // SLTU
                {7'b0000000, 3'b100}: ALU_Ctrl_op = `ALU_CTRL_XOR;   // XOR
                {7'b0000000, 3'b101}: ALU_Ctrl_op = `ALU_CTRL_SRL;   // SRL
                {7'b0100000, 3'b101}: ALU_Ctrl_op = `ALU_CTRL_SRA;   // SRA
                {7'b0000000, 3'b110}: ALU_Ctrl_op = `ALU_CTRL_OR;    // OR
                {7'b0000000, 3'b111}: ALU_Ctrl_op = `ALU_CTRL_AND;   // AND
                
                // M 扩展 - 乘除法指令 (funct7 = 0000001)
                {7'b0000001, 3'b000}: ALU_Ctrl_op = `ALU_CTRL_MUL;    // MUL
                {7'b0000001, 3'b001}: ALU_Ctrl_op = `ALU_CTRL_MULH;   // MULH
                {7'b0000001, 3'b010}: ALU_Ctrl_op = `ALU_CTRL_MULHSU; // MULHSU
                {7'b0000001, 3'b011}: ALU_Ctrl_op = `ALU_CTRL_MULHU;  // MULHU
                {7'b0000001, 3'b100}: ALU_Ctrl_op = `ALU_CTRL_DIV;    // DIV
                {7'b0000001, 3'b101}: ALU_Ctrl_op = `ALU_CTRL_DIVU;   // DIVU
                {7'b0000001, 3'b110}: ALU_Ctrl_op = `ALU_CTRL_REM;    // REM
                {7'b0000001, 3'b111}: ALU_Ctrl_op = `ALU_CTRL_REMU;   // REMU
                
                default: ALU_Ctrl_op = `ALU_CTRL_ADD;
            endcase
        end
        
        //=====================================================================
        // ALU_OP_I_TYPE: I 型立即数指令
        // 由 funct3 决定操作，移位指令还需看 funct7
        //=====================================================================
        `ALU_OP_I_TYPE : begin
            Mem_W_Strb = 4'b0000;
            case (Funct3)
                3'b000: ALU_Ctrl_op = `ALU_CTRL_ADD;   // ADDI
                3'b010: ALU_Ctrl_op = `ALU_CTRL_SLT;   // SLTI
                3'b011: ALU_Ctrl_op = `ALU_CTRL_SLTU;  // SLTIU
                3'b100: ALU_Ctrl_op = `ALU_CTRL_XOR;   // XORI
                3'b110: ALU_Ctrl_op = `ALU_CTRL_OR;    // ORI
                3'b111: ALU_Ctrl_op = `ALU_CTRL_AND;   // ANDI
                3'b001: ALU_Ctrl_op = `ALU_CTRL_SLL;   // SLLI
                // SRLI/SRAI: 由 funct7[5] 区分
                3'b101: ALU_Ctrl_op = (Funct7 == 7'b0000000)? `ALU_CTRL_SRL : `ALU_CTRL_SRA;
                default: ALU_Ctrl_op = `ALU_CTRL_ADD;
            endcase                
        end
        
        default: begin
            ALU_Ctrl_op = `ALU_CTRL_ADD;
            Mem_W_Strb = 4'b0000;
        end
        endcase
    end
endmodule
