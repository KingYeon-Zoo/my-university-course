`timescale 1ns / 1ps
module FIR_filter(
		input clk,
		input rst,
		input [7:0]fir_in,//滤波器输入
		output [7:0]fir_out//滤波器输出
		);
		//存放输入序列的位移值
		reg signed [7:0]data1,data2,data3,data4,data5,data6,data7,data8;
		//有符号小数乘法的输出
		wire signed [22:0] out1,out2,out3,out4,out5,out6,out7,out8;
		reg signed [23:0]temp_out;    
		//8阶线性FIR滤波器的抽头系数  
		parameter [15:0] cof1 = 16'h023e;
		parameter [15:0] cof2 = 16'h0c46; 
		parameter [15:0] cof3 = 16'h29fe; 
		parameter [15:0] cof4 = 16'h477e; 
		parameter [15:0] cof5 = 16'h477e; 
		parameter [15:0] cof6 = 16'h29fe; 
		parameter [15:0] cof7 = 16'h0c46; 
		parameter [15:0] cof8 = 16'h023e; 
		always@(negedge clk)
			if(rst)
			begin
				data1<=7'd0;
				data2<=7'd0;
				data3<=7'd0;
				data4<=7'd0;
				data5<=7'd0;
				data6<=7'd0;
				data7<=7'd0;
				data8<=7'd0;
			end 
			else
			begin
				data1<=fir_in;           
				data2<=data1;
				data3<=data2;
				data4<=data3;
				data5<=data4;
				data6<=data5;
				data7<=data6;
				data8<=data7;
				temp_out<=out1+out2+out3+out4+out5+out6+out7+out8;
			end
		multip multip1(.clk(clk),.rst(rst),.in1(cof1),.in2(data1),.out(out1));
		multip multip2(.clk(clk),.rst(rst),.in1(cof2),.in2(data2),.out(out2));
		multip multip3(.clk(clk),.rst(rst),.in1(cof3),.in2(data3),.out(out3));
		multip multip4(.clk(clk),.rst(rst),.in1(cof4),.in2(data4),.out(out4));
		multip multip5(.clk(clk),.rst(rst),.in1(cof5),.in2(data5),.out(out5));
		multip multip6(.clk(clk),.rst(rst),.in1(cof6),.in2(data6),.out(out6));
		multip multip7(.clk(clk),.rst(rst),.in1(cof7),.in2(data7),.out(out7));
		multip multip8(.clk(clk),.rst(rst),.in1(cof8),.in2(data8),.out(out8)); 
		assign fir_out=temp_out[23:16];
endmodule
