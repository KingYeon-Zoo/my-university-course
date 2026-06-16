`timescale 1ns / 1ps
module FIR_top(
		input clk,
		input rst,
		output [7:0]fir_out//ÂË²¨Æ÷Êä³ö
		);
		wire [7:0]spo;
		wire [8:0]address;
		dist_mem_gen_0 your_instance_name (
			.a(address),
			.spo(spo)
		);
		FIR_count count(
			.clk(clk),
			.rst(rst),
			.address(address)
		);
		FIR_filter filter(
			.clk(clk),
			.rst(rst),
			.fir_in(spo),
			.fir_out(fir_out)
		);
endmodule
