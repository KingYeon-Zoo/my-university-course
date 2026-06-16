`timescale 1ns / 1ps
module sim_div;
	    reg clk,rst;
	    reg[14:0]N;
	    div_clk div_clk(.clk(clk),.rst_n(rst),.N(N),.clk_out(clk_out));
	    always #5 clk = ~clk;
	    initial begin
	        rst=1;
	        clk = 1;
	        N=15'd7;
	        #5 rst = 1'b0;
	        #5 rst = 1'b1;
	        #385 rst = 1'b0;
	        N = 15'd8;
	        #5 rst =1'b1;
	        #600 $finish;
	    end
endmodule
