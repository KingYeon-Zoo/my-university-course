/******************************************************************************
* 文件名:     Control.v
* 描述:       主控制单元
*             根据指令的 Opcode 生成所有控制信号
*             同时负责生成流水线冲刷信号
*
* 控制信号说明:
*   Imm_Type   - 立即数类型 (I/S/B/U/J)
*   ALU_op     - ALU 操作类型 (00=加法, 01=分支, 10=R型, 11=I型)
*   WB_sel     - 写回数据选择 (00=ALU, 01=PC+4, 10=Mem, 11=Imm)
*   Reg_w      - 寄存器写使能
*   ALU_src1   - ALU 源1选择 (0=Rs1, 1=PC)
*   ALU_src2   - ALU 源2选择 (0=Rs2, 1=Imm)
*   Mem_w/r    - 内存写/读使能
*   Branch     - 分支指令标志
*   Jump       - 跳转指令标志
*   CSR_en     - CSR 操作使能
******************************************************************************/

`include "SYSTEM_DEF.vh"

module Control(
    input [`OPCODE_WIDTH - 1:0] Opcode,     // 操作码 (指令[6:0])
    input Branch_Taken,                      // 分支是否实际跳转
    input ID_EX_Jump,                        // EX 阶段是否是跳转指令
    input EX_Predict_Taken,                  // EX 阶段的分支预测结果
    input [`PC_WIDTH - 1:0] ID_PC,           // ID 阶段的 PC
    input [`PC_WIDTH - 1:0] Branch_PC,       // 分支目标地址
    
    // 控制信号输出
    output reg [2:0] Imm_Type,               // 立即数类型
    output reg [1:0] ALU_op,                 // ALU 操作类型
    output reg [1:0] WB_sel,                 // 写回数据选择
    output reg Reg_w,                        // 寄存器写使能
    output reg ALU_src1,                     // ALU 源操作数1选择
    output reg ALU_src2,                     // ALU 源操作数2选择
    output reg Mem_w,                        // 内存写使能
    output reg Mem_r,                        // 内存读使能
    output reg Branch,                       // 分支指令标志
    output reg Jump,                         // 跳转指令标志
    output reg CSR_en,                       // CSR 操作使能
    
    // 冲刷信号输出
    output reg IF_ID_Flush,                  // IF/ID 流水线冲刷
    output ID_EX_Flush_1                     // ID/EX 流水线冲刷
);

    //=========================================================================
    // 流水线冲刷逻辑
    // 需要冲刷的情况:
    //   1. 分支跳转但未预测 (Branch_Taken && !EX_Predict_Taken)
    //   2. 预测跳转但实际不跳转 (EX_Predict_Taken && !Branch_Taken)
    //   3. 跳转指令 (JAL/JALR)
    // 特殊情况: 如果 ID_PC == Branch_PC，说明已经在正确路径上，不需要冲刷
    //=========================================================================
    always @(*) begin
        if(ID_PC == Branch_PC)   //Branch_PC就是EX_ALU_Result
            IF_ID_Flush = 0;                // 已在正确路径，无需冲刷
        else begin
            if(Branch_Taken || ID_EX_Jump) 
                                            //Branch_Taken在BPU中计算,原理是如果分支实际跳转，则Branch_Taken为1，否则为0
                                            //对应的公式是: Branch_Taken = Taken && EX_Branch;
                IF_ID_Flush = 1;            // 实际跳转，冲刷错误路径
            else if(EX_Predict_Taken)       //EX_Predict_Taken就是Predict_Taken,Predict_Taken = Predict && BTB_Valid
                IF_ID_Flush = 1;            // 预测错误，冲刷错误路径
            else 
                IF_ID_Flush = 0;
        end
    end

    // ID/EX 冲刷信号 (与 IF/ID 类似，但用组合逻辑实现避免毛刺)
    assign ID_EX_Flush_1 = (ID_PC == Branch_PC)? 0 : 
        ((Branch_Taken || ID_EX_Jump) || (EX_Predict_Taken && ~(Branch_Taken || ID_EX_Jump)));
    
    //=========================================================================
    // 控制信号生成 - 根据 Opcode 译码
    //=========================================================================
    always @(*) begin
        case(Opcode)
        
        //---------------------------------------------------------------------
        // R 型指令: ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, SLT, SLTU
        // 格式: op rd, rs1, rs2
        //---------------------------------------------------------------------
        `R_TYPE : begin
            Imm_Type = 0;                   // 不使用立即数
            ALU_op = `ALU_OP_R_TYPE;        // 根据 funct3/funct7 决定操作
            Reg_w = 1;                      // 写入 rd
            ALU_src1 = 0;                   // 使用 Rs1
            ALU_src2 = 0;                   // 使用 Rs2
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd0;                  // 写回 ALU 结果
        end
        
        //---------------------------------------------------------------------
        // I 型 ALU 指令: ADDI, ANDI, ORI, XORI, SLTI, SLTIU, SLLI, SRLI, SRAI
        // 格式: op rd, rs1, imm
        //---------------------------------------------------------------------
        `I_TYPE_ALU : begin
            Imm_Type = `I_TYPE_IMM;         // I 型立即数
            ALU_op = `ALU_OP_I_TYPE;        // 根据 funct3 决定操作
            Reg_w = 1;                      // 写入 rd
            ALU_src1 = 0;                   // 使用 Rs1
            ALU_src2 = 1;                   // 使用立即数
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd0;                  // 写回 ALU 结果
        end
        
        //---------------------------------------------------------------------
        // Load 指令: LB, LH, LW, LBU, LHU
        // 格式: op rd, offset(rs1)
        // 功能: rd = Mem[rs1 + offset]
        //---------------------------------------------------------------------
        `I_TYPE_LOAD : begin
            Imm_Type = `I_TYPE_IMM;         // I 型立即数
            ALU_op = `ALU_OP_ADD;           // ALU 做加法计算地址
            Reg_w = 1;                      // 写入 rd
            ALU_src1 = 0;                   // 使用 Rs1 (基址)
            ALU_src2 = 1;                   // 使用立即数 (偏移)
            Mem_w = 0;
            Mem_r = 1;                      // 读内存
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd2;                  // 写回内存数据
        end
        
        //---------------------------------------------------------------------
        // JALR 指令: 间接跳转
        // 格式: jalr rd, offset(rs1)
        // 功能: rd = PC+4; PC = (rs1 + offset) & ~1
        //---------------------------------------------------------------------
        `I_TYPE_JALR : begin
            Imm_Type = `I_TYPE_IMM;
            ALU_op = `ALU_OP_ADD;           // 计算跳转目标
            Reg_w = 1;                      // 保存返回地址到 rd
            ALU_src1 = 0;                   // 使用 Rs1
            ALU_src2 = 1;                   // 使用立即数
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 1;                       // 跳转指令
            CSR_en = 0;
            WB_sel = 2'd1;                  // 写回 PC+4 (返回地址)
        end
        
        //---------------------------------------------------------------------
        // CSR 指令: CSRRW, CSRRS, CSRRC, CSRRWI, CSRRSI, CSRRCI
        // 格式: op rd, csr, rs1/uimm
        //---------------------------------------------------------------------
        `I_TYPE_CSR : begin
            Imm_Type = `I_TYPE_IMM;         // CSR 地址在立即数位置
            ALU_op = `ALU_OP_ADD;
            Reg_w = 1;                      // 读取的 CSR 值写入 rd
            ALU_src1 = 0;
            ALU_src2 = 0;
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 1;                     // 使能 CSR 操作
            WB_sel = 2'd0;                  // 写回 CSR 读取值 (通过 EX_ALU_Result)
        end
        
        //---------------------------------------------------------------------
        // S 型 Store 指令: SB, SH, SW
        // 格式: op rs2, offset(rs1)
        // 功能: Mem[rs1 + offset] = rs2
        //---------------------------------------------------------------------
        `S_TYPE : begin
            Imm_Type = `S_TYPE_IMM;         // S 型立即数
            ALU_op = `ALU_OP_ADD;           // 计算内存地址
            Reg_w = 0;                      // 不写寄存器
            ALU_src1 = 0;                   // 使用 Rs1 (基址)
            ALU_src2 = 1;                   // 使用立即数 (偏移)
            Mem_w = 1;                      // 写内存
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd0;
        end
        
        //---------------------------------------------------------------------
        // B 型分支指令: BEQ, BNE, BLT, BGE, BLTU, BGEU
        // 格式: op rs1, rs2, offset
        // 功能: if(condition) PC = PC + offset
        //---------------------------------------------------------------------
        `B_TYPE : begin
            Imm_Type = `B_TYPE_IMM;         // B 型立即数
            ALU_op = `ALU_OP_BRANCH;        // 分支比较操作
            Reg_w = 0;                      // 不写寄存器
            ALU_src1 = 0;                   // 使用 Rs1
            ALU_src2 = 0;                   // 使用 Rs2 (比较)
            Mem_w = 0;
            Mem_r = 0;
            Branch = 1;                     // 分支指令
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd0;
        end
        
        //---------------------------------------------------------------------
        // LUI 指令: 加载高位立即数
        // 格式: lui rd, imm
        // 功能: rd = imm << 12
        //---------------------------------------------------------------------
        `U_TYPE_LUI : begin
            Imm_Type = `U_TYPE_IMM;         // U 型立即数 (高 20 位)
            ALU_op = `ALU_OP_ADD;
            Reg_w = 1;
            ALU_src1 = 0;
            ALU_src2 = 0;
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd3;                  // 直接写回立即数
        end 
        
        //---------------------------------------------------------------------
        // AUIPC 指令: PC 加高位立即数
        // 格式: auipc rd, imm
        // 功能: rd = PC + (imm << 12)
        //---------------------------------------------------------------------
        `U_TYPE_AUIPC : begin
            Imm_Type = `U_TYPE_IMM;
            ALU_op = `ALU_OP_ADD;           // PC + Imm
            Reg_w = 1;
            ALU_src1 = 1;                   // 使用 PC (实际是 PC+4)
            ALU_src2 = 1;                   // 使用立即数
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd0;                  // 写回 ALU 结果
        end
        
        //---------------------------------------------------------------------
        // JAL 指令: 直接跳转
        // 格式: jal rd, offset
        // 功能: rd = PC+4; PC = PC + offset
        //---------------------------------------------------------------------
        `J_TYPE_JAL : begin
            Imm_Type = `J_TYPE_IMM;         // J 型立即数
            ALU_op = `ALU_OP_ADD;
            Reg_w = 1;                      // 保存返回地址
            ALU_src1 = 1;                   // 使用 PC
            ALU_src2 = 1;                   // 使用立即数
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 1;                       // 跳转指令
            CSR_en = 0;
            WB_sel = 2'd1;                  // 写回 PC+4
        end
        
        //---------------------------------------------------------------------
        // 默认: 所有控制信号置零 (相当于 NOP)
        //---------------------------------------------------------------------
        default: begin
            Imm_Type = 0;
            ALU_op = 0;
            Reg_w = 0;
            ALU_src1 = 0;
            ALU_src2 = 0;
            Mem_w = 0;
            Mem_r = 0;
            Branch = 0;
            Jump = 0;
            CSR_en = 0;
            WB_sel = 2'd0;
        end
        endcase
    end
endmodule
