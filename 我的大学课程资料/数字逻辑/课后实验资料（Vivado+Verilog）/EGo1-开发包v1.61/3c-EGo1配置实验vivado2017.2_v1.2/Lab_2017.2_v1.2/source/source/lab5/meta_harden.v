`timescale 1ns / 1ps
module meta_harden(
    input clk,
    input rst,
    input sig_src,
    output reg sig_dst
    );
    //
    reg sig_meta;
    always @( posedge clk or posedge rst)
        if( rst )
        begin
            sig_dst <= 1'b0;
            sig_meta <= 1'b0;
        end
        else
        begin
            sig_meta <= sig_src;
            sig_dst <= sig_meta;
        end
endmodule
