`timescale 1ns / 1ps
module multip(
		input clk,
		input rst,
		input [15:0]in1, 
		input [7:0]in2,
		output reg[22:0]out
		);
		reg [15:0]comp1,truef1;
		reg [7:0]comp2,truef2; 
		reg symbol;//符号位
		reg [21:0]temp; 
		reg [22:0]truef_out; 
		always@ (negedge clk )
			if(rst)//复位使能，寄存器清零
			begin
				comp1<=8'b0;
				comp2<=8'b0;
				truef1<=8'b0;
				truef2<=8'b0;
				symbol<=1'b0;
				temp<=14'b0;
				truef_out<=15'b0;
				out<=31'b0;
			end
			else
			begin
				comp1<=in1;//输入寄存器赋值
				comp2<=in2;   
				truef1<=(comp1[15]==0)?comp1:{comp1[15],~comp1[14:0]+1'b1}; 
				truef2<=(comp2[7]==0)?comp2:{comp2[7],~comp2[6:0]+1'b1};
				symbol<=truef1[15]^truef2[7];//输出数的符号位
				temp<=truef1[14:0]*truef2[6:0];//输入有效数据相乘
				truef_out<={symbol,temp};//输出数的原码
				out<=(truef_out[22]==0)?
				truef_out:{truef_out[22],~truef_out[21:0]+1'b1};
			end
endmodule
