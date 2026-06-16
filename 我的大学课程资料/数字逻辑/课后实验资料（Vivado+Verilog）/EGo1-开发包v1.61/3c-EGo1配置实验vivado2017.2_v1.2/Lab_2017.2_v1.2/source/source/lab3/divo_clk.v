`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2016/08/29 22:28:05
// Design Name: 
// Module Name: divo_clk
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


	module divo_clk(
	    input  clk,
	    input rst,
	    input en_odd,
	    input  [14:0]N,
	    output reg clka,clkb,
	    output wire clk_o
	    );
	    integer cnt1;
	    integer cnt2;
	    assign clk_o = clka | clkb;				//clka与clkb错位相“或”
	    always @(posedge clk or posedge rst)    //clk上升沿和rst上升沿触发 
	    begin
	        if (rst)					//rst为1复位
	        begin
	            clka <= 1'b0; 			//设置clk上升沿触发输出信号clka初值为0 
	            cnt1 <= 0;      		//设置计数器cnt1复位值为0
	        end
	        else
	        begin
	            if (en_odd)			//en_odd使能信号为高，执行奇分频
	            begin
	                if (cnt1 == 0)     //cnt1为0时，clka取0，cnt1取N-1
	                begin
	                    clka <= 1'b0; 
	                    cnt1 <= N-1; 
	                end
	                else if (cnt1 > (N-1)/2 )     //cnt大于(N-1)/2时
	                    begin               //clka取1，cnt1自减一
	                        clka <= 1'b1;
	                        cnt1 <=cnt1-1;
	                    end 
	                    else					//cnt小于或等于(N-1)/2
	                    begin				//clka取0，cnt1自减一
	                        clka <= 1'b0;
	                        cnt1 <=cnt1-1;
	                    end 
	            end 
	            else						// en_odd使能为低，clka信号始终为0
	            begin
	                clka <= 1'b0;
	                cnt1 <= N-1;
	            end
	        end 
	    end 
	    ////////////////////////////////////////////////////////////////////////////////////////////
	    always @(negedge clk or posedge rst)	//clk下降沿，rst上升沿触发
	    begin
	        if (rst)
	        begin
	            clkb <= 1'b0; 
	            cnt2 <= 0;
	        end
	        else
	        begin
	            if (en_odd)
	            begin
	                if (cnt2 == 0)
	                begin
	                    clkb <= 1'b0;
	                    cnt2 <=N-1; 
	                end
	                else if (cnt2 > (N-1)/2 ) 
	                    begin
	                        clkb <= 1'b1;
	                        cnt2<=cnt2-1;
	                    end 
	                    else
	                    begin
	                        clkb <= 1'b0;
	                        cnt2<=cnt2-1;
	                    end
	            end
	            else
	            begin
	                clkb <= 1'b0;
	                cnt2 <= N-1;
	            end
	        end
	    end
endmodule

