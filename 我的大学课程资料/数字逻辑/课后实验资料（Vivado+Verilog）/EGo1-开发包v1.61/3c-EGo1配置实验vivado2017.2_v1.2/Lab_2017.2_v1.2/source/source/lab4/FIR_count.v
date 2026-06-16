`timescale 1ns / 1ps
module FIR_count(
		input clk,
		input rst,  
		output reg [8:0]address
		);
		always @(negedge clk)
			if(rst)
			begin
				address<=9'd0;
			end
			else
			begin
				if(address==9'd400)
					address<=9'd0;
				else
					address<=address+9'd1; 
			end
endmodule
