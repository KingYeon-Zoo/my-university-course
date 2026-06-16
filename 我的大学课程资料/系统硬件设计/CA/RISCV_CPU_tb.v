/******************************************************************************
* 文件名:     RISCV_CPU_tb.v
* 描述:       RISC-V CPU 测试平台 (Testbench)
*             用于仿真验证 CPU 功能
*
* 功能:
*   1. 生成时钟和复位信号
*   2. 从文件加载指令和数据到存储器
*   3. 运行仿真一段时间后输出结果
*   4. 将寄存器堆和数据存储器内容写入文件
*
* 文件说明:
*   输入文件:
*     - IM.dat  : 指令存储器初始化文件 (十六进制)
*     - DM.dat  : 数据存储器初始化文件 (十六进制)
*   
*   输出文件:
*     - RF.out  : 仿真结束后的寄存器堆内容
*     - DM.out  : 仿真结束后的数据存储器内容
*
* 使用方法:
*   1. 准备测试指令文件 (使用 rv32i_transfer.py 转换汇编)
*   2. 将 IM.dat 和 DM.dat 放到 testbench 目录
*   3. 运行仿真
*   4. 查看 RF.out 和 DM.out 验证结果
******************************************************************************/

`include "SYSTEM_DEF.vh"

module RISCV_CPU_tb ();
    
    //=========================================================================
    // 测试信号
    //=========================================================================
    reg clk;                                // 时钟信号
    reg rst_n;                              // 复位信号

    // 临时存储器 (用于从文件加载数据)
    reg [7:0] InstrMem [0:`INSTR_MEM_SIZE - 1];  // 指令数据临时存储
    reg [7:0] DataMem [0:`DATA_MEM_SIZE - 1];    // 数据临时存储
    
    integer i;                              // 循环变量
    integer register_file, dm_file;         // 输出文件句柄
    
    //=========================================================================
    // 被测模块实例化
    //=========================================================================
    RISCV_CPU test(clk, rst_n);

    //=========================================================================
    // 时钟和复位生成
    //=========================================================================
    initial begin
        // 初始化
        clk = 0;
        rst_n = 1;
        
        // 复位序列: 等待 3ns 后拉低复位，持续 10ns 后释放
        #3 rst_n = 0;                       // 拉低复位
        #10 rst_n = 1;                      // 释放复位
        
        // 仿真8000ns (800个时钟周期)
        // 足够执行完所有指令(~250周期)并观察最终状态
        #8000 begin
            //=================================================================
            // 输出寄存器堆内容到文件
            //=================================================================
            register_file = $fopen("D:/Users/Desktop/CA/testbench/RF.out", "w");
            if (register_file) begin
                $fdisplay(register_file, "// Register File Contents with Index");
                $fdisplay(register_file, "// Format: [Index] Data");
                // 输出 32 个寄存器的值
                for (i = 0; i < `GPR_SIZE; i = i + 1) begin
                    $fdisplay(register_file, "[%0d] %h", i, test.Register_File.GPR[i]);
                end
                $fclose(register_file);
                $display("Register File written to RF.out");
            end
            else $display("Failed to open RF.out");

            //=================================================================
            // 输出数据存储器内容到文件
            //=================================================================
            dm_file = $fopen("D:/Users/Desktop/CA/testbench/DM.out", "w");
            if (dm_file) begin
                $fdisplay(dm_file, "// Data Memory Contents with Address");
                $fdisplay(dm_file, "// Format: [Address] Data");
                // 输出所有数据存储器单元
                for (i = 0; i < `DATA_MEM_SIZE; i = i + 1) begin
                    $fdisplay(dm_file, "[%0d] %h", i, test.Data_Memory.DataMem[i]);
                end
                $fclose(dm_file);
                $display("Data Memory written to DM.out");
            end
            else $display("Failed to open DM.out");
        end
        
        #10 $finish;                        // 结束仿真
    end

    //=========================================================================
    // 时钟生成: 周期 10ns (频率 100MHz)
    //=========================================================================
    always #5 clk <= ~clk;

    //=========================================================================
    // 预处理: 从文件加载指令和数据
    //=========================================================================
    initial begin : Preprocess
        // 从文件读取指令存储器内容
        $readmemh("D:/Users/Desktop/CA/testbench/IM.dat", InstrMem);
        // 从文件读取数据存储器内容
        $readmemh("D:/Users/Desktop/CA/testbench/DM.dat", DataMem);
        
        // 将数据复制到 CPU 内部的存储器
        for (i = 0; i < `INSTR_MEM_SIZE; i = i + 1) begin
            test.Instruction_Memory.InstrMem[i] = InstrMem[i];
        end

        for (i = 0; i < `DATA_MEM_SIZE; i = i + 1) begin
            test.Data_Memory.DataMem[i] = DataMem[i];
        end
        
        $display("Initialize the Instr_Mem & Data_Mem");
    end
endmodule
