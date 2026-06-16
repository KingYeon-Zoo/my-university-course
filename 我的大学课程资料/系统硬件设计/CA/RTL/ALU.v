/******************************************************************************
* 文件名:     ALU.v
* 描述:       算术逻辑单元 (Arithmetic Logic Unit)
*             执行所有算术和逻辑运算
*
* 支持的操作 (由 ALU_Ctrl_op 控制):
*   0000 - ADD  : 加法
*   0001 - SUB  : 减法
*   0010 - SLL  : 逻辑左移
*   0011 - SLT  : 有符号小于比较
*   0100 - SLTU : 无符号小于比较
*   0101 - XOR  : 异或
*   0110 - SRL  : 逻辑右移
*   0111 - SRA  : 算术右移 (保留符号位)
*   1000 - OR   : 或
*   1001 - AND  : 与
*   1010 - GEU  : 无符号大于等于
*   1011 - GE   : 有符号大于等于
******************************************************************************/

`include "SYSTEM_DEF.vh"

module ALU(
    input [31:0] Src1,                      // 源操作数 1
    input [31:0] Src2,                      // 源操作数 2
    input [4:0] ALU_Ctrl_op,                // ALU 控制信号 (扩展到5位支持乘除法)
    output reg [31:0] ALU_Result,           // ALU 运算结果
    output Zero_Flag                        // 零标志 (结果为 0 时置 1)
);

    // 有符号数版本 (用于有符号比较、算术右移和有符号乘除法)
    wire signed [31:0] Src1_Signed, Src2_Signed;
    assign Src1_Signed = Src1;
    assign Src2_Signed = Src2;
    
    // 乘法结果 (64位)
    wire signed [63:0] mul_result_signed;      // 有符号乘法结果
    wire [63:0] mul_result_unsigned;           // 无符号乘法结果
    wire signed [63:0] mul_result_su;          // 有符号×无符号乘法结果
    
    assign mul_result_signed = Src1_Signed * Src2_Signed;
    assign mul_result_unsigned = Src1 * Src2;
    assign mul_result_su = Src1_Signed * $signed({1'b0, Src2});  // Src1有符号 × Src2无符号
    
    // 零标志: ALU 结果为 0 时置 1
    assign Zero_Flag = (ALU_Result == 0);
    
    // ALU 运算选择
    always @(*) begin
        case(ALU_Ctrl_op)
            //=================================================================
            // 算术运算
            //=================================================================
            `ALU_CTRL_ADD : ALU_Result = Src1 + Src2;           // 加法
            `ALU_CTRL_SUB : ALU_Result = Src1 - Src2;           // 减法
            
            //=================================================================
            // 比较运算 (结果为 0 或 1)
            //=================================================================
            `ALU_CTRL_SLT : ALU_Result = (Src1_Signed < Src2_Signed);  // 有符号 <
            `ALU_CTRL_SLTU: ALU_Result = (Src1 < Src2);                // 无符号 <
            `ALU_CTRL_GE  : ALU_Result = (Src1_Signed >= Src2_Signed); // 有符号 >=
            `ALU_CTRL_GEU : ALU_Result = (Src1 >= Src2);               // 无符号 >=
            
            //=================================================================
            // 逻辑运算
            //=================================================================
            `ALU_CTRL_AND : ALU_Result = Src1 & Src2;           // 按位与
            `ALU_CTRL_OR  : ALU_Result = Src1 | Src2;           // 按位或
            `ALU_CTRL_XOR : ALU_Result = Src1 ^ Src2;           // 按位异或
            
            //=================================================================
            // 移位运算 (移位量为 Src2 的低 5 位)
            //=================================================================
            `ALU_CTRL_SLL : ALU_Result = Src1 << Src2[4:0];     // 逻辑左移
            `ALU_CTRL_SRL : ALU_Result = Src1 >> Src2[4:0];     // 逻辑右移
            `ALU_CTRL_SRA : ALU_Result = Src1_Signed >>> Src2[4:0];  // 算术右移
            
            //=================================================================
            // 乘法运算 (M 扩展)
            //=================================================================
            `ALU_CTRL_MUL   : ALU_Result = mul_result_signed[31:0];    // MUL: 取低32位
            `ALU_CTRL_MULH  : ALU_Result = mul_result_signed[63:32];   // MULH: 有符号×有符号，取高32位
            `ALU_CTRL_MULHSU: ALU_Result = mul_result_su[63:32];       // MULHSU: 有符号×无符号，取高32位
            `ALU_CTRL_MULHU : ALU_Result = mul_result_unsigned[63:32]; // MULHU: 无符号×无符号，取高32位
            
            //=================================================================
            // 除法运算 (M 扩展)
            // 特殊情况处理:
            //   - 除以0: 结果为全1 (0xFFFFFFFF)
            //   - 溢出 (最小负数÷-1): 结果为最小负数本身
            //=================================================================
            `ALU_CTRL_DIV: begin
                if (Src2 == 0) 
                    ALU_Result = 32'hFFFFFFFF;  // 除以0
                else if (Src1_Signed == 32'h80000000 && Src2_Signed == -1)
                    ALU_Result = 32'h80000000;  // 溢出情况
                else 
                    ALU_Result = Src1_Signed / Src2_Signed;  // 正常有符号除法
            end
            
            `ALU_CTRL_DIVU: begin
                if (Src2 == 0)
                    ALU_Result = 32'hFFFFFFFF;  // 除以0
                else
                    ALU_Result = Src1 / Src2;   // 无符号除法
            end
            
            //=================================================================
            // 取余运算 (M 扩展)
            //=================================================================
            `ALU_CTRL_REM: begin
                if (Src2 == 0)
                    ALU_Result = Src1;  // 除以0时余数为被除数
                else if (Src1_Signed == 32'h80000000 && Src2_Signed == -1)
                    ALU_Result = 0;     // 溢出情况余数为0
                else
                    ALU_Result = Src1_Signed % Src2_Signed;  // 有符号取余
            end
            
            `ALU_CTRL_REMU: begin
                if (Src2 == 0)
                    ALU_Result = Src1;  // 除以0时余数为被除数
                else
                    ALU_Result = Src1 % Src2;   // 无符号取余
            end
            
            default: ALU_Result = 0;
        endcase
    end
endmodule
