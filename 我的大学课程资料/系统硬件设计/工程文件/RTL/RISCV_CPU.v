/******************************************************************************
* 文件名:     RISCV_CPU.v
* 项目:       五级流水线 RISC-V CPU 设计
* 描述:       CPU 顶层模块，实现五级流水线架构
*             支持 RV32I 指令集，包含数据前递、冒险检测和动态分支预测
*
* 流水线阶段:
*   IF  (取指)   -> ID  (译码)   -> EX  (执行)   -> MEM (访存)  -> WB  (写回)
*   PC, I_Mem      Control, RF     ALU, BPU        D_Mem, LDU     WB MUX
*                  ImmGen          Forwarding
*
* 特性:
*   - 数据前递 (Forwarding): 解决数据冒险，减少流水线停顿
*   - 冒险检测 (Hazard Detection): 处理 Load-Use 冒险
*   - 动态分支预测: 使用 2-bit 饱和计数器 (BHT) + 分支目标缓冲 (BTB)
*
* 修改记录:
*   2025-12-27: 添加FPGA调试接口，支持上板验证
******************************************************************************/

`include "SYSTEM_DEF.vh"

module RISCV_CPU(
    input aclk,                     // 系统时钟
    input aresetn                   // 异步复位信号 (低电平有效)
    
`ifdef FPGA_BOARD
    // FPGA调试接口 (仅在上板模式下启用)
    ,output [`PC_WIDTH - 1:0] Debug_PC,         // 当前PC值
    input [`ADDR_WIDTH - 1:0] Debug_Reg_Addr1,  // 调试读寄存器地址1
    input [`ADDR_WIDTH - 1:0] Debug_Reg_Addr2,  // 调试读寄存器地址2
    output [`DATA_WIDTH - 1:0] Debug_Reg_Data1, // 调试读寄存器数据1
    output [`DATA_WIDTH - 1:0] Debug_Reg_Data2  // 调试读寄存器数据2
`endif
    );

    //=========================================================================
    // IF 阶段 (取指) 信号声明
    //=========================================================================
    wire [`PC_WIDTH - 1:0] IF_PC;           // 当前 PC 值
    wire [`PC_WIDTH - 1:0] PC_Plus_4;       // PC + 4 (下一条顺序指令地址)
    wire [`PC_WIDTH - 1:0] ID_PC,EX_PC,PC_Plus_Imm;  // 各阶段的 PC 值
    wire IF_ID_w;                           // IF/ID 寄存器写使能 (用于停顿控制)
    wire [`INSTR_WIDTH - 1:0] IF_Instr;     // 从指令存储器取出的指令
    wire [`INSTR_WIDTH - 1:0] ID_Instr;     // 传递到 ID 阶段的指令

    //=========================================================================
    // ID 阶段 (译码) 信号声明
    //=========================================================================
    // 寄存器数据
    wire [`DATA_WIDTH - 1:0] ID_Rs1_Data,EX_Rs1_Data;  // Rs1 寄存器数据
    wire [`DATA_WIDTH - 1:0] ID_Rs2_Data,EX_Rs2_Data;  // Rs2 寄存器数据
    
    // 寄存器地址 (5位，可寻址 x0-x31)
    wire [`ADDR_WIDTH - 1:0] ID_Rs1_Addr,EX_Rs1_Addr;  // Rs1 地址
    wire [`ADDR_WIDTH - 1:0] ID_Rs2_Addr,EX_Rs2_Addr;  // Rs2 地址
    wire [`ADDR_WIDTH - 1:0] ID_Rd_Addr,EX_Rd_Addr,MEM_Rd_Addr,WB_Rd_Addr;  // Rd 目标寄存器地址
    
    // 指令字段
    wire [6:0] ID_Funct7,EX_Funct7;          // funct7 字段 (指令[31:25])
    wire [2:0] ID_Funct3,EX_Funct3,MEM_Funct3;  // funct3 字段 (指令[14:12])

    //=========================================================================
    // 控制信号声明
    //=========================================================================
    wire Branch_Taken;                      // 分支是否跳转 (由 BPU 计算)
    wire [2:0] Imm_Type;                    // 立即数类型 (I/S/B/U/J)
    wire [1:0] ID_ALU_op,EX_ALU_op;          // ALU 操作类型
    wire [1:0] ID_WB_sel,EX_WB_sel,MEM_WB_sel,WB_WB_sel;  // 写回数据选择
    // WB_sel: 00=ALU结果, 01=PC+4, 10=内存数据, 11=立即数
    
    wire ID_Reg_w,EX_Reg_w,WB_Reg_w;        // 寄存器写使能
    wire ID_ALU_src1,EX_ALU_src1;           // ALU 源操作数1选择 (0=Rs1, 1=PC)
    wire ID_ALU_src2,EX_ALU_src2;           // ALU 源操作数2选择 (0=Rs2, 1=Imm)
    wire ID_Mem_w,EX_Mem_w,MEM_Mem_w;       // 内存写使能
    wire ID_Mem_r,EX_Mem_r,MEM_Mem_r;       // 内存读使能
    wire ID_Branch,EX_Branch;               // 分支指令标志
    wire ID_Jump,EX_Jump;                   // 跳转指令标志 (JAL/JALR)
    wire [1:0] PC_sel;                      // PC 来源选择
    // PC_sel: 0=PC+4, 1=BTB预测地址, 2=EX_PC+4(预测错误恢复), 3=ALU结果(跳转目标)
    
    //=========================================================================
    // 流水线冲刷信号
    //=========================================================================
    wire IF_ID_Flush;                       // 冲刷 IF/ID 寄存器
    wire ID_EX_Flush,ID_EX_Flush_0,ID_EX_Flush_1;  // 冲刷 ID/EX 寄存器
    // ID_EX_Flush_0: 来自 Hazard_Unit (Load-Use 冒险)
    // ID_EX_Flush_1: 来自 Control (分支/跳转)

    //=========================================================================
    // 立即数和数据通路信号
    //=========================================================================
    wire [`DATA_WIDTH - 1:0] ID_Imm,EX_Imm,MEM_Imm,WB_Imm;  // 立即数
    wire [`OPCODE_WIDTH - 1:0] Opcode;      // 操作码 (指令[6:0])

    //=========================================================================
    // EX 阶段 (执行) 信号声明
    //=========================================================================
    wire [`DATA_WIDTH - 1:0] Src1_Data,Src2_Data;  // 前递后的源操作数
    wire [`DATA_WIDTH - 1:0] Src1,Src2;            // ALU 实际输入
    wire [`DATA_WIDTH - 1:0] ALU_Result,EX_ALU_Result,MEM_ALU_Result,WB_ALU_Result;
    wire [4:0] ALU_Ctrl_op;                 // ALU 控制信号 (扩展到5位支持M扩展)
    wire Zero_Flag;                         // 零标志 (ALU 结果为 0)

    //=========================================================================
    // MEM 阶段 (访存) 信号声明
    //=========================================================================
    wire [`DATA_WIDTH - 1:0] EX_PC_Plus_4,MEM_PC_Plus_4,WB_PC_Plus_4;
    wire [`DATA_WIDTH - 1:0] EX_Mem_W_Data,MEM_Mem_W_Data;  // 内存写入数据
    wire [`DATA_WIDTH - 1:0] Mem_R_Data,MEM_Mem_R_Data,WB_Mem_R_Data;  // 内存读取数据
    wire [`DATA_WIDTH - 1:0] WB_Data;       // 写回数据
    wire [1:0] Forward_A,Forward_B;         // 前递控制信号
    wire [3:0] EX_Mem_W_Strb,MEM_Mem_W_Strb;  // 内存写字节使能 (用于 SB/SH/SW)

    //=========================================================================
    // CSR (控制状态寄存器) 信号
    //=========================================================================
    wire ID_CSR_en,EX_CSR_en;               // CSR 使能
    wire [`DATA_WIDTH - 1:0] CSR_R_Data;    // CSR 读取数据

    //=========================================================================
    // 分支预测信号
    //=========================================================================
    wire Predict;                           // BHT 预测结果 (1=预测跳转)
    wire [`PC_WIDTH - 1:0] BTB_PC;          // BTB 中存储的跳转目标地址
    wire BTB_Valid;                         // BTB 命中标志
    wire Predict_Taken,ID_Predict_Taken,EX_Predict_Taken;  // 预测跳转标志
    
    // 只有当 BHT 预测跳转且 BTB 命中时，才认为预测跳转
    assign Predict_Taken = Predict && BTB_Valid;


    //=========================================================================
    // 指令译码 - 从指令中提取各字段
    //=========================================================================
    assign Opcode = ID_Instr[6:0];          // 操作码
    assign ID_Rs1_Addr = ID_Instr[19:15];   // Rs1 地址
    assign ID_Rs2_Addr = ID_Instr[24:20];   // Rs2 地址
    assign ID_Rd_Addr = ID_Instr[11:7];     // Rd 地址
    assign ID_Funct7 = ID_Instr[31:25];     // funct7
    assign ID_Funct3 = ID_Instr[14:12];     // funct3

    // 内存写入数据来自 Rs2 (经过前递)
    assign EX_Mem_W_Data = Src2_Data;

    //=========================================================================
    // PC 来源选择逻辑 (处理分支预测)
    //=========================================================================
    // PC_sel 编码:
    //   0: PC+4         - 顺序执行
    //   1: BTB_PC       - 预测跳转
    //   2: EX_PC+4      - 预测错误，需要回到正确的下一条指令
    //   3: EX_ALU_Result - 实际跳转目标
    assign PC_sel = ((Branch_Taken||EX_Jump)&&~EX_Predict_Taken)? 2'd3 :  // 实际跳转但未预测跳转
                    (EX_Predict_Taken&&~(Branch_Taken||EX_Jump))? 2'd2 :  // 预测跳转但实际不跳转
                    (Predict_Taken)? 2'd1 : 2'd0;                          // 预测跳转 / 顺序执行

    // 计算 PC + 4 (用于 JAL/JALR 保存返回地址)
    assign EX_PC_Plus_4 = EX_PC + 4;

    //=========================================================================
    // ALU 输入多路选择器 (包含前递逻辑)
    //=========================================================================
    // Src1_Data: 根据前递信号选择 Rs1 数据来源
    //   Forward_A = 00: 使用 ID/EX 寄存器中的 Rs1 数据
    //   Forward_A = 01: 从 WB 阶段前递
    //   Forward_A = 10: 从 MEM 阶段前递
    assign Src1_Data = (Forward_A == 2'b00)? EX_Rs1_Data :
                    (Forward_A == 2'b01)? WB_Data : MEM_ALU_Result;

    // Src1: ALU 第一个操作数
    //   ALU_src1 = 0: 使用 Rs1 数据
    //   ALU_src1 = 1: 使用 PC+4 (用于 AUIPC)
    assign Src1 = (EX_ALU_src1)? EX_PC_Plus_4 : Src1_Data;

    // Src2_Data: 根据前递信号选择 Rs2 数据来源
    assign Src2_Data = (Forward_B == 2'b00)? EX_Rs2_Data :
                    (Forward_B == 2'b01)? WB_Data : MEM_ALU_Result;

    // Src2: ALU 第二个操作数
    //   ALU_src2 = 0: 使用 Rs2 数据
    //   ALU_src2 = 1: 使用立即数
    assign Src2 = (EX_ALU_src2)? EX_Imm : Src2_Data;

    // EX_ALU_Result: 根据指令类型选择结果
    //   分支指令: PC + Imm (跳转目标)
    //   CSR 指令: CSR 读取值
    //   其他: ALU 运算结果
    assign EX_ALU_Result = (EX_Branch)? PC_Plus_Imm : 
                        (EX_CSR_en)? CSR_R_Data : ALU_Result;

    //=========================================================================
    // 写回数据多路选择器
    //=========================================================================
    // WB_sel 编码:
    //   00: ALU 结果
    //   01: PC + 4 (JAL/JALR 返回地址)
    //   10: 内存读取数据 (Load 指令)
    //   11: 立即数 (LUI 指令)
    assign WB_Data = (WB_WB_sel == 2'b00)? WB_ALU_Result : 
                    (WB_WB_sel == 2'b01)? WB_PC_Plus_4 : 
                    (WB_WB_sel == 2'b10)? WB_Mem_R_Data : WB_Imm;

    // ID/EX 冲刷信号 = Load-Use 冒险冲刷 OR 分支/跳转冲刷
    assign ID_EX_Flush = ID_EX_Flush_1 || ID_EX_Flush_0;

`ifdef FPGA_BOARD
    //=========================================================================
    // FPGA调试接口输出
    //=========================================================================
    assign Debug_PC = IF_PC;            // 输出当前PC值用于调试
`endif

    //=========================================================================
    // 模块实例化 - IF 阶段
    //=========================================================================
    
    // 程序计数器
    PC Program_Counter (
        .clk(aclk),
        .rst_n(aresetn),
        .PC_sel(PC_sel),              // PC 来源选择
        .EX_ALU_Result(EX_ALU_Result), // 跳转目标地址
        .PC_Plus_4(PC_Plus_4),        // 顺序下一条地址
        .BTB_PC(BTB_PC),              // 预测跳转地址
        .EX_PC_Plus_4(EX_PC_Plus_4),  // 预测错误恢复地址
        .IF_PC(IF_PC));               // 输出: 当前 PC

    // PC + 4 加法器
    PC_Adder PC_Adder_inst (
        .IF_ID_w(IF_ID_w),            // 写使能 (停顿时保持 PC)
        .PC_In(IF_PC),
        .PC_Out(PC_Plus_4));

    // 分支历史表 (2-bit 饱和计数器预测)
    BHT Branch_History_Table (
        .clk(aclk),
        .rst_n(aresetn),
        .PC_Tag(IF_PC[`BHT_PC_WIDTH - 1:0]),  // 用 PC 低位索引
        .Branch_Taken(Branch_Taken),           // 实际分支结果 (用于更新)
        .EX_PC_Tag(EX_PC[`BHT_PC_WIDTH - 1:0]),
        .Predict(Predict));                    // 预测结果

    // 分支目标缓冲 (缓存跳转目标地址)
    BTB Branch_Tag_Buffer (
        .clk(aclk),
        .rst_n(aresetn),
        .PC_Tag(IF_PC[`BHT_PC_WIDTH - 1:0]),
        .BTB_PC(BTB_PC),              // 预测的跳转地址
        .BTB_Valid(BTB_Valid),        // BTB 命中
        .EX_PC_Tag(EX_PC[`BHT_PC_WIDTH - 1:0]),
        .Branch_PC(EX_ALU_Result),    // 实际跳转地址 (用于更新)
        .Branch_Taken(Branch_Taken));

    // 指令存储器
    I_Mem Instruction_Memory (
        .Instr_Addr(IF_PC),
        .Instr(IF_Instr));
    
    // IF/ID 流水线寄存器
    IF_ID IF_ID_inst (
        .clk(aclk),
        .rst_n(aresetn),
        .IF_ID_w(IF_ID_w),            // 写使能 (停顿控制)
        .IF_ID_Flush(IF_ID_Flush),    // 冲刷信号
        .IF_PC(IF_PC),
        .IF_Instr(IF_Instr),
        .IF_Predict_Taken(Predict_Taken),
        .ID_PC(ID_PC),
        .ID_Predict_Taken(ID_Predict_Taken),
        .ID_Instr(ID_Instr));

    //=========================================================================
    // 模块实例化 - ID 阶段
    //=========================================================================
    
    // 寄存器堆 (32 个通用寄存器)
    RF Register_File(
        .clk(aclk),
        .rst_n(aresetn),
        .Reg_w(WB_Reg_w),             // 写使能
        .Rs1_Addr(ID_Rs1_Addr),       // 读端口 1 地址
        .Rs2_Addr(ID_Rs2_Addr),       // 读端口 2 地址
        .Rd_Addr(WB_Rd_Addr),         // 写端口地址
        .Rd_Data(WB_Data),            // 写入数据
        .Rs1_Data(ID_Rs1_Data),       // 读端口 1 数据
        .Rs2_Data(ID_Rs2_Data)        // 读端口 2 数据
`ifdef FPGA_BOARD
        ,.Debug_Addr1(Debug_Reg_Addr1),  // 调试读端口 1 地址
        .Debug_Addr2(Debug_Reg_Addr2),   // 调试读端口 2 地址
        .Debug_Data1(Debug_Reg_Data1),   // 调试读端口 1 数据
        .Debug_Data2(Debug_Reg_Data2)    // 调试读端口 2 数据
`endif
        );

    // 控制单元 (生成所有控制信号)
    Control Control_Unit(
        .Opcode(Opcode),
        .Branch_Taken(Branch_Taken),
        .ID_EX_Jump(EX_Jump),
        .EX_Predict_Taken(EX_Predict_Taken),
        .ID_PC(ID_PC),
        .Branch_PC(EX_ALU_Result),
        .Imm_Type(Imm_Type),          // 立即数类型
        .ALU_op(ID_ALU_op),           // ALU 操作类型
        .WB_sel(ID_WB_sel),           // 写回选择
        .Reg_w(ID_Reg_w),             // 寄存器写使能
        .ALU_src1(ID_ALU_src1),       // ALU 源 1 选择
        .ALU_src2(ID_ALU_src2),       // ALU 源 2 选择
        .Mem_w(ID_Mem_w),             // 内存写使能
        .Mem_r(ID_Mem_r),             // 内存读使能
        .Branch(ID_Branch),           // 分支标志
        .Jump(ID_Jump),               // 跳转标志
        .CSR_en(ID_CSR_en),           // CSR 使能
        .IF_ID_Flush(IF_ID_Flush),    // IF/ID 冲刷
        .ID_EX_Flush_1(ID_EX_Flush_1)); // ID/EX 冲刷

    // 立即数生成器
    ImmGen Immediate_Generator(
        .Instr(ID_Instr),
        .Imm_Type(Imm_Type),
        .Imm(ID_Imm));

    // 冒险检测单元 (处理 Load-Use 冒险)
    Hazard_Unit Hazard_Unit_inst(
        .Rs1Addr(ID_Rs1_Addr),
        .Rs2Addr(ID_Rs2_Addr),
        .RdAddr(EX_Rd_Addr),          // EX 阶段的目标寄存器
        .EX_Mem_r(EX_Mem_r),          // EX 阶段是否是 Load 指令
        .IF_ID_w(IF_ID_w),            // 停顿 IF/ID
        .ID_EX_Flush_0(ID_EX_Flush_0)); // 冲刷 ID/EX

    // ID/EX 流水线寄存器
    ID_EX ID_EX_inst(
        .clk(aclk),
        .rst_n(aresetn),
        .ID_EX_Flush(ID_EX_Flush),
        // 控制信号
        .ID_ALU_op(ID_ALU_op),
        .ID_ALU_src1(ID_ALU_src1),
        .ID_ALU_src2(ID_ALU_src2),
        .ID_Branch(ID_Branch),
        .ID_Jump(ID_Jump),
        .ID_Mem_r(ID_Mem_r),
        .ID_Mem_w(ID_Mem_w),
        .ID_Reg_w(ID_Reg_w),
        .ID_WB_sel(ID_WB_sel),
        // 数据
        .ID_PC(ID_PC),
        .ID_Rs1_Data(ID_Rs1_Data),
        .ID_Rs2_Data(ID_Rs2_Data),
        .ID_Imm(ID_Imm),
        .ID_Rs1_Addr(ID_Rs1_Addr),
        .ID_Rs2_Addr(ID_Rs2_Addr),
        .ID_Rd_Addr(ID_Rd_Addr),
        .ID_Funct7(ID_Funct7),
        .ID_Funct3(ID_Funct3),
        .ID_CSR_en(ID_CSR_en),
        .ID_Predict_Taken(ID_Predict_Taken),
        // 输出
        .EX_ALU_op(EX_ALU_op),
        .EX_ALU_src1(EX_ALU_src1),
        .EX_ALU_src2(EX_ALU_src2),
        .EX_Branch(EX_Branch),
        .EX_Jump(EX_Jump),
        .EX_Mem_r(EX_Mem_r),
        .EX_Mem_w(EX_Mem_w),
        .EX_Reg_w(EX_Reg_w),
        .EX_WB_sel(EX_WB_sel),
        .EX_PC(EX_PC),
        .EX_Rs1_Data(EX_Rs1_Data),
        .EX_Rs2_Data(EX_Rs2_Data),
        .EX_Imm(EX_Imm),
        .EX_Rs1_Addr(EX_Rs1_Addr),
        .EX_Rs2_Addr(EX_Rs2_Addr),
        .EX_Rd_Addr(EX_Rd_Addr),
        .EX_Funct7(EX_Funct7),
        .EX_Funct3(EX_Funct3),
        .EX_CSR_en(EX_CSR_en),
        .EX_Predict_Taken(EX_Predict_Taken));

    //=========================================================================
    // 模块实例化 - EX 阶段
    //=========================================================================
    
    // CSR 控制状态寄存器
    CSR Control_State_Register(
        .clk(aclk),
        .rst_n(aresetn),
        .CSR_en(EX_CSR_en),
        .CSR_Addr(EX_Imm[11:0]),      // CSR 地址在立即数低 12 位
        .CSR_W_Data(Src1_Data),       // 写入数据来自 Rs1
        .Funct3(EX_Funct3),           // 决定 CSR 操作类型
        .CSR_R_Data(CSR_R_Data));

    // 算术逻辑单元
    ALU Arithmetic_Logic_Unit(
        .Src1(Src1),
        .Src2(Src2),
        .ALU_Ctrl_op(ALU_Ctrl_op),
        .ALU_Result(ALU_Result),
        .Zero_Flag(Zero_Flag));

    // ALU 控制单元
    ALU_Control ALU_Control_Unit(
        .ALU_op(EX_ALU_op),
        .Funct3(EX_Funct3),
        .Funct7(EX_Funct7),
        .Mem_W_Strb(EX_Mem_W_Strb),   // 内存写字节使能
        .ALU_Ctrl_op(ALU_Ctrl_op));

    // 分支处理单元 (判断分支条件)
    BPU Branch_Processing_Unit(
        .ALU_Result0(ALU_Result[0]),  // ALU 结果最低位
        .Zero_Flag(Zero_Flag),
        .Funct3(EX_Funct3),           // 分支类型
        .EX_Branch(EX_Branch),
        .EX_PC(EX_PC),
        .EX_Imm(EX_Imm),
        .PC_Plus_Imm(PC_Plus_Imm),    // 分支目标地址
        .Branch_Taken(Branch_Taken)); // 分支是否跳转

    // 数据前递单元
    Forwarding_Unit Forwarding_Unit_inst(
        .MEM_Rd_Addr(MEM_Rd_Addr),
        .MEM_Reg_w(MEM_Reg_w),
        .WB_Rd_Addr(WB_Rd_Addr),
        .WB_Reg_w(WB_Reg_w),
        .EX_Rs1_Addr(EX_Rs1_Addr),
        .EX_Rs2_Addr(EX_Rs2_Addr),
        .Forward_A(Forward_A),        // Rs1 前递选择
        .Forward_B(Forward_B));       // Rs2 前递选择

    // EX/MEM 流水线寄存器
    EX_MEM EX_MEM_inst(
        .clk(aclk),
        .rst_n(aresetn),
        .EX_Mem_r(EX_Mem_r),
        .EX_Mem_w(EX_Mem_w),
        .EX_Reg_w(EX_Reg_w),
        .EX_WB_sel(EX_WB_sel),
        .EX_Imm(EX_Imm),
        .EX_PC_Plus_4(EX_PC_Plus_4),
        .EX_ALU_Result(EX_ALU_Result),
        .EX_Mem_W_Data(EX_Mem_W_Data),
        .EX_Rd_Addr(EX_Rd_Addr),
        .EX_Mem_W_Strb(EX_Mem_W_Strb),
        .EX_Funct3(EX_Funct3),
        .MEM_Mem_r(MEM_Mem_r),
        .MEM_Mem_w(MEM_Mem_w),
        .MEM_Reg_w(MEM_Reg_w),
        .MEM_WB_sel(MEM_WB_sel),
        .MEM_Imm(MEM_Imm),
        .MEM_PC_Plus_4(MEM_PC_Plus_4),
        .MEM_ALU_Result(MEM_ALU_Result),
        .MEM_Mem_W_Data(MEM_Mem_W_Data),
        .MEM_Rd_Addr(MEM_Rd_Addr),
        .MEM_Mem_W_Strb(MEM_Mem_W_Strb),
        .MEM_Funct3(MEM_Funct3));

    //=========================================================================
    // 模块实例化 - MEM 阶段
    //=========================================================================
    
    // 数据存储器
    D_Mem Data_Memory(
        .clk(aclk),
        .Mem_r(MEM_Mem_r),
        .Mem_w(MEM_Mem_w),
        .Mem_W_Strb(MEM_Mem_W_Strb),  // 写字节选择
        .Mem_Addr(MEM_ALU_Result),    // 地址 = ALU 计算结果
        .Mem_W_Data(MEM_Mem_W_Data),
        .Mem_R_Data(Mem_R_Data));

    // 加载数据单元 (符号/零扩展)
    LDU Load_Data_Unit(
        .MEM_Funct3(MEM_Funct3),
        .Mem_R_Data(Mem_R_Data),
        .LDU_Result(MEM_Mem_R_Data));

    //=========================================================================
    // 模块实例化 - WB 阶段
    //=========================================================================
    
    // MEM/WB 流水线寄存器
    MEM_WB MEM_WB_inst(
        .clk(aclk),
        .rst_n(aresetn),
        .MEM_Reg_w(MEM_Reg_w),
        .MEM_WB_sel(MEM_WB_sel),
        .MEM_Imm(MEM_Imm),
        .MEM_PC_Plus_4(MEM_PC_Plus_4),
        .MEM_Mem_R_Data(MEM_Mem_R_Data),
        .MEM_ALU_Result(MEM_ALU_Result),
        .MEM_Rd_Addr(MEM_Rd_Addr),
        .WB_Reg_w(WB_Reg_w),
        .WB_WB_sel(WB_WB_sel),
        .WB_Imm(WB_Imm),
        .WB_PC_Plus_4(WB_PC_Plus_4),
        .WB_Mem_R_Data(WB_Mem_R_Data),
        .WB_ALU_Result(WB_ALU_Result),
        .WB_Rd_Addr(WB_Rd_Addr));

endmodule
