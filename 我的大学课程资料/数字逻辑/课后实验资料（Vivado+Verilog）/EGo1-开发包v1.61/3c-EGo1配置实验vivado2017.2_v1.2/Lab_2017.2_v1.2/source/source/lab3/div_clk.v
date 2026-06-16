`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2016/08/29 22:22:36
// Design Name: 
// Module Name: div_clk
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module div_clk(
	    input  clk,					//内部100M时钟信号输入
	    input rst_n,					//定义复位信号
	    input  [14:0] N,				//输入15位分频倍数（通过拨码开关）
	    output clk_out					//分频时钟信号输出
	    );
	    wire en_even,en_odd;
	    wire rst;
	    wire clk_e, clka, clkb, clk_o;
	    assign rst     = ~rst_n;
	    assign en_even = ~N[0];			//N[0]取反，定义en_even使能
	    assign en_odd  =  N[0];		//N[0]，定义en_odd使能
	    dive_clk e_clk(				//偶数倍分频器e_clk实例化
	        .clk(clk),
	        .rst(rst),
	        .en_even(en_even),
	        .N(N),
	        .clk_e(clk_e)
	 	);
	    divo_clk o_clk(				//奇数倍分频器o_clk实例化
	        .clk(clk),
	        .rst(rst),
            .en_odd(en_odd),
	        .N(N),
	        .clka(clka),
	        .clkb(clkb),
	        .clk_o(clk_o)
	 	);
	    assign clk_out = clk_e | clk_o;  	//取clk_e与clk_o中当前有效信号为输出
endmodule
