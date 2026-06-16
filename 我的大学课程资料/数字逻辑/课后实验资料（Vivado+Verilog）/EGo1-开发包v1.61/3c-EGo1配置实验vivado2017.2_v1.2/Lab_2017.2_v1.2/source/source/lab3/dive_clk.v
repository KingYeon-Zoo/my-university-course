`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2016/08/29 22:26:19
// Design Name: 
// Module Name: dive_clk
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


module dive_clk(
	    input clk,
	    input rst,
	    input en_even,
	    input [14:0]N,	
	    output reg clk_e
	    ); 
	    integer cnt; 
	    always @(posedge clk or posedge rst)	//clk上升沿、rst上升沿触发 
	        if (rst)					//rst为1复位
	        begin
	            cnt <= 0;			//设置计数器cnt复位值为0
	            clk_e <= 1'b0;		//设置偶数倍分频输出信号clk_e初值为0
	        end
	        else
	        begin
	            if (en_even)			//en_even使能信号为高，执行偶分频
	            begin 
	                if (cnt == 0) 		//cnt为0时，clk_e翻转，计数器取N/2-1
	                    begin 
	                        clk_e  <= ~clk_e;
	                        cnt    <= N/2-1; 
	                    end 
	                else				//cnt非0时，clk_e保持，计数器减一
	                    begin
	                        clk_e  <= clk_e; 
	                        cnt    <= cnt - 1'b1; 
	                    end
	            end
	            else					// en_even使能为低，输出信号始终为0。
	                begin 
	                clk_e  <= 1'b0;
	                cnt    <= 0;
	            end
	        end 
endmodule

