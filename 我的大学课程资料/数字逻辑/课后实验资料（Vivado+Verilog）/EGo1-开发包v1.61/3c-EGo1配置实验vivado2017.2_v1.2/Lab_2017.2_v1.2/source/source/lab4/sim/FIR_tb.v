`timescale 1ns / 1ps
module FIR_tb;
		reg clk; 
		reg rst; 
		wire [7:0] fir_out; 
		initial begin
			clk=1'b0; 
			rst=1'b1; 
			#50 rst=1'b0; 
		end
		always #10 clk=~clk; 
		FIR_top fir(.clk(clk),.rst(rst),.fir_out(fir_out));
endmodule
